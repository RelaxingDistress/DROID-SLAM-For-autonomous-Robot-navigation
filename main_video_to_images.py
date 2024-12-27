from src.image_extractor import extract_images

def main():

  # Specify the video name
  video_name = 'dog_video'
  video_file = f'data/videos/{video_name}.mp4'
  output_dir = f'data/{video_name}/rgb'

  # Extract the frames to data/images
  extract_images(video_file, output_dir, frame_interval=10)

if __name__ == '__main__':
  main()
