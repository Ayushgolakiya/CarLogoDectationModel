import os
import hashlib
from flask import Flask, request, jsonify, send_from_directory
import cv2
import numpy as np
from roboflow import Roboflow
import supervision as sv
from functools import lru_cache
import re
app = Flask(__name__)

# Define directories
UPLOAD_FOLDER = 'Video_dataset/unanotated_video'
ANNOTATED_FOLDER = 'Video_dataset/anotated_video'
VIDEO_DATA_FOLDER = 'Video_dataset/video_data'
COUNTER_FILE = 'Video_dataset/counter.txt'

# Create directories if they do not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(ANNOTATED_FOLDER, exist_ok=True)
os.makedirs(VIDEO_DATA_FOLDER, exist_ok=True)

# Roboflow configuration
API_KEY = "1d4cXMkWZ3y3bGTQZrk7"
PROJECT_NAME = "car_logo_detection_model"
VERSION = 3

@lru_cache(maxsize=1)
def load_roboflow_model():
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace().project(PROJECT_NAME)
    return project.version(VERSION).model

def calculate_hash(file_path):
    """Generate a SHA-256 hash for a given video file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_next_counter_value():
    """Read and update the counter value from the text file."""
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'w') as f:
            f.write("0")
    
    with open(COUNTER_FILE, 'r') as f:
        counter = int(f.read().strip())
    
    # Update counter
    new_counter = counter + 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(new_counter))

    return new_counter
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Clean the filename
    filename = clean_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Generate hash for the uploaded video
    video_hash = calculate_hash(file_path)
    hash_file_path = os.path.join(VIDEO_DATA_FOLDER, f"{video_hash}.txt")

    try:
        # Check if the hash exists in the video_data folder
        if os.path.exists(hash_file_path):
            # The video has already been processed, retrieve the annotated video
            counter = get_counter_from_hash(video_hash)
            annotated_video_path = os.path.join(ANNOTATED_FOLDER, f"annotated_{counter}.avi")
            
            if os.path.exists(annotated_video_path):
                # Return the existing annotated video
                return jsonify({
                    'message': 'File already processed', 
                    'filename': os.path.basename(annotated_video_path)
                }), 200
            else:
                # Log a more descriptive error if the annotated video is missing
                return jsonify({'error': f'Annotated video not found for counter {counter}'}), 500
        else:
            # Hash does not exist, process video through Roboflow and save
            try:
                # Get the next counter value for new files
                counter = get_next_counter_value()

                # Annotate the video
                annotated_video_path = annotate_video(file_path, counter)

                # Save the hash in the video_data folder
                with open(hash_file_path, 'w') as f:
                    f.write(str(counter))  # Save the counter associated with this hash

                return jsonify({
                    'message': 'File processed successfully', 
                    'filename': os.path.basename(annotated_video_path)
                }), 200
            except Exception as e:
                # Add more detailed logging for the error during processing
                return jsonify({'error': f'Error during video annotation: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error retrieving or processing file: {str(e)}'}), 500

@app.route('/video/<filename>', methods=['GET'])
def get_annotated_video(filename):
    return send_from_directory(ANNOTATED_FOLDER, filename)

def clean_filename(filename):
    """Remove special characters and emojis from the filename."""
    sanitized_name = re.sub(r'[^\w_.-]', '_', filename)
    return sanitized_name.strip('_')

def annotate_video(input_path, counter):
    """Annotate the video using the Roboflow model and save the annotated video."""
    model = load_roboflow_model()

    # Run inference on the video file
    job_id, signed_url, expire_time = model.predict_video(
        input_path,
        fps=5,
        prediction_type="batch-video",
    )

    # Poll for results until video inference is complete
    results = model.poll_until_video_results(job_id)

    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    tracker = sv.ByteTrack()

    def annotate_frame(frame: np.ndarray, frame_number: int) -> np.ndarray:
        try:
            time_offset = frame_number / frame_rate
            closest_time_offset = min(results['time_offset'], key=lambda t: abs(t - time_offset))
            index = results['time_offset'].index(closest_time_offset)
            detection_data = results[PROJECT_NAME][index]

            roboflow_format = {
                "predictions": detection_data['predictions'],
                "image": {"width": frame.shape[1], "height": frame.shape[0]}
            }

            detections = sv.Detections.from_inference(roboflow_format)
            detections = tracker.update_with_detections(detections)

            labels = [pred['class'] for pred in detection_data['predictions']]
            labels = labels[:len(detections)]  # Adjust labels to match the number of detections

        except (IndexError, KeyError, ValueError) as e:
            detections = sv.Detections(xyxy=np.empty((0, 4)),
                                       confidence=np.empty(0),
                                       class_id=np.empty(0, dtype=int))
            labels = []

        annotated_frame = frame.copy()
        if len(detections) > 0:
            annotated_frame = box_annotator.annotate(annotated_frame, detections=detections)
            annotated_frame = label_annotator.annotate(annotated_frame, detections=detections, labels=labels)

        return annotated_frame

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video at {input_path}")

    global frame_rate
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    annotated_output_path = os.path.join(ANNOTATED_FOLDER, f'annotated_{counter}.avi')
    out = cv2.VideoWriter(annotated_output_path, cv2.VideoWriter_fourcc(*'XVID'), frame_rate, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        annotated_frame = annotate_frame(frame, frame_number)
        out.write(annotated_frame)

    cap.release()
    out.release()

    return annotated_output_path

def get_counter_from_hash(video_hash):
    """Retrieve the counter value from the hash file."""
    hash_file_path = os.path.join(VIDEO_DATA_FOLDER, f"{video_hash}.txt")
    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as f:
            return f.read().strip()
    else:
        raise Exception("Hash not found")

if __name__ == '__main__':
    app.run(debug=False,port=5001)
