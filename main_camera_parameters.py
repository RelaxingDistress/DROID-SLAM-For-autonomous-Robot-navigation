from src.camera_parameters_identifier import process_checkerboards
from src.image_extractor import extract_images

import numpy as np
import os

def main():
    # Specify the video name and output directory
    video_file = 'C:\Users\mangl\OneDrive\Desktop\Navigator_project\Data\checkerboardVideo.mp4'
    output_dir = 'C:\Users\mangl\OneDrive\Desktop\Navigator_project\Data\checkerboard'
    output_file = os.path.join(output_dir, 'camera_parameters.txt')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Extract the frames to data/images
    print(f"Extracting images from {video_file} to {output_dir}...")
    extract_images(video_file, output_dir, frame_interval=1)

    # Run the camera parameter algorithm
    print("Processing checkerboards to identify camera parameters...")
    camera_parameters = process_checkerboards(output_dir)

    # Validate that camera parameters include the expected values
    if not all(key in camera_parameters for key in ['fx', 'fy', 'cx', 'cy']):
        raise ValueError("Camera parameters must include 'fx', 'fy', 'cx', and 'cy'.")

    # Extract only the desired parameters
    fun_params = [camera_parameters['fx'], camera_parameters['fy'], 
                  camera_parameters['cx'], camera_parameters['cy']]

    # Save the parameters to a text file
    print(f"Saving camera parameters to {output_file}...")
    np.savetxt(output_file, [fun_params], header='fx, fy, cx, cy', fmt='%.6f')
    print("Camera parameters saved successfully!")

if __name__ == '__main__':
    main()
