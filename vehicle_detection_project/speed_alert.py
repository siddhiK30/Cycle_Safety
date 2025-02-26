import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict
import math
import pyttsx3
import threading
import tempfile
import shutil


from moviepy.editor import VideoFileClip, CompositeAudioClip, AudioFileClip

def generate_tts_audio(text, filename):
   
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, filename)
    engine.runAndWait()

class HybridSpeedDetector:
    def __init__(self, video_path):
       
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
            
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.last_alert_time = 0
        self.alert_cooldown = 2.0  # seconds
        self.engine_lock = threading.Lock()
        
       
        self.alerts = []
        
        # Initialize other parameters
        self.focal_length = self.frame_width
        self.camera_height = 1.5
        self.camera_angle = 15
        self.fov = 90
        self.model = YOLO('yolov8n.pt')
        self.ref_car_width = 1.8
        self.ref_car_length = 4.5
        self.ref_car_height = 1.5
        self.frame_area = self.frame_width * self.frame_height
        self.danger_area_ratio = 0.15
        self.warning_area_ratio = 0.08
        self.danger_distance = 10.0
        self.warning_distance = 15.0
        self.min_depth = 1.0
        self.max_depth = 50.0
        self.vehicles = defaultdict(lambda: {
            'positions': [],
            'timestamps': [],
            'areas': [],
            'depths': [],
            'speeds': [],
            'last_seen': 0,
            'depth_confidence': []
        })
        self.conf_threshold = 0.3
        self.vehicle_classes = [2, 3, 5, 7]
        self.next_track_id = 0

    def play_alert(self, message, video_time):
       
        self.alerts.append((video_time, message))

    def estimate_depth_non_linear(self, bbox, prev_depth=None):
       
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        if width <= 0 or height <= 0:
            return self.max_depth, 0.0
        
        apparent_area = width * height
        max_possible_area = self.frame_width * self.frame_height
        area_ratio = apparent_area / max_possible_area
        
        depth_from_width = (self.ref_car_width * self.focal_length) / width
        depth_from_height = (self.ref_car_height * self.focal_length) / height
        
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        pos_x = abs((center_x - self.frame_width / 2) / (self.frame_width / 2))
        pos_y = abs((center_y - self.frame_height / 2) / (self.frame_height / 2))
        
        width_weight = 1.0 - pos_x
        height_weight = 1.0 - pos_y
        
        depth = (depth_from_width * width_weight + depth_from_height * height_weight) / (width_weight + height_weight + 1e-6)
        
        area_confidence = 1.0 - (area_ratio ** 0.5)
        position_confidence = 1.0 - (pos_x * pos_y)
        
        if depth < 5.0 and prev_depth is not None:
            area_change = abs(area_ratio - prev_depth)
            depth = max(self.min_depth, depth * (1 + area_change))
        
        depth = np.clip(depth, self.min_depth, self.max_depth)
        confidence = min(area_confidence, position_confidence)
        
        return depth, confidence

    def calculate_approach_speed(self, areas, timestamps):
    
        if len(areas) < 2 or len(timestamps) < 2:
            return 0.0
        
        area_change = (areas[-1] - areas[-2])
        time_change = timestamps[-1] - timestamps[-2]
        
        if time_change > 0:
            return area_change / time_change
        return 0.0

    def get_hybrid_warning(self, area, depth, approach_speed, depth_confidence, current_position, previous_positions):
       
        area_ratio = area / self.frame_area
        
        area_severity = 0
        depth_severity = 0
        
        if area_ratio >= self.danger_area_ratio:
            area_severity = 2
        elif area_ratio >= self.warning_area_ratio:
            area_severity = 1
        
        if depth <= self.danger_distance:
            depth_severity = 2
        elif depth <= self.warning_distance:
            depth_severity = 1
        
        area_confidence = min(1.0, area_ratio * 5)
        combined_severity = max(area_severity * area_confidence, depth_severity * depth_confidence)
        
        direction = ""
        if len(previous_positions) >= 2:
            current_x = current_position[0]
            prev_x = previous_positions[-1][0]
            x_movement = current_x - prev_x
            movement_threshold = 2.0
            if abs(x_movement) > movement_threshold:
                if x_movement > 0:
                    direction = "from LEFT"
                else:
                    direction = "from RIGHT"
        
        if combined_severity >= 1.5:
            warning_msg = "DANGER: Vehicle Too Close!"
            if direction:
                warning_msg = f"DANGER: Vehicle Too Close {direction}!"
            return warning_msg, (0, 0, 255), 2
        elif combined_severity >= 0.8:
            if approach_speed > 0:
                warning_msg = "Warning: Vehicle Approaching Rapidly!"
                if direction:
                    warning_msg = f"Warning: Vehicle Approaching Rapidly {direction}!"
                return warning_msg, (0, 165, 255), 1
            warning_msg = "Warning: Vehicle Nearby"
            if direction:
                warning_msg = f"Warning: Vehicle Nearby {direction}"
            return warning_msg, (0, 165, 255), 1
        
        return "", (0, 255, 0), 0

    def calculate_velocity_3d(self, positions, timestamps, depths):
        
        if len(positions) < 2 or len(timestamps) < 2:
            return 0.0
            
        velocities = []
        for i in range(1, len(positions)):
            dt = timestamps[i] - timestamps[i - 1]
            if dt <= 0:
                continue
                
            x1 = positions[i - 1][0] - self.frame_width / 2
            x2 = positions[i][0] - self.frame_width / 2
            y1 = positions[i - 1][1] - self.frame_height / 2
            y2 = positions[i][1] - self.frame_height / 2
            
            z1 = depths[i - 1]
            z2 = depths[i]
            
            pos1 = np.array([x1 * z1 / self.focal_length, y1 * z1 / self.focal_length, z1])
            pos2 = np.array([x2 * z2 / self.focal_length, y2 * z2 / self.focal_length, z2])
            
            displacement = np.linalg.norm(pos2 - pos1)
            velocity = displacement / dt
            velocities.append(velocity)
                
        if not velocities:
            return 0.0
        return sum(velocities) / len(velocities)

    def update_tracking(self, detection, current_time):
       
        x1, y1, x2, y2, conf, class_id = detection
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        area = (x2 - x1) * (y2 - y1)
        
        best_match = None
        min_distance = float('inf')
        
        for track_id, data in self.vehicles.items():
            if data['positions'] and (current_time - data['last_seen']) < 1.0:
                last_pos = data['positions'][-1]
                distance = math.sqrt((center_x - last_pos[0])**2 + (center_y - last_pos[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    best_match = track_id
        
        if best_match is None or min_distance > 100:
            track_id = self.next_track_id
            self.next_track_id += 1
        else:
            track_id = best_match
        
        prev_depth = None
        if self.vehicles[track_id]['depths']:
            prev_depth = self.vehicles[track_id]['depths'][-1]
        
        depth, depth_confidence = self.estimate_depth_non_linear((x1, y1, x2, y2), prev_depth)
        
        self.vehicles[track_id]['positions'].append((center_x, center_y))
        self.vehicles[track_id]['timestamps'].append(current_time)
        self.vehicles[track_id]['areas'].append(area)
        self.vehicles[track_id]['depths'].append(depth)
        self.vehicles[track_id]['depth_confidence'].append(depth_confidence)
        self.vehicles[track_id]['last_seen'] = current_time
        
        velocity = self.calculate_velocity_3d(
            self.vehicles[track_id]['positions'][-5:],
            self.vehicles[track_id]['timestamps'][-5:],
            self.vehicles[track_id]['depths'][-5:]
        )
        
        approach_speed = self.calculate_approach_speed(
            self.vehicles[track_id]['areas'],
            self.vehicles[track_id]['timestamps']
        )
        
        max_history = 10
        for key in ['positions', 'timestamps', 'areas', 'depths', 'depth_confidence']:
            if len(self.vehicles[track_id][key]) > max_history:
                self.vehicles[track_id][key] = self.vehicles[track_id][key][-max_history:]
        
        return track_id, area, depth, approach_speed, depth_confidence, velocity

    def process_frame(self, frame, video_time):
       
        results = self.model(frame, verbose=False)[0]
        
        danger_detected = False
        
        for detection in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, class_id = detection
            
            if conf < self.conf_threshold or int(class_id) not in self.vehicle_classes:
                continue
            
            current_position = ((x1 + x2) / 2, (y1 + y2) / 2)
            
            track_id, area, depth, approach_speed, depth_confidence, velocity = self.update_tracking(detection, time.time())
            previous_positions = self.vehicles[track_id]['positions'][:-1]
            
            warning_msg, color, severity = self.get_hybrid_warning(
                area, depth, approach_speed, depth_confidence,
                current_position, previous_positions
            )
            
            if color == (0, 0, 255):
                danger_detected = True
                if "from LEFT" in warning_msg:
                    self.play_alert("Watch out! Vehicle approaching from left!", video_time)
                elif "from RIGHT" in warning_msg:
                    self.play_alert("Watch out! Vehicle approaching from right!", video_time)
                else:
                    self.play_alert("Watch out!", video_time)
            
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            y_offset = 65
            if warning_msg:
                cv2.putText(frame, warning_msg, (int(x1), int(y1) - y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                y_offset -= 20
            
            speed_text = f"Speed: {velocity * 3.6:.1f} km/h"
            cv2.putText(frame, speed_text, (int(x1), int(y1) - y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset -= 20
            
            cv2.putText(frame, f"Distance: {depth:.1f}m", (int(x1), int(y1) - y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            y_offset -= 20
            
            area_percentage = (area / self.frame_area) * 100
            cv2.putText(frame, f"Area: {area_percentage:.1f}%", (int(x1), int(y1) - y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if danger_detected:
            text = "CAREFUL!!"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_TRIPLEX, 2, 3)[0]
            text_x = (frame.shape[1] - text_size[0]) // 2
            
            cv2.rectangle(frame, 
                          (text_x - 10, 10), 
                          (text_x + text_size[0] + 10, 10 + text_size[1] + 10),
                          (0, 0, 0),
                          -1)
            
            cv2.putText(frame,
                        text,
                        (text_x, 10 + text_size[1]),
                        cv2.FONT_HERSHEY_TRIPLEX,
                        2,
                        (0, 0, 255),
                        3)
        
        return frame

    def run(self):
        """
        Main processing loop with video writing and subsequent audio overlay.
        """
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            'output.mp4',
            fourcc,
            self.fps,
            (self.frame_width, self.frame_height)
        )
        
        print("Processing video...")
        frame_count = 0
        
        # Process frames and record alerts along with their video timestamps (in seconds)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            video_time = frame_count / self.fps  # Video time in seconds
            processed_frame = self.process_frame(frame, video_time)
            out.write(processed_frame)
            
            frame_count += 1
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames")
        
        print("Processing complete. Saving video...")
        self.cap.release()
        out.release()
        print("Video saved as 'output.mp4'")
        
       
        alert_group_threshold = 1.0  # seconds
        grouped_alerts = []
        if self.alerts:
            # Sort alerts by their video time
            sorted_alerts = sorted(self.alerts, key=lambda x: x[0])
            current_group = [sorted_alerts[0]]
            for alert in sorted_alerts[1:]:
                if alert[0] - current_group[-1][0] <= alert_group_threshold:
                    current_group.append(alert)
                else:
                    grouped_alerts.append(current_group)
                    current_group = [alert]
            grouped_alerts.append(current_group)
        
        # Create a temporary directory for audio files
        temp_dir = tempfile.mkdtemp()
        audio_clips = []
        video_clip = VideoFileClip("output.mp4")
        duration = video_clip.duration
        
        for i, group in enumerate(grouped_alerts):
           
            combined_message = " | ".join(msg for _, msg in group)
           
            start_time = group[0][0]
            audio_filename = os.path.join(temp_dir, f"alert_group_{i}.wav")
            generate_tts_audio(combined_message, audio_filename)
            try:
                alert_clip = AudioFileClip(audio_filename)
                alert_clip = alert_clip.set_start(start_time)
                audio_clips.append(alert_clip)
            except Exception as e:
                print(f"Error loading audio clip {audio_filename}: {e}")
        
        if audio_clips:
            composite_audio = CompositeAudioClip(audio_clips)
            final_audio = composite_audio.set_duration(duration)
            final_video = video_clip.set_audio(final_audio)
        else:
            final_video = video_clip
        
        final_video.write_videofile("final_output.mp4", codec="libx264", audio_codec="aac")
        print("Final video with audio saved as 'final_output1.mp4'")
        
        
        shutil.rmtree(temp_dir)
        
       
        with self.engine_lock:
            self.engine.stop()

if __name__ == "__main__":
    try:
        video_path = 'ViewSmall.mp4'  
        detector = HybridSpeedDetector(video_path)
        detector.run()
    except Exception as e:
        print(f"Error: {str(e)}")