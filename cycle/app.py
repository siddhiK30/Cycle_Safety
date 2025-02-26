# Backend (Python) - Modified HybridSpeedDetector class
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import base64
import json

app = Flask(__name__)
socketio = SocketIO(app)

class HybridSpeedDetector:
    def __init__(self, video_path):
        # Keep existing initialization code
        # Add WebSocket support for real-time updates
        self.latest_metrics = {
            'distance': 0,
            'speed': 0,
            'warning_level': 'Safe',
            'status': 'Safe Distance'
        }

    def process_frame(self, frame):
        # Existing process_frame code
        # Add metric updates
        results = self.model(frame, verbose=False)[0]
        current_time = time.time()
        
        # Reset metrics for new frame
        closest_vehicle = {
            'distance': float('inf'),
            'speed': 0,
            'warning_level': 'Safe'
        }
        
        for detection in results.boxes.data.tolist():
            x1, y1, x2, y2, conf, class_id = detection
            
            if conf < self.conf_threshold or int(class_id) not in self.vehicle_classes:
                continue
            
            track_id, area, depth, approach_speed, depth_confidence, velocity = self.update_tracking(detection, current_time)
            warning_msg, color, severity = self.get_hybrid_warning(area, depth, approach_speed, depth_confidence)
            
            # Update closest vehicle metrics
            if depth < closest_vehicle['distance']:
                closest_vehicle['distance'] = depth
                closest_vehicle['speed'] = velocity * 3.6  # Convert to km/h
                if severity == 2:
                    closest_vehicle['warning_level'] = 'High'
                    closest_vehicle['status'] = 'Danger'
                elif severity == 1:
                    closest_vehicle['warning_level'] = 'Medium'
                    closest_vehicle['status'] = 'Warning'
                else:
                    closest_vehicle['warning_level'] = 'Low'
                    closest_vehicle['status'] = 'Safe Distance'
            
            # Existing drawing code...
        
        # Update latest metrics
        self.latest_metrics = closest_vehicle
        
        # Emit metrics through WebSocket
        socketio.emit('vehicle_metrics', closest_vehicle)
        
        return frame

    def generate_frames(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
                
            processed_frame = self.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(detector.generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

detector = HybridSpeedDetector('cars.mp4')