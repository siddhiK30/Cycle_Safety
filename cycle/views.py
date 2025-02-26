from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from .models import SafetySession, TrustedContact, LocationShare, SafetyCategory, SafetyTip
from django.contrib import messages
import requests
import logging
from django.http import JsonResponse
import json
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MarkerSerializer
from .models import Marker
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import SafetyIncident
from math import radians, sin, cos, sqrt, atan2
from .models import Users
from django.contrib.auth.models import User
from math import radians, sin, cos, sqrt, atan2
from .models import Users

import uuid
from twilio.rest import Client
from django.conf import settings
import googlemaps

from django.shortcuts import render

def start(request):
    return render(request, "landing.html")
def ride(request):
    return render(request, "profile.html")


# API route to fetch all markers
def get_markers(request):
    markers = Marker.objects.all().values('lat', 'lng')
    print(markers)  # Check if the correct markers are being returned
    return JsonResponse(list(markers), safe=False)


# API route to add a new marker
import json
from django.http import JsonResponse

def add_marker(request):
    if request.method == "POST":
        data = json.loads(request.body)
        lat = data.get('lat')
        lng = data.get('lng')

        print(f"Received marker: lat={lat}, lng={lng}")  # Debug log to check the received data

        # Save the marker to the database
        marker = Marker.objects.create(lat=lat, lng=lng)
        return JsonResponse({'id': marker.id, 'lat': lat, 'lng': lng})


def index(request):
    markers = Marker.objects.all()  # Fetch all markers from the database
    markers_data = list(markers.values('lat', 'lng'))  # Convert queryset to list of dicts
    return render(request, 'area_flag.html', {'markers': markers_data})

