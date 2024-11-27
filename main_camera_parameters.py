from src.image_extractor import extract_images

import numpy as np

def main():

  # Specify the video name
  video_file = 'data/videos/checkerboard.mp4'
  output_dir = 'data/checkerboard'

  # Extract the frames to data/images
  extract_images(video_file, output_dir, frame_interval=1)

  # Run the camera parameter algorithm
  camera_parameters = process_checkerboards(output_dir)

  # Save the camera parameters
  np.savetxt(camera_parameters)

if __name__ == '__main__':
  main()

