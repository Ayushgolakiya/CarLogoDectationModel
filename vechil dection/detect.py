from ultralytics import YOLO

# Load a COCO-pretrained YOLOv8 model
model = YOLO("yolov8s.pt")

# Display model information (optional)
model.info()

# Run inference with the YOLOv8 model on the 'bus.jpg' image
results = model("bus.jpg")

# Define the COCO class ID for cars (usually 2)
car_class_id = 2

# Process each result
for result in results:
    # Extract bounding boxes, class IDs, and confidences
    boxes = result.boxes
    class_names = result.names

    # Iterate through detected boxes
    for box in boxes:
        # Get class ID as an integer
        class_id = int(box.cls.item())  # Convert tensor to integer

        # Check if the detected class is a car
        if class_id == car_class_id:
            # Convert tensors to native Python types
            confidence = box.conf.item()  # Convert tensor to float
            bbox = box.xyxy.tolist()  # Convert tensor to list

            # Print the detection details
            print(f"Class: {class_names[class_id]}, Confidence: {confidence:.2f}, BBox: {bbox}")
