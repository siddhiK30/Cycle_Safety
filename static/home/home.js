// mapboxgl.accessToken = 'pk.eyJ1IjoibWFuYXZpMTIzIiwiYSI6ImNsc3hjdjAzcTAxb3kycXAya3IyNnl3djgifQ.vyfIAPnhABA9sgvga4F6XA';
        
//         // Initialize variables
// let userLocation = null;
// let mapInstance = null;
// let directions = null;
// let routeCoords = [];
// let deviationAlert = false;
// let sosTimeout = null;
// let lastLocation = null;
// let lastMovementTime = Date.now();
// let stationaryTimeout = null;
// let stationaryCheckTimeout = null;
// let voiceEnabled = false;
// let currentStep = 0;
// let routeInstructions = [];
// const speechSynth = window.speechSynthesis;
// const safeDistanceThreshold = 0.005;
// const stationaryThreshold = 0.0001;
// const stationaryTimeLimit = 10000 * 60 * 1000;
// const sosDelay = 5 * 1000;

// // Initialize map and location tracking
// async function storeUserLocation(location) {
//     try {
//         await fetch('https://suraksha-84726-default-rtdb.firebaseio.com/users/N4iwwMbD5xViwkdjFSFk7dmQTyw2/location.json', {
//             method: 'PATCH',
//             headers: { 'Content-Type': 'application/json' },
//             body: JSON.stringify(location)
//         });
//     } catch (error) {
//         console.error('Error storing location:', error);
//     }
// }
// function getCookie(name) {
//             let cookieValue = null;
//             if (document.cookie && document.cookie !== '') {
//                 const cookies = document.cookie.split(';');
//                 for (let i = 0; i < cookies.length; i++) {
//                     const cookie = cookies[i].trim();
//                     if (cookie.startsWith(name + '=')) {
//                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                         break;
//                     }
//                 }
//             }
//             return cookieValue;
//         }

//         document.getElementById('sosButton').addEventListener('click', function () {
//             console.alert("SOS send Successfully")
//     isSOSActive = true;
//     startVideo();
    
//     // Show the "Ask All for Help" button
//     const askAllButton = document.getElementById('askAllForHelp');
//     askAllButton.classList.remove('hidden');
//     askAllButton.classList.add('visible');

