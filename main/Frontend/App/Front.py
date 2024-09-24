# Frontend code for the Streamlit web application
import streamlit as st
import requests
from PIL import Image
import io
import cv2
import time
import tempfile
import os

# Backend URLs
IMAGE_BACKEND_URL = "http://127.0.0.1:5000"
VIDEO_BACKEND_URL = "http://127.0.0.1:5001"

# Streamlit app title
st.title("Car Detection Model - Overview, Demo, and Team")

# Create tabs for Homepage, Project Demo, and About Us
tab1, tab2, tab3 = st.tabs(["Project Overview", "Car Detection Demo", "About Us"])

# --------------- HOMEPAGE (Project Overview) ---------------
with tab1:
    st.header("Car Detection Model Overview")
    st.write("""
    The Car Detection Model project focuses on developing an AI-powered system capable of accurately detecting cars in images and videos.
    By using state-of-the-art deep learning techniques, such as the YOLOv9 algorithm, the model is optimized for real-time performance.
    This project has wide applications including traffic monitoring, autonomous vehicles, and security systems.
    """)

    st.subheader("Project Methodology")
    st.write("""
    The key stages of the project:
    1. **Data Collection and Preprocessing**: We collected and annotated a large dataset of car images using Roboflow.
    2. **Model Training**: YOLOv9 was trained on these images for car detection with high accuracy.
    3. **Evaluation and Refinement**: We evaluated the model on test datasets to improve precision, recall, and general performance.
    4. **Deployment**: The model was deployed using Roboflow's API for real-time detection applications.
    """)

    st.subheader("Try the Car Detection Model")
    st.write("You can upload an image or video to see the car detection model in action in the next tab.")

# --------------- PROJECT DEMO (Car Detection) ---------------
# --------------- PROJECT DEMO (Car Detection) ---------------
with tab2:
    st.header("Car Detection Demo")

    # Create tabs for Image and Video upload
    demo_tab1, demo_tab2 = st.tabs(["Image Upload", "Video Upload"])

    # --------------- IMAGE UPLOAD TAB ---------------
    with demo_tab1:
        st.subheader("Upload and Process an Image")
        st.write("Click the button below to go to the image upload page.")
        if st.button("Go to Image Upload"):
            st.markdown('<a href="http://localhost:8503" target="_blank">Open Image Upload</a>', unsafe_allow_html=True)

    # --------------- VIDEO UPLOAD TAB ---------------
    with demo_tab2:
        st.subheader("Upload and Process a Video")
        st.write("Click the button below to go to the video upload page.")
        if st.button("Go to Video Upload"):
            st.markdown('<a href="http://localhost:8504" target="_blank">Open Video Upload</a>', unsafe_allow_html=True)

# --------------- ABOUT US ---------------
with tab3:
    st.header("About Us")

    st.write("""
    This project was developed by a group of students from Auro University as part of their BSc in Information Technology (IT) program.
    Our goal was to develop a cutting-edge car detection model that can be used for real-time applications.
    """)

    st.subheader("Meet the Team")
    st.write("""
    - **Ayush Golakiya** (212022015)
    - **Hiteeka Prajapati** (212022064)
    - **Mahendra Leva** (212022072)
    - **Arinn Choksi** (212022027)
    """)

    st.subheader("Supervision")
    st.write("""
    The project was guided by **Ms. Juhi Khenger**, who provided valuable feedback and direction throughout the project development process.
    """)

    st.subheader("Acknowledgements")
    st.write("""
    We would like to thank Auro University for providing the necessary resources and support to make this project possible.
    """)


