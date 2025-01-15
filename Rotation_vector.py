import numpy as np
from plyfile import PlyData, PlyElement
import open3d as o3d
import os

# Step 1: Mount Google Drive and Load the PLY File
from google.colab import drive
drive.mount('/content/drive')

# Define paths
drive_ply_file = "/content/drive/My Drive/massrobotics.ply"  # Replace with your Google Drive PLY file path
local_ply_file = "./massrobotics.ply"
output_file = "./aligned_floor.ply"

# Copy the file from Google Drive to the working directory
if not os.path.exists(drive_ply_file):
    raise FileNotFoundError(f"File not found in Google Drive: {drive_ply_file}")

!cp "$drive_ply_file" "$local_ply_file"
print(f"Copied PLY file from Google Drive: {drive_ply_file}")

# Load the .ply file
ply_data = PlyData.read(local_ply_file)

# Extract vertex data (x, y, z coordinates)
vertices = np.array([ply_data['vertex'][axis] for axis in ['x', 'y', 'z']]).T

# Extract face data (triangles)
faces = np.array([list(face[0]) for face in ply_data['face']['vertex_indices']])

print(f"Loaded {len(vertices)} vertices and {len(faces)} faces from the PLY file.")

# Step 2: Compute Triangle Normals
def compute_triangle_normals(vertices, faces):
    normals = []
    for face in faces:
        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        normal = np.cross(v2 - v1, v3 - v1)  # Cross product to compute normal
        normal = normal / np.linalg.norm(normal)  # Normalize the vector
        normals.append(normal)
    return np.array(normals)

# Calculate normals for all triangles
normals = compute_triangle_normals(vertices, faces)
print(f"Computed normals for {len(normals)} triangles.")

# Step 3: Identify Floor Triangles
# Identify triangles whose normals are nearly parallel to Z-axis
floor_faces = []
floor_normals = []

for i, normal in enumerate(normals):
    # Check if the normal is roughly parallel to [0, 0, 1] (Z-axis)
    if np.isclose(normal[2], 1, atol=0.1):  # Adjust tolerance as needed
        floor_faces.append(faces[i])
        floor_normals.append(normal)

floor_faces = np.array(floor_faces)
floor_normals = np.array(floor_normals)

print(f"Identified {len(floor_faces)} floor triangles.")

# Step 4: Calculate Rotation Vector and Angle
# Compute the average floor normal vector
average_normal = np.mean(floor_normals, axis=0)
average_normal = average_normal / np.linalg.norm(average_normal)  # Normalize

# Calculate rotation axis (cross product with [0, 0, 1])
rotation_axis = np.cross(average_normal, [0, 0, 1])
rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)  # Normalize

# Calculate rotation angle
rotation_angle = np.arccos(np.dot(average_normal, [0, 0, 1]))

print(f"Rotation Axis: {rotation_axis}")
print(f"Rotation Angle (radians): {rotation_angle}")

# Step 5: Apply Rotation
def rotation_matrix(axis, angle):
    axis = axis / np.linalg.norm(axis)
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    ux, uy, uz = axis
    return np.array([
        [cos_theta + ux**2 * (1 - cos_theta), ux*uy*(1 - cos_theta) - uz*sin_theta, ux*uz*(1 - cos_theta) + uy*sin_theta],
        [uy*ux*(1 - cos_theta) + uz*sin_theta, cos_theta + uy**2 * (1 - cos_theta), uy*uz*(1 - cos_theta) - ux*sin_theta],
        [uz*ux*(1 - cos_theta) - uy*sin_theta, uz*uy*(1 - cos_theta) + ux*sin_theta, cos_theta + uz**2 * (1 - cos_theta)]
    ])

# Create rotation matrix
rotation_mat = rotation_matrix(rotation_axis, rotation_angle)

# Apply rotation to all vertices
rotated_vertices = vertices @ rotation_mat.T
print("Applied rotation to align floor triangles with XY plane.")

# Step 6: Save the Rotated PLY File
def save_ply(vertices, faces, output_file):
    # Create Open3D PointCloud object
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(vertices)

    # Save the point cloud
    o3d.io.write_point_cloud(output_file, point_cloud)

    print(f"Saved rotated PLY file to: {output_file}")

save_ply(rotated_vertices, faces, output_file)

# Step 7: Push the Rotated File to GitHub (Optional)
!git config --global user.name "RelaxingDistress"  # Replace with your GitHub username
!git config --global user.email "mvijla23@gmail.com.com"  # Replace with your GitHub email
!git clone https://github.com/RelaxingDistress/DROID-SLAM-For-autonomous-Robot-navigation.git
!mv "$output_file" DROID-SLAM-For-autonomous-Robot-navigation/  # Move the file to your GitHub repository
%cd DROID-SLAM-For-autonomous-Robot-navigation
!git add aligned_floor.ply
!git commit -m "Added aligned PLY file"
!git push
