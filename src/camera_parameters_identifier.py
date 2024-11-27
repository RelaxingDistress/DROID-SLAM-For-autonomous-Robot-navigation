# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

import os
import cv2
import numpy as np

def process_checkerboards(image_dir):
    """
    Process images in the directory to extract camera parameters based on checkerboard detection.

    Args:
        image_dir (str): Path to the directory containing checkerboard images.

    Returns:
        dict: A dictionary containing camera parameters (fx, fy, cx, cy).
    """
    # Termination criteria for corner refinement
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Checkerboard dimensions (customize these based on your checkerboard)
    checkerboard_size = (9, 6)  # 9x6 internal corners
    square_size = 25  # Size of a square in mm (customize based on your checkerboard)

    # Prepare 3D points in real-world space
    objp = np.zeros((checkerboard_size[0] * checkerboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:checkerboard_size[0], 0:checkerboard_size[1]].T.reshape(-1, 2)
    objp *= square_size

    # Arrays to store object points and image points
    objpoints = []  # 3D points in real-world space
    imgpoints = []  # 2D points in image plane

    # Process each image in the directory
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)
        image = cv2.imread(image_path)
        if image is None:
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect the checkerboard corners
        ret, corners = cv2.findChessboardCorners(gray, checkerboard_size, None)
        if ret:
            objpoints.append(objp)

            # Refine corner positions
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    # Perform camera calibration
    if len(objpoints) < 1 or len(imgpoints) < 1:
        raise ValueError("Not enough checkerboard patterns detected for calibration.")

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    # Extract camera parameters
    fx = mtx[0, 0]  # Focal length in x-direction
    fy = mtx[1, 1]  # Focal length in y-direction
    cx = mtx[0, 2]  # Principal point x-coordinate
    cy = mtx[1, 2]  # Principal point y-coordinate

    return {'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy}

