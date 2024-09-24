# This is the backend code for the image handling
import os
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageDraw, ImageFont
from roboflow import Roboflow
import hashlib
import io
from model import Roboflow_model as model

app = Flask(__name__)

# Paths (everything is stored under image_dataset/)
BASE_FOLDER = 'image_dataset'
UPLOAD_FOLDER = os.path.join(BASE_FOLDER, 'image')
LABELS_FOLDER = os.path.join(BASE_FOLDER, 'labels')
HASH_FOLDER = os.path.join(BASE_FOLDER, 'hash')
COUNTER_FILE = os.path.join(BASE_FOLDER, 'Image_counter.txt')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(LABELS_FOLDER, exist_ok=True)
os.makedirs(HASH_FOLDER, exist_ok=True)

# Initialize counter
if not os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, 'w') as f:
        f.write('0')

def get_next_counter():
    with open(COUNTER_FILE, 'r+') as f:
        counter = int(f.read().strip())
        f.seek(0)
        f.write(str(counter + 1))
    return counter

def get_image_hash(image_path):
    """Compute MD5 hash for an image."""
    hash_md5 = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    file = request.files['image']
    
    # Save the uploaded image temporarily to compute its hash
    temp_image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(temp_image_path)

    # Compute the hash of the uploaded image
    uploaded_image_hash = get_image_hash(temp_image_path)

    # Check if the hash already exists in the hash directory
    for hash_file in os.listdir(HASH_FOLDER):
        with open(os.path.join(HASH_FOLDER, hash_file), 'r') as f:
            stored_hash = f.read().strip()
            if stored_hash == uploaded_image_hash:
                # Hash exists, retrieve existing image and label
                image_counter = hash_file.split('.')[0]
                existing_image_path = os.path.join(UPLOAD_FOLDER, f'image_{image_counter}.png')
                existing_label_path = os.path.join(LABELS_FOLDER, f'label_{image_counter}.txt')

                # Annotate the image using the existing label
                img = Image.open(existing_image_path)
                draw = ImageDraw.Draw(img)

                # Read the existing YOLO label and annotate the image
                with open(existing_label_path, 'r') as label_file:
                    for line in label_file:
                        class_id, x_center, y_center, width, height = map(float, line.strip().split())
                        image_width, image_height = img.size
                        left = (x_center - width / 2) * image_width
                        top = (y_center - height / 2) * image_height
                        right = (x_center + width / 2) * image_width
                        bottom = (y_center + height / 2) * image_height
                        draw.rectangle([left, top, right, bottom], outline="red", width=2)

                # Send the annotated image back to the frontend
                img_io = io.BytesIO()
                img.save(img_io, 'PNG')
                img_io.seek(0)
                return send_file(img_io, mimetype='image/png', as_attachment=False)

    # If no match is found, proceed with Roboflow prediction
    counter = get_next_counter()
    image_filename = f'image_{counter}.png'
    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
    os.rename(temp_image_path, image_path)

    # Send image to Roboflow for prediction
    prediction = model.predict(image_path).json()

    # Annotate the image using the prediction
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for pred in prediction['predictions']:
        x, y, width, height = pred['x'], pred['y'], pred['width'], pred['height']
        left = x - width / 2
        top = y - height / 2
        right = x + width / 2
        bottom = y + height / 2
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        
        # Write the class name above the rectangle
        class_name = pred['class']
        font = ImageFont.truetype("arial.ttf", 20)
        
        # Get the size of the text
        text_bbox = font.getbbox(class_name)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_position = (left, top - text_height - 5)  # Adjust the position as needed
        
        # Draw a filled rectangle for the text background
        draw.rectangle([text_position, (text_position[0] + text_width, text_position[1] + text_height)], fill="red")
        
        # Draw the text with white color
        draw.text(text_position, class_name, fill="white", font=font)

        # YOLO format: class_id, x_center, y_center, width, height (normalized)
        class_id = pred['class_id']
        image_width, image_height = img.size
        yolo_x_center = x / image_width
        yolo_y_center = y / image_height
        yolo_width = width / image_width
        yolo_height = height / image_height

        # Save YOLO label
        label_filename = f'label_{counter}.txt'
        label_path = os.path.join(LABELS_FOLDER, label_filename)
        with open(label_path, 'w') as f:
            f.write(f"{class_id} {yolo_x_center} {yolo_y_center} {yolo_width} {yolo_height}\n")

    # Save the hash of the new image
    with open(os.path.join(HASH_FOLDER, f'{counter}.txt'), 'w') as f:
        f.write(uploaded_image_hash)

    # Send the annotated image back to the frontend
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png', as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)