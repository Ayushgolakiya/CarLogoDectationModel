# This script is used to upload a video file to the frontend and display it in the browser. The video is then sent to the backend for processing and the annotated video is fetched and displayed in the frontend. The video can be played back in the browser using OpenCV and Streamlit.
import streamlit as st
import requests
import cv2
import time
import tempfile
import os

# Backend URL
BACKEND_URL = "http://127.0.0.1:5001"

st.title("Video Upload and Display")

# Initialize session state for video playback
if 'playback_state' not in st.session_state:
    st.session_state.playback_state = False
if 'video_path' not in st.session_state:
    st.session_state.video_path = None

# Upload video to frontend
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Show the uploaded video in the frontend
    st.video(uploaded_file)

    # Add an upload button to trigger the backend upload
    if st.button("Upload Video"):
        with st.spinner("Uploading and processing the video..."):
            # Send the file to the backend directly from memory
            files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/upload", files=files)

            if response.status_code == 200:
                st.success("File uploaded and processed successfully")
                filename = response.json().get('filename')

                # Fetch the annotated video from the backend
                video_url = f"{BACKEND_URL}/video/{filename}"
                video_response = requests.get(video_url)

                if video_response.status_code == 200:
                    # Save the fetched video temporarily
                    temp_video_path = os.path.join(tempfile.gettempdir(), filename)
                    with open(temp_video_path, 'wb') as f:
                        f.write(video_response.content)

                    # Store the video path in session state
                    st.session_state.video_path = temp_video_path

                else:
                    st.error("Failed to fetch the video from the backend")
            else:
                st.error("Failed to upload and process the file")

# Only show the Play button if a video is available
if st.session_state.video_path:
    if st.button('Play'):
        # Toggle playback state
        st.session_state.playback_state = True

# Playback logic
if st.session_state.playback_state and st.session_state.video_path:
    # Open the video using OpenCV
    cap = cv2.VideoCapture(st.session_state.video_path)

    if not cap.isOpened():
        st.error('Error: Could not open video.')

    # Get the frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1 / fps  # Calculate delay between frames

    # Streamlit video playback
    stframe = st.empty()  # Placeholder for the video frames

    # Loop through the video frames
    while cap.isOpened():
        ret, frame = cap.read()  # Read a frame from the video
        if not ret:
            break  # Break if there are no more frames

        # Convert the frame to RGB (OpenCV uses BGR by default)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Display the frame in Streamlit
        stframe.image(frame, channels='RGB')

        # Add a delay to match the frame rate
        time.sleep(frame_delay)

    # Release the video capture object
    cap.release()

    # Reset playback state after video ends
    st.session_state.playback_state = False
