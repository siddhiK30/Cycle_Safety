from django.shortcuts import render, redirect

from django.core.files.storage import FileSystemStorage
from .models import VideoUpload, DetectionResult
from .detection import DjangoHybridSpeedDetector
import threading


def upload_video(request):
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        title = request.POST.get('title', 'Untitled')
        
        # Save video upload
        video_upload = VideoUpload.objects.create(
            title=title,
            video_file=video_file,
            
        )
        
        # Create detection result entry
        result = DetectionResult.objects.create(video=video_upload)
        
        # Start processing in background
        detector = DjangoHybridSpeedDetector(
            video_upload.video_file.path,
            result.id
        )
        thread = threading.Thread(target=detector.process_and_save)
        thread.start()
        
        return redirect('processing_status', result_id=result.id)
    
    return render(request, 'upload.html')


def processing_status(request, result_id):
    result = DetectionResult.objects.get(id=result_id)
    return render(request, 'status.html', {'result': result})

def results_list(request):
    results = DetectionResult.objects.filter(
        
    ).order_by('-detection_date')
    return render(request, 'results.html', {'results': results})