//     // Add location fetching and sending SOS SMS
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             (position) => {
//                 const { latitude, longitude } = position.coords;

//                 // Send SOS message to the backend
//                 fetch("/send-sos/", {
//                     method: "POST",
//                     headers: {
//                         "Content-Type": "application/json",
//                         "X-CSRFToken": getCookie("csrftoken"),
//                     },
//                     body: JSON.stringify({ latitude, longitude }),
//                 })
//                     .then((response) => response.json())
//                     .then((data) => {
//                         alert(data.message); // Notify user
//                     })
//                     .catch((error) => {
//                         console.error("Error:", error);
//                     });

//                 // Additionally, send location as part of the SOS alert
//                 sendSOSAlert(latitude, longitude);
//             },
//             (error) => {
//                 alert("Unable to fetch location. Please enable GPS.");
//             }
//         );
//     } else {
//         alert("Geolocation is not supported by this browser.");
//     }
// });
// function initMap() {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             position => {
//                 const { latitude, longitude } = position.coords;
//                 userLocation = { latitude, longitude };
//                 lastLocation = { latitude, longitude };
//                 storeUserLocation({ latitude, longitude });
//                 setupMap();
//                 startStationaryCheck();
//             },
//             error => {
//                 console.error("Error getting location:", error);
//                 alert("Unable to retrieve your location. Please ensure location services are enabled.");
//             }
//         );
//     } else {
//         alert("Geolocation is not supported by this browser.");
//     }
// }

// // Voice navigation functions
// function toggleVoiceGuidance() {
//     voiceEnabled = !voiceEnabled;
//     const button = document.getElementById('voiceToggle');
//     button.textContent = voiceEnabled ? 'Disable Voice' : 'Enable Voice';
//     if (voiceEnabled && routeInstructions.length > 0) {
//         speakCurrentInstruction();
//     }
// }

// function speakCurrentInstruction() {
//     if (routeInstructions.length > 0 && currentStep < routeInstructions.length) {
//         const utterance = new SpeechSynthesisUtterance(routeInstructions[currentStep]);
//         utterance.rate = 0.9;
//         utterance.pitch = 1.0;
//         speechSynth.speak(utterance);
//     }
// }

// function setupMap() {
//     mapInstance = new mapboxgl.Map({
//         container: 'map',
//         style: 'mapbox://styles/mapbox/streets-v11',
//         center: [userLocation.longitude, userLocation.latitude],
//         zoom: 14
//     });

//     directions = new MapboxDirections({
//         accessToken: mapboxgl.accessToken,
//         unit: 'metric',
//         profile: 'mapbox/driving'
//     });
//     mapInstance.addControl(directions, 'top-left');

//     new mapboxgl.Marker({ color: '#4B0082' })
//         .setLngLat([userLocation.longitude, userLocation.latitude])
//         .addTo(mapInstance)
//         .setPopup(new mapboxgl.Popup().setText('You are here'));

//     directions.on('route', e => {
//         if (e.route && e.route[0]) {
//             routeCoords = e.route[0].geometry.coordinates;
//             routeInstructions = e.route[0].legs[0].steps.map(step => step.maneuver.instruction);
//             currentStep = 0;
//             monitorRoute(routeCoords);
//             if (voiceEnabled) {
//                 speakCurrentInstruction();
//             }
//         }
//     });
// }

// function startStationaryCheck() {
//     if (stationaryCheckTimeout) {
//         clearTimeout(stationaryCheckTimeout);
//     }
//     stationaryCheckTimeout = setInterval(checkStationary, 10000);
// }

// function checkStationary() {
//     if (lastLocation && !deviationAlert) {
//         const timeSinceLastMovement = Date.now() - lastMovementTime;
//         if (timeSinceLastMovement >= stationaryTimeLimit) {
//             handleStationary();
//         }
//     }
// }

// function calculateDistanceToNextStep(currentCoords, routeCoords) {
//     const nextWaypoint = routeCoords[currentStep + 1];
//     if (!nextWaypoint) return Infinity;
    
//     return Math.sqrt(
//         Math.pow(currentCoords[0] - nextWaypoint[0], 2) + 
//         Math.pow(currentCoords[1] - nextWaypoint[1], 2)
//     );
// }

// function monitorRoute(routeCoords) {
//     if (navigator.geolocation) {
//         navigator.geolocation.watchPosition(
//             position => {
//                 const { latitude, longitude } = position.coords;
//                 storeUserLocation({ latitude, longitude });

//                 if (lastLocation) {
//                     const movement = Math.sqrt(
//                         Math.pow(longitude - lastLocation.longitude, 2) + 
//                         Math.pow(latitude - lastLocation.latitude, 2)
//                     );
//                     if (movement > stationaryThreshold) {
//                         lastMovementTime = Date.now();
//                     }
//                 }

//                 lastLocation = { latitude, longitude };

//                 if (Array.isArray(routeCoords) && routeCoords.length > 0) {
//                     const isDeviating = checkDeviation([longitude, latitude], routeCoords);
                    
//                     if (voiceEnabled && routeInstructions.length > 0) {
//                         const distanceToNextStep = calculateDistanceToNextStep([longitude, latitude], routeCoords);
//                         if (distanceToNextStep < 0.0001 && currentStep < routeInstructions.length - 1) {
//                             currentStep++;
//                             speakCurrentInstruction();
//                         }
//                     }

//                     if (isDeviating) {
//                         handleDeviation();
//                     } else if (deviationAlert) {
//                         clearTimeout(sosTimeout);
//                         deviationAlert = false;
//                         document.getElementById('alertBox').style.display = 'none';
//                     }
//                 }
//             },
//             error => console.error("Error watching position:", error)
//         );
//     }
// }

// function checkDeviation(currentCoords, routeCoords) {
//     if (!Array.isArray(routeCoords) || routeCoords.length === 0) return false;
//     return !routeCoords.some(([lng, lat]) => {
//         const distance = Math.sqrt(
//             Math.pow(currentCoords[0] - lng, 2) + Math.pow(currentCoords[1] - lat, 2)
//         );
//         return distance < safeDistanceThreshold;
//     });
// }
// const nearbyUsersButton = document.getElementById('nearbyUsersButton');
//         const popup = document.getElementById('nearbyUsersPopup');
//         const closeButton = document.querySelector('.close-button');

//         nearbyUsersButton.addEventListener('click', () => {
//             popup.style.display = 'block';
//         });

//         closeButton.addEventListener('click', () => {
//             popup.style.display = 'none';
//         });

//         window.addEventListener('click', (event) => {
//             if (event.target === popup) {
//                 popup.style.display = 'none';
//             }
//         });
// function getCookie(name) {
//     const value = document.cookie;
//     const parts = value.split(`; ${name}=`);
//     if (parts.length === 2) return parts.pop().split(';').shift();
// }

// function sendSosAlert() {
//     if (navigator.geolocation) {
//         navigator.geolocation.getCurrentPosition(
//             (position) => {
//                 const { latitude, longitude } = position.coords;
                
//                 fetch("/send-sos/", {
//                     method: "POST",
//                     headers: {
//                         "Content-Type": "application/json",
//                         "X-CSRFToken": getCookie("csrftoken")
//                     },
//                     body: JSON.stringify({ latitude, longitude }),
//                 })
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log("SOS sent successfully:", data);
//                     alert("Emergency contacts have been notified!");
//                 })
//                 .catch(error => {
//                     console.error("Error sending SOS:", error);
//                     alert("Failed to send emergency alert.");
//                 });
//             },
//             (error) => {
//                 alert("Unable to fetch location. Please enable GPS.");
//             }
//         );
//     } else {
//         alert("Geolocation is not supported by this browser.");
//     }
// }

// let alertSound = document.getElementById('alertSound');
// let alertModal = document.getElementById('alertModal');

// function showAlert(message, isEmergency = false) {
//     document.getElementById('alertMessage').textContent = message;
//     document.getElementById('alertBox').style.display = 'block';
    
//     document.getElementById('modalMessage').textContent = message;
//     alertModal.style.display = 'flex';
    
//     alertSound.play();
    
//     if (Notification.permission === "granted") {
//         new Notification("Safety Alert", { body: message });
//         alertSound.pause();
//     }
    
//     if (isEmergency) {
//         alert(message);
//         alertSound.pause();
//     }
// }

// function handleStationary() {
//     if (!deviationAlert) {
//         deviationAlert = true;
//         showAlert('You haven\'t moved for 8 minutes. Are you safe?');
//         sosTimeout = setTimeout(() => {
//             console.log("sendSosAlert");
//             sendSosAlert();
//             alertSound.pause();   
//         }, sosDelay);
//     }
// }

// function handleDeviation() {
//     if (!deviationAlert) {
//         deviationAlert = true;
//         showAlert('Deviation Detected! Confirm if you are safe.');
//         sosTimeout = setTimeout(() => {
//             showAlert('Emergency: No response received! Sending SOS Alert!', true);
//             sendSosAlert();
//         }, sosDelay);
//     }
// }

// function handleConfirmSafety() {
//     deviationAlert = false;
//     document.getElementById('alertBox').style.display = 'none';
//     alertModal.style.display = 'none';
//     alertSound.pause();
//     alertSound.currentTime = 0;
//     clearTimeout(sosTimeout);
//     lastMovementTime = Date.now();
// }

// function requestNotificationPermission() {
//     if (Notification.permission !== "granted" && Notification.permission !== "denied") {
//         Notification.requestPermission();
//     }
// }

// // Initialize everything
// function init() {
//     initMap();
//     requestNotificationPermission();
// }
// const API_URL = "https://detect.roboflow.com/driver-fatigue/2";
//         const API_KEY = "7y9E0pW7t5IcONqrvdVn";
//         let lastAlertTime = 0;
//         const ALERT_COOLDOWN = 10000; // 10 seconds in milliseconds

//         async function initCamera() {
//             try {
//                 const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//                 const video = document.getElementById('videoFeed');
//                 video.srcObject = stream;

//                 // Start detection loop
//                 setInterval(detectFatigue, 1000);
//             } catch (error) {
//                 console.error("Error accessing camera:", error);
//             }
//         }
//         async function detectFatigue() {
//     const video = document.getElementById('videoFeed');
//     const canvas = document.createElement('canvas');
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext('2d');
//     ctx.drawImage(video, 0, 0);

//     // Convert canvas to blob
//     const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
//     const formData = new FormData();
//     formData.append('file', blob);

//     // Function to speak alerts using Web Speech API
//     function speakAlert(message) {
//         const speech = new SpeechSynthesisUtterance(message);
//         speech.rate = 0.9;  // Slightly slower rate for clarity
//         speech.pitch = 1;   // Normal pitch
//         speech.volume = 1;  // Full volume
//         window.speechSynthesis.speak(speech);
//     }

//     try {
//         const response = await fetch(`${API_URL}?api_key=${API_KEY}`, {
//             method: 'POST',
//             body: formData
//         });
//         const result = await response.json();

//         if (result.predictions) {
//             const currentTime = Date.now();
//             const statusElement = document.getElementById('detectionStatus');
//             const alertElement = document.getElementById('alertMessage');

//             for (const prediction of result.predictions) {
//                 if (prediction.class.toLowerCase().includes('drowsy')) {
//                     statusElement.className = 'detection-status status-drowsy';
//                     statusElement.textContent = 'Drowsy';

//                     if (currentTime - lastAlertTime >= ALERT_COOLDOWN) {
//                         alertElement.style.display = 'block';
                        
//                         // Speak the alert message
//                         speakAlert("Alert! You seem tired. Please take a break and freshen up for your safety.");
//                         lastAlertTime = currentTime;

//                         // Hide alert after 10 seconds
//                         setTimeout(() => {
//                             alertElement.style.display = 'none';
//                         }, 10000);
//                     }
//                 } else {
//                     statusElement.className = 'detection-status status-awake';
//                     statusElement.textContent = 'Awake';
//                     alertElement.style.display = 'none';
//                 }
//             }
//         }
//     } catch (error) {
//         console.error("Error during fatigue detection:", error);
//     }
// }
// function handleDeviation() {
//             if (!deviationAlert) {
//                 deviationAlert = true;
//                 // Set a 30-second delay before showing the alert
//                 setTimeout(() => {
//                     showAlert('Deviation Detected! Confirm if you are safe.');
//                     sosTimeout = setTimeout(() => {
//                         showAlert('Emergency: No response received! Sending SOS Alert!', true);
//                         sendSosAlert();
//                     }, sosDelay);
//                 }, 30000); // 30 seconds delay
//             }
//         }

//         function handleStationary() {
//             if (!deviationAlert) {
//                 deviationAlert = true;
//                 // Set an 8-minute delay before showing the alert
//                 setTimeout(() => {
//                     showAlert('You haven\'t moved for 8 minutes. Are you safe?');
//                     sosTimeout = setTimeout(() => {
//                         sendSosAlert();
//                         alertSound.pause();   
//                     }, sosDelay);
//                 }, 480000); // 8 minutes delay
//             }
//         }
//         // Initialize
//         initCamera();
// // Start the application
// initMap();
// class SpeedTracker {
//     constructor() {
//         this.maxSpeed = 40; // Maximum speed on the speedometer
//         this.currentSpeed = 0;
//         this.speeds = [];
//         this.distance = 0;
        
//         // Cache DOM elements
//         this.speedDisplay = document.querySelector('.current-speed');
//         this.speedometer = document.querySelector('.speedometer-value');
//         this.avgSpeedDisplay = document.querySelector('.average-speed');
//         this.maxSpeedDisplay = document.querySelector('.max-speed');
//         this.distanceDisplay = document.querySelector('.total-distance');
        
//         // Initialize colors
//         this.speedColors = {
//             low: '#4CAF50',    // Green
//             medium: '#FFA726', // Orange
//             high: '#EF5350'    // Red
//         };
//     }

//     // Calculate the SVG path for the speedometer arc
//     calculateArc(speed) {
//         const percentage = speed / this.maxSpeed;
//         const endAngle = 180 * percentage;
//         const x = 10 + 140 * percentage;
//         const y = 90 - Math.sin(endAngle * Math.PI / 180) * 70;
//         return `M10,90 A70,70 0 0,1 ${x},${y}`;
//     }

//     // Update the speedometer color based on speed
//     updateColor(speed) {
//         let color;
//         if (speed < this.maxSpeed * 0.4) {
//             color = this.speedColors.low;
//         } else if (speed < this.maxSpeed * 0.7) {
//             color = this.speedColors.medium;
//         } else {
//             color = this.speedColors.high;
//         }
        
//         this.speedometer.style.stroke = color;
//         this.speedDisplay.style.color = color;
//     }

//     // Update statistics
//     updateStats() {
//         // Calculate average speed
//         const avgSpeed = this.speeds.length > 0 
//             ? this.speeds.reduce((a, b) => a + b) / this.speeds.length 
//             : 0;
        
//         // Update displays
//         this.avgSpeedDisplay.textContent = avgSpeed.toFixed(1);
//         this.maxSpeedDisplay.textContent = Math.max(...this.speeds, 0).toFixed(1);
//         this.distanceDisplay.textContent = this.distance.toFixed(1);
//     }

//     // Set new speed value
//     setSpeed(speed) {
//         // Clamp speed between 0 and maxSpeed
//         this.currentSpeed = Math.min(Math.max(speed, 0), this.maxSpeed);
        
//         // Update speedometer
//         this.speedometer.setAttribute('d', this.calculateArc(this.currentSpeed));
//         this.speedDisplay.textContent = `${this.currentSpeed.toFixed(1)} `;
        
//         // Update color
//         this.updateColor(this.currentSpeed);
        
//         // Update statistics
//         this.speeds.push(this.currentSpeed);
//         // Keep only last 10 readings for average
//         if (this.speeds.length > 10) this.speeds.shift();
        
//         // Update distance (simplified calculation)
//         this.distance += (this.currentSpeed / 3600); // km/h to km
        
//         this.updateStats();
//     }

//     // Simulate speed changes (for testing)
//     startSimulation() {
//         let time = 0;
//         const interval = setInterval(() => {
//             // Simulate varying speed using sine wave
//             const speed = 20 + Math.sin(time) * 15;
//             this.setSpeed(speed);
//             time += 0.1;
//         }, 100);

//         return () => clearInterval(interval); // Return cleanup function
//     }
// }

// // Initialize the speed tracker
// const speedTracker = new SpeedTracker();

// // Example usage:
// // speedTracker.setSpeed(25); // Set speed to 25 km/h
// // speedTracker.startSimulation(); // Start speed simulation

// // For testing: simulate random speed updates
// function simulateSpeed() {
//     const speed = Math.random() * 40; // Random speed between 0 and 40
//     speedTracker.setSpeed(speed);
// }

// // Update speed every 2 seconds for demonstration
// setInterval(simulateSpeed, 2000);
// const helpButton = document.getElementById('help-button');
//         const userList = document.getElementById('user-list');
//         const noUsersMessage = document.getElementById('no-users-message');
//         const nearbyUsers = []; // Replace with actual logic to fetch nearby users

//         // Sample nearby user data (replace with your actual data fetching)
//         if (nearbyUsers.length === 0) {
//             userList.style.display = 'none';
//             noUsersMessage.style.display = 'block';
//         } else {
//             nearbyUsers.forEach(user => {
//                 const li = document.createElement('li');
//                 li.textContent = user; // Or user.name if you have user objects
//                 userList.appendChild(li);
//             });
//         }


//         helpButton.addEventListener('click', () => {
//             if (helpButton.textContent === 'Ask for Help') {
//                 helpButton.textContent = 'Help Requested';
//                 helpButton.style.backgroundColor = 'yellow'; // Or any color you like
//                 helpButton.style.color = 'black'; // Ensure good contrast
//                 // Add logic here to actually send a help request (e.g., using AJAX)
//             } else {
//                 helpButton.textContent = 'Ask for Help';
//                 helpButton.style.backgroundColor = ''; // Reset to default
//                 helpButton.style.color = ''; // Reset to default
//                 // Add logic here to handle cancelling a help request
//             }
//         });

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Download, ArrowLeft, FileText, RefreshCw, Camera, Bell } from 'lucide-react';