class MarkerListCreateView(APIView):
    def get(self, request):
        markers = Marker.objects.all()
        serializer = MarkerSerializer(markers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MarkerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarkerUpdateView(APIView):
    def put(self, request, pk):
        try:
            marker = Marker.objects.get(pk=pk)
            serializer = MarkerSerializer(marker, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Marker.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Used!')
                return redirect('signup')
            
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Already have an account for this Email!')
                return redirect('signup')
            
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # startup = Startup(user=user, name=username, email=email)
                # startup.save()
                return redirect('login')
        else:
            messages.info(request, 'Password Not The Same!')
            return redirect('signup')
        
    else:    
        return render(request, 'signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Credentials Invalid!')
            return redirect('login')
    else:
        return render(request, 'login.html')  
    

def videocall_view(request):
    return render(request, 'videocall.html')  # Correct relative path
def voice_view(request):
    return render(request, 'voicecall.html') 
def video_view(request):
    return render(request, 'video.html') 



def badges(request):
    context = {
        'count': MarkerCount.get_count(),
        'incident_count' : IncidentMarkerCount.get_count()
    }
    return render(request, 'badge.html', context)


def sessions(request):
    sessions = SafetySession.objects.all()
    return render(request, 'sessions.html', {'sessions': sessions})    


# Initialize logger
logger = logging.getLogger(__name__)

def geocode_address(address):
    if not address:
        return None, None

    try:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'in',  # Restrict search to India
        }
        headers = {'User-Agent': 'SurakshaSathi/1.0'}
        response = requests.get(base_url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
        
        # Log error when no result is found
        logger.error(f"No geocoding result for address: {address}")
        return None, None
    except Exception as e:
        # Log exception for debugging
        logger.error(f"Geocoding error: {e}")
        return None, None


def session_map(request, session_id):
    session = get_object_or_404(SafetySession, id=session_id)
    
    # Check if session has a location
    if not session.location:
        return render(request, 'session_map.html', {
            'session': session,
            'error': 'No valid location available for this session.'
        })
    
    # Get coordinates using geocode_address
    lat, lng = geocode_address(session.location)
    
    if lat is None or lng is None:
        # If geocoding fails, render with an error message
        return render(request, 'session_map.html', {
            'session': session,
            'error': 'Unable to geocode the session location.'
        })

    context = {
        'session': session,
        'session_lat': lat,
        'session_lng': lng
    }
    return render(request, 'session_map.html', context)

def safety_tips(request):
    return render(request, 'safety_tips.html')

def upload(request):
    return render(request, 'upload.html')

def area_flag(request):
    return render(request, 'area_flag.html')

   
def anomoly(request):
    return render(request, 'anomoly.html')

def offline(request):
    return render(request, 'mumbai_map.html')
def health(request):
    return render(request, "health.html")
# def chatbot_api(request):
#     if request.method == 'POST':
#         user_message = request.POST.get('message')
#         # Define your prompt for OpenAI GPT
#         prompt = """You are a safety assistant for women. Provide clear, concise, and actionable safety advice. Ensure your answers are friendly, empathetic, and professional. Also if they feel stressed make them feel relief give them solutions. Your response should not be bigger than 5 sentence but it can be smaller upto one sentence depeneds on question. Answer the following question based on information provided earlier: 
#             """ 
        
#         prompt += user_message

#         api_key = 'AIzaSyA1fQnq8k8ckP5WEyF97kDmLiAGnVhPKz4'

#         try:
#             genai.configure(api_key=api_key)
#             model = genai.GenerativeModel("gemini-1.5-flash")
#             response = model.generate_content(prompt)
#             reply = response.text

#             return JsonResponse({'reply': reply})

#         except Exception as e:
#             return JsonResponse({'reply': f'An error occurred: {str(e)}'}) 
# logger = logging.getLogger(__name__)


import requests
from django.http import JsonResponse
from django.conf import settings
import logging
import json
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)

def get_address_from_coordinates(lat, lon):
    """Reverse geocode coordinates using Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {'User-Agent': 'SafetyTrails/1.0'}  # Required by Nominatim
        response = requests.get(url, headers=headers)
        data = response.json()
        return data.get('display_name', '')
    except Exception as e:
        logger.error(f"Error in reverse geocoding: {str(e)}")
        return None

def get_nearby_services(lat, lon):
    """Get nearby police stations and hospitals using Overpass API"""
    try:
        # Search within 5km radius
        radius = 5000
        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="police"](around:{radius},{lat},{lon});
          way["amenity"="police"](around:{radius},{lat},{lon});
          node["amenity"="hospital"](around:{radius},{lat},{lon});
          way["amenity"="hospital"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """
        response = requests.post(overpass_url, data=overpass_query)
        data = response.json()
        
        services = []
        for element in data.get('elements', []):
            if element.get('tags'):
                service = {
                    'type': element['tags'].get('amenity'),
                    'name': element['tags'].get('name', 'Unnamed'),
                    'lat': element.get('lat', 0),
                    'lon': element.get('lon', 0)
                }
                services.append(service)
        
        return services
    except Exception as e:
        logger.error(f"Error fetching nearby services: {str(e)}")
        return []




def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def get_nearby_users(current_user, max_distance=5):
    """Get list of users within specified distance"""
    if not current_user.latitude or not current_user.longitude:
        return []
        
    users = Users.objects.exclude(user=current_user.user).filter(is_active=True)
    nearby_users = []
    
    for user in users:
        if user.latitude and user.longitude:
            distance = calculate_distance(
                current_user.latitude, 
                current_user.longitude,
                user.latitude, 
                user.longitude
            )
            if distance <= max_distance:
                nearby_users.append({
                    'user': user,
                    'name': user.name,
                    'distance': round(distance, 1)
                })
    
    return sorted(nearby_users, key=lambda x: x['distance'])

from voice_detector.utils import VoiceDetector
from voice_detector.models import UserAlertConfig

@login_required
def home_view(request):
    try:
        # Initialize voice detection for the user
        config, created = UserAlertConfig.objects.get_or_create(
            user=request.user,
            defaults={
                'phone_number': request.user.profile.phone_number if hasattr(request.user, 'profile') else '',
                'required_repetitions': 3,
                'time_threshold': 5
            }
        )
        
        # Start voice detection
        detector = VoiceDetector()
        detector.start_detection(config)

        # Your existing code
        current_user_profile = Users.objects.get(user=request.user)
        nearby_users = get_nearby_users(current_user_profile)
        
        context = {
            'current_user_name': current_user_profile.name,
            'current_user_location': {
                'latitude': current_user_profile.latitude,
                'longitude': current_user_profile.longitude
            },
            'nearby_users': nearby_users,   
            'has_location': bool(current_user_profile.latitude and current_user_profile.longitude)
        }
        
        return render(request, 'home.html', context)
        
    except Users.DoesNotExist:
        return render(request, 'home.html', {
            'error_message': "Please complete your profile to see nearby users.",
            'nearby_users': [],
            'has_location': False
        })

@csrf_exempt
@login_required
def send_emergency_alert(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        location = data.get('location')
        requester = request.user
        requester_profile = Users.objects.get(user=requester)
        
        if not location or 'latitude' not in location or 'longitude' not in location:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid location data'
            }, status=400)
            
        # Update requester's location
        requester_profile.latitude = location['latitude']
        requester_profile.longitude = location['longitude']
        requester_profile.save()
        
        # Get nearby users
        nearby_users = get_nearby_users(requester_profile)
        location_url = f"https://www.google.com/maps?q={location['latitude']},{location['longitude']}"
        
        # Initialize Twilio and track messages
        twilio = TwilioService()
        message_attempts = []
        
        # Send alerts to nearby users
        for user_data in nearby_users:
            nearby_user = user_data['user']
            try:
                if nearby_user.phone_number:
                    success, msg_id = twilio.send_emergency_sms(
                        to_number=nearby_user.phone_number,
                        requester_name=requester.username,
                        location_url=location_url,
                        message_type='nearby user',
                        
                    )
                    message_attempts.append({
                        'user_name': nearby_user.name,
                        'distance': user_data['distance'],
                        'success': success,
                        'message_id': msg_id
                    })
            except Exception as e:
                logger.error(f"Error sending alert to nearby user {nearby_user.name}: {str(e)}")
                message_attempts.append({
                    'user_name': nearby_user.name,
                    'distance': user_data['distance'],
                    'success': False,
                    'error': str(e)
                })

        # Send alerts to trusted contacts
        trusted_contacts = TrustedContact.objects.filter(user=requester)
        for contact in trusted_contacts:
            try:
                success, msg_id = twilio.send_emergency_sms(
                    to_number=contact.phone,
                    requester_name=requester.username,
                    location_url=location_url,
                    message_type='trusted_contact'
                )
                message_attempts.append({
                    'contact_name': contact.name,
                    'type': 'trusted_contact',
                    'success': success,
                    'message_id': msg_id
                })
            except Exception as e:
                logger.error(f"Error sending alert to trusted contact {contact.name}: {str(e)}")
                message_attempts.append({
                    'contact_name': contact.name,
                    'type': 'trusted_contact',
                    'success': False,
                    'error': str(e)
                })

        return JsonResponse({
            'status': 'success',
            'message': f"Emergency alerts sent to {len(message_attempts)} recipients",
            'details': {
                'nearby_users_count': len(nearby_users),
                'trusted_contacts_count': len(trusted_contacts),
                'message_attempts': message_attempts
            }
        })

    except Exception as e:
        logger.error(f"Emergency alert error: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

from django.http import JsonResponse

def send_help_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('name', '')
            # Process the help request, e.g., send an email or log it
            # Respond with success
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

from twilio.rest import Client
from django.conf import settings
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Users, TrustedContact
from .services import TwilioService

# @login_required
# @require_http_methods(["POST"])
# def update_location(request):
#     try:
#         data = json.loads(request.body)
#         location = LocationShare.objects.create(
#             user=request.user,
#             latitude=data['latitude'],
#             longitude=data['longitude'],
#             timestamp=data['timestamp']
#         )
        
#         # Get user's trusted contacts
#         trusted_contacts = TrustedContact.objects.filter(user=request.user)
        
#         # Notify trusted contacts through WebSocket
#         channel_layer = get_channel_layer()
#         for contact in trusted_contacts:
#             async_to_sync(channel_layer.group_send)(
#                 f"location_updates_{contact.id}",
#                 {
#                     "type": "location_update",
#                     "message": {
#                         "latitude": data['latitude'],
#                         "longitude": data['longitude'],
#                         "timestamp": data['timestamp'],
#                         "user": request.user.username
#                     }
#                 }
#             )
        
#         return JsonResponse({"status": "success"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=400)

# @login_required
# @require_http_methods(["POST"])
# def stop_sharing(request):
#     try:
#         # Update sharing status
#         LocationShare.objects.filter(user=request.user, active=True).update(active=False)
        
#         # Notify trusted contacts that sharing has stopped
#         trusted_contacts = TrustedContact.objects.filter(user=request.user)
#         channel_layer = get_channel_layer()
        
#         for contact in trusted_contacts:
#             async_to_sync(channel_layer.group_send)(
#                 f"location_updates_{contact.id}",
#                 {
#                     "type": "sharing_stopped",
#                     "message": {
#                         "user": request.user.username
#                     }
#                 }
#             )
        
#         return JsonResponse({"status": "success"})
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
@csrf_exempt
def send_sos(request):
    if request.method == "POST":
        try:
            # Load location data from request
            data = json.loads(request.body)
            latitude = data["latitude"]
            longitude = data["longitude"]

            # Define user's emergency contacts
            emergency_contacts = [
                "+917066343531",  # Contact 1
                #"+918879363714",  # Contact 2
                 "+919930404660",  # Contact 3
            ]

            # Twilio credentials
            account_sid = "ACf204394952d87fc728ead2d682620b32"
            auth_token = "0a37c5f1e46ace5872fa1a444b5883a0"
            client = Client(account_sid, auth_token)

            # Message body with location
            message_body = (
                f"Emergency! The user needs help. Location: "
                f"https://www.google.com/maps?q={latitude},{longitude}"
            )

            # Send SMS to all emergency contacts
            for contact in emergency_contacts:
                client.messages.create(
                    body=message_body,
                    from_="+16084296876",
                    to=contact,
                )

            return JsonResponse({"message": "SOS messages sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=400)


    
# Initialize Twilio client
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

# Initialize Google Maps client
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)



