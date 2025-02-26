from django.db import models

class VideoUpload(models.Model):
    title = models.CharField(max_length=100)
    video_file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


    def __str__(self):
        return self.title

class DetectionResult(models.Model):
    video = models.ForeignKey(VideoUpload, on_delete=models.CASCADE)
    processed_video = models.FileField(upload_to='processed_videos/', null=True)
    detection_date = models.DateTimeField(auto_now_add=True)
    total_vehicles = models.IntegerField(default=0)
    average_speed = models.FloatField(default=0.0)
    danger_incidents = models.IntegerField(default=0)