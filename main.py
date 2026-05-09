import pandas as pd
from ultralytics import YOLO
import cv2

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video
video_path = "input/input.mp4"
cap = cv2.VideoCapture(video_path)

# Save output video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

out = cv2.VideoWriter(
    'output/output.mp4',
    fourcc,
    30,
    (int(cap.get(3)), int(cap.get(4)))
)

# Create empty list
shot_data = []

# Variables for shot classification
previous_ball_x = None
shot_type = "Unknown"

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Detect only persons and sports ball
    results = model.track(frame, persist=True, classes=[0, 32])

    # Draw detections
    annotated_frame = results[0].plot()

    # Ball movement logic
    for box in results[0].boxes:

        cls = int(box.cls[0])

        # Sports ball class
        if cls == 32:

            x1, y1, x2, y2 = box.xyxy[0]

            ball_x = int((x1 + x2) / 2)

            if previous_ball_x is not None:

                movement = abs(ball_x - previous_ball_x)

                if movement > 80:
                    shot_type = "Smash"

                elif movement > 40:
                    shot_type = "Forehand"

                else:
                    shot_type = "Backhand"

            previous_ball_x = ball_x

    # Show shot label
    cv2.putText(
        annotated_frame,
        f"Shot: {shot_type}",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Frame number
    frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    # Save CSV data
    shot_data.append({
        "frame": frame_number,
        "shot_type": shot_type
    })

    # Show video
    cv2.imshow("YOLO Tracking", annotated_frame)

    # Save video
    out.write(annotated_frame)

    # Quit button
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release everything
cap.release()
out.release()
cv2.destroyAllWindows()

# Save CSV
df = pd.DataFrame(shot_data)
df.to_csv("output/shot_analysis.csv", index=False)

print("CSV file saved successfully!")