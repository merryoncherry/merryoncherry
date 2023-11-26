import os
import subprocess

def normalize_audio(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.m4a')):  # Add other file types if needed
                file_path = os.path.join(root, file)
                file_name, file_extension = os.path.splitext(file_path)

                # Command to normalize audio - you can adjust ffmpeg parameters as needed
                temp_output = f"{file_name}_normalized{file_extension}"
                cmd = f'ffmpeg -i "{file_path}" -af loudnorm=I=-16:LRA=11:TP=-1.5 "{temp_output}"'
                subprocess.run(cmd, shell=True)

                # Replace original file
                os.replace(temp_output, file_path)


# Replace 'your_directory_path' with the path to your top-level directory
normalize_audio("c:\\Users\\Chuck\\Documents\\xlightsShows\\Collection\\Import")

