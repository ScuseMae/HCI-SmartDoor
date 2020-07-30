import time
from datetime import datetime
import sqlite3
import face_recognition
import cv2
import os
import subprocess
import paho.mqtt.client as mqtt
from pushjack import APNSSandboxClient


def send_notification():
    client = APNSSandboxClient(certificate='Path to Apple iOS Push Service Notification Certificate',
                               default_error_timeout=10,
                               default_expiration_offset=2592000,
                               default_batch_size=100,
                               default_retries=5)
    token = 'DeviceToken#'
    alert = 'Hello world.'

    # Send to a single device (keyword args optional)
    res = client.send(token,
                      alert,
                      badge=1,
                      sound='default',
                      content_available=True,
                      title='Title')

    # List of all tokens sent.
    print(res.tokens)
    # List of errors as APNSServerError objects
    print(res.errors)
    # Dict mapping errors as token => APNSServerError object.
    print(res.token_errors)


# Get a reference to webcam
video_capture = cv2.VideoCapture(0)

# load sample picture & learn how to recognize it
sample_image = face_recognition.load_image_file("jobs.jpg")
sample_image_encoding = face_recognition.face_encodings(sample_image)[0]

# load 2nd sample image & learn how to recognize it
sample_2_image = face_recognition.load_image_file("zucks.jpg")
sample_2_image_encoding = face_recognition.face_encodings(sample_2_image)[0]

# Create arrays of known face encodings & their names
known_face_encodings = [
    sample_image_encoding,
    sample_2_image_encoding
]

known_face_names = [
    "jobs",
    "zucks"
]

# Optional if time
unknown_face_names = []
blocked_face_names = []

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# seconds & counter variables
seconds = 5
counter = 0
has_been_called = False
open_stream = None

while True:

    # Grab a single video frame
    ret, frame = video_capture.read()

    # Resize video frame to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (OpenCV setting) to RGB color (face_recognition setting)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all faces & encodings in current video frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # See if face matches known face
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown..."

            # If match made in known_face_encodings, just use first one
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

                # if faceRecognized equals specified person, do action
                if counter > 60:
                    if not has_been_called:
                        if name == "known_face_name":
                            print('known_face_name')
                            has_been_called = True
                            # Send Apple Push Notification
                            send_notification()
                            # Connect to MQTT
                            client = mqtt.Client()
                            # Specify IP Address, port, etc.
                            client.connect("IpAddress", 1883, 60)
                            # Publish actuator action
                            client.publish("rpi/gpio", "on")
                            client.disconnect()
                            # global open_stream
                            # Open up http stream (correct/best way to do this??)
                            open_stream = subprocess.Popen(
                                ['python3', 'Path to Stream_2/main.py'],
                                shell=False)
                            # exit()
                face_names.append(name)

    process_this_frame = not process_this_frame

    # Display results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display resulting image
    cv2.imshow('Video', frame)

    # Counter Increment, name has_been_called?, count to slow recognition time/close application?
    counter += 1

    # Hit 'q' on keyboard to quit application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

# Terminate SubProcess (nice way?)
pid = open_stream.pid
open_stream.terminate()
try:
    os.kill(pid, 0)
    open_stream.kill()
    print('Force Killed Process')
except OSError as e:
    print('Terminated Gently...')