const API_URL = "https://detect.roboflow.com/driver-fatigue/2";
const API_KEY = "7y9E0pW7t5IcONqrvdVn";
const ALERT_COOLDOWN = 10000; // 10 seconds in milliseconds

const LectureDetailPage = () => {
  const { id } = useParams();
  const [lecture, setLecture] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState('');
  const [summarizing, setSummarizing] = useState(false);
  
  // Fatigue detection states
  const [isVisible, setIsVisible] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState('Awake');
  const [showAlert, setShowAlert] = useState(false);
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const videoRef = useRef(null);
  const lastAlertTimeRef = useRef(0);

  const fetchLectureDetails = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:8000/resources/${id}/`);
      setLecture(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching lecture details:', err);
      setError('Failed to load lecture details');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLectureDetails();
  }, [id]);

  const speakAlert = (message) => {
    const speech = new SpeechSynthesisUtterance(message);
    speech.rate = 0.9;
    speech.pitch = 1;
    speech.volume = 1;
    window.speechSynthesis.speak(speech);
  };

  const detectFatigue = async () => {
    if (!videoRef.current || !cameraEnabled) return;

    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    try {
      const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
      const formData = new FormData();
      formData.append('file', blob);

      const response = await fetch(`${API_URL}?api_key=${API_KEY}`, {
        method: 'POST',
        body: formData
      });
      const result = await response.json();

      if (result.predictions) {
        const currentTime = Date.now();
        for (const prediction of result.predictions) {
          if (prediction.class.toLowerCase().includes('drowsy')) {
            setDetectionStatus('Drowsy');
            if (currentTime - lastAlertTimeRef.current >= ALERT_COOLDOWN) {
              setShowAlert(true);
              speakAlert("You seem tired. Please take a break and freshen up.");
              lastAlertTimeRef.current = currentTime;
              setTimeout(() => setShowAlert(false), 10000);
            }
          } else {
            setDetectionStatus('Awake');
            setShowAlert(false);
          }
        }
      }
    } catch (error) {
      console.error("Error during fatigue detection:", error);
    }
  };

  const toggleCamera = async () => {
    if (!cameraEnabled) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraEnabled(true);
          setIsVisible(true);
        }
      } catch (error) {
        console.error("Error accessing camera:", error);
      }
    } else {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      setCameraEnabled(false);
      setIsVisible(false);
    }
  };

  useEffect(() => {
    let detectionInterval;
    if (cameraEnabled) {
      detectionInterval = setInterval(detectFatigue, 1000);
    }
    return () => {
      clearInterval(detectionInterval);
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, [cameraEnabled]);

  const handleDownload = async (fileType, fileName) => {
    try {
      const response = await axios({
        url: `http://127.0.0.1:8000/resources/${id}/download_${fileType}/`,
        method: 'GET',
        responseType: 'blob',
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  };

  const summarise = async () => {
    try {
      setSummarizing(true);
      const response = await axios.post(
        `http://127.0.0.1:8000/resources/${id}/summarize/`
      );

      if (response.data.status === 'success') {
        setSummary(response.data.summary);
      } else {
        throw new Error(response.data.error || 'Failed to generate summary');
      }
    } catch (error) {
      console.error('Error generating summary:', error);
      alert(error.response?.data?.error || 'Failed to generate summary');
    } finally {
      setSummarizing(false);
    }
  };

  const getVideoUrl = (videoPath) => {
    if (!videoPath) return null;
    return videoPath.startsWith('http') ? videoPath : `http://localhost:8000${videoPath}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-50 to-blue-100">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  if (error || !lecture) {
    return (
      <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-50 to-blue-100">
        <div className="bg-white p-8 rounded-2xl shadow-xl text-center">
          <p className="text-xl text-red-500 font-medium mb-4">{error || 'Lecture not found.'}</p>
          <button
            onClick={() => window.history.back()}
            className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all duration-300"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 p-8">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => window.history.back()}
          className="flex items-center text-blue-600 hover:text-blue-700 mb-6 group"
        >
          <ArrowLeft className="mr-2 transform group-hover:-translate-x-1 transition-transform duration-300" />
          <span>Back to Lectures</span>
        </button>

        {showAlert && (
          <div className="fixed top-4 right-4 bg-red-500 text-white px-6 py-4 rounded-xl shadow-lg flex items-center space-x-3 animate-bounce">
            <Bell className="h-6 w-6" />
            <span>Alert: You seem tired! Take a break.</span>
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-xl overflow-hidden mb-8">
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">{lecture.title}</h1>
            <p className="text-gray-500">
              Uploaded on: {new Date(lecture.created_at).toLocaleDateString()}
            </p>
          </div>

          <div className="flex flex-col lg:flex-row gap-8 p-6">
            <div className="lg:w-3/5 space-y-6">
              <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg">
                {lecture?.lecture ? (
                  <video
                    key={getVideoUrl(lecture.lecture)}
                    controls
                    className="w-full aspect-video"
                    preload="metadata"
                    controlsList="nodownload"
                  >
                    <source src={getVideoUrl(lecture.lecture)} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <div className="w-full aspect-video flex items-center justify-center text-gray-400">
                    No video available
                  </div>
                )}
              </div>

              <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg p-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-white text-lg font-semibold">Fatigue Detection</h3>
                  <button
                    onClick={toggleCamera}
                    className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                      cameraEnabled ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
                    } text-white transition-colors`}
                  >
                    <Camera className="h-5 w-5" />
                    <span>{cameraEnabled ? 'Stop Camera' : 'Start Camera'}</span>
                  </button>
                </div>
                {cameraEnabled && (
                  <div className={`transition-opacity duration-300 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full rounded-lg"
                    />
                    <div className={`mt-2 px-3 py-1 rounded-lg inline-flex items-center ${
                      detectionStatus === 'Awake' ? 'bg-green-500' : 'bg-red-500'
                    } text-white`}>
                      <span>Status: {detectionStatus}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:w-2/5 space-y-6">
              <div className="bg-blue-50 rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Resources</h2>
                {lecture?.file1 && (
                  <button
                    onClick={() => handleDownload('file1', `${lecture.title}_resource1.pdf`)}
                    className="w-full bg-white text-gray-700 px-4 py-3 rounded-xl hover:bg-gray-50 transition-all duration-300 flex items-center justify-between shadow-sm mb-3"
                  >
                    <div className="flex items-center">
                      <FileText className="mr-3 text-blue-600" />
                      <span className="font-medium">Lecture Notes</span>
                    </div>
                    <Download className="text-blue-600" />
                  </button>
                )}

                <button
                  onClick={summarise}
                  disabled={summarizing}
                  className={`w-full bg-blue-600 text-white px-4 py-3 rounded-xl hover:bg-blue-700 transition-all duration-300 flex items-center justify-between shadow-md ${
                    summarizing ? 'opacity-75 cursor-not-allowed' : ''
                  }`}
                >
                  <span className="font-medium">
                    {summarizing ? 'Generating Summary...' : 'Generate Summary'}
                  </span>
                  {summarizing ? (
                    <RefreshCw className="animate-spin" />
                  ) : (
                    <RefreshCw />
                  )}
                </button>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Lecture Summary</h2>
                {summarizing ? (
                  <div className="flex items-center justify-center h-32 text-gray-500">
                    <RefreshCw className="animate-spin mr-2" />
                    <span>Generating summary...</span>
                  </div>
                ) : (
                  <div className="prose max-w-none">
                    <p className="text-gray-600">
                      {summary || 'Click "Generate Summary" to create a summary of this lecture.'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LectureDetailPage;