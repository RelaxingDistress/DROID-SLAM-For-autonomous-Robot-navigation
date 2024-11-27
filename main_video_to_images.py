from src.image_extract import extract_images

def main():

  # Specify the video name
  video_file = 'data/videos/dog_video.mp4'
  output_dir = 'data/images'

  # Extract the frames to data/images
  extract_images(video_file, output_dir, frame_interval=1)

if __name__ == '__main__':
  main()
