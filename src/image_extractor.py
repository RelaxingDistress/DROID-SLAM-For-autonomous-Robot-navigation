import cv2
import os

def extract_images(video_path, output_folder, frame_interval=1):
    """
    Extracts frames from a video file and saves them as images.

    Parameters:
        video_path (str): Path to the input video file.
        output_folder (str): Folder where the extracted images will be saved.
        frame_interval (int): Save every nth frame (default is 1, i.e., save every frame).
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break  # End of video

        # Save every nth frame
        if frame_count % frame_interval == 0:
            image_path = os.path.join(output_folder, f"frame_{frame_count:05d}.jpg")
            cv2.imwrite(image_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Extraction complete. {saved_count} frames saved to '{output_folder}'.")

