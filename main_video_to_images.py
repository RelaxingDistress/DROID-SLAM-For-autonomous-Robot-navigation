from src.image_extract import extract_frames

def main():

  # Specify the video name
  video_filename = 'data/videos/test.MOV'
  image_output_path = 'data/images'

  # Extract the frames to data/images
  extract_frames(video_filename, image_output_path)

if __name__ == '__main__':
  main()
