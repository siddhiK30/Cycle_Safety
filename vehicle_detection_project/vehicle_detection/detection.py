

from vehicle_detection.models import DetectionResult  # Changed from relative import
import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import defaultdict
import math
import pyttsx3
import threading

class DjangoHybridSpeedDetector:
    def __init__(self, video_path, result_id):
        self.video_path = video_path
        self.result_id = result_id
        # Initialize all the parameters from the original HybridSpeedDetector
        self.cap = cv2.VideoCapture(video_path)
        # ... (rest of the initialization code from original class)
        
    def process_and_save(self):
        output_filename = f'processed_videos/output_{self.result_id}.mp4'
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, 
                            (self.frame_width, self.frame_height))

        total_vehicles = 0
        total_speed = 0
        speed_count = 0
        danger_count = 0

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            processed_frame = self.process_frame(frame)
            out.write(processed_frame)
            
        result = DetectionResult.objects.get(id=self.result_id)
        result.processed_video = output_filename  # Store relative path
        result.total_vehicles = total_vehicles
        result.average_speed = total_speed / speed_count if speed_count > 0 else 0
        result.danger_incidents = danger_count
        result.save()

        self.cap.release()
        out.release()  
        