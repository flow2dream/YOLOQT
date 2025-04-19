import os

def get_image_paths(folder_path, image_extensions):
    image_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in image_extensions:
                image_paths.append({"path":os.path.join(root, file), "image":None})

    return image_paths