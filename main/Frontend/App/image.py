# this is for uploading image and displaying the annotated image

import streamlit as st
import requests
from PIL import Image
import io

# Streamlit frontend
st.title("Car Logo Detection")

# Upload image
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_image is not None:
    # Display original image
    st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)

    # Send image to backend
    with st.spinner('Processing...'):
        files = {'image': uploaded_image}
        response = requests.post("http://127.0.0.1:5000/upload-image", files=files)

    if response.status_code == 200:
        # Receive and display the annotated image
        annotated_image = Image.open(io.BytesIO(response.content))
        st.image(annotated_image, caption='Annotated Image with Bounding Boxes', use_column_width=True)

    else:
        st.error("Error occurred while processing the image.")
