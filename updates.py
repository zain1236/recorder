# import requests
# from tqdm import tqdm
# import os
# import datetime
# def download_file(url, output_path):
#     response = requests.get(url, stream=True)
#     total_size = int(response.headers.get('content-length', 0))
#
#     with open(output_path, 'wb') as file:
#         progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)
#
#         for chunk in response.iter_content(chunk_size=1024):
#             if chunk:
#                 file.write(chunk)
#                 progress_bar.update(len(chunk))
#
#         progress_bar.close()
#
# # Example usage
# url = 'http://182.180.54.158:10202/updatedfile'
# output_path = 'optimizev3.exe'
#
# # download_file(url, output_path)
# modification_time = os.path.getmtime(output_path)
# print(modification_time)
# modification_datetime = datetime.datetime.fromtimestamp(modification_time)
#
# print(f"Modification time: {modification_datetime}")

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
from tqdm import tqdm
import threading

def download_file_with_progress(url, output_path, progress_var):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # Adjust the block size as per your preference

    with open(output_path, 'wb') as file:
        downloaded_size = 0

        for data in response.iter_content(block_size):
            file.write(data)
            downloaded_size += len(data)
            progress = int((downloaded_size / total_size) * 100)
            progress_var.set(progress)


def download_button_clicked():
    url = "http://182.180.54.158:10202/updatedfile"  # Replace with your download URL
    output_path = "optimize.exe"  # Replace with the desired output file path

    progress_var.set(0)  # Reset progress bar

    # Start the download in a separate thread
    download_thread = threading.Thread(target=download_file_with_progress, args=(url, output_path, progress_var))
    download_thread.start()


update_window = tk.Tk()
update_window.title("Download Progress")
update_window.geometry("300x100")

# Create a progress bar
percentage_label = tk.Label(update_window, text="0%")
percentage_label.pack(pady=20)
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(update_window, variable=progress_var, length=200)
progress_bar.pack()

# Create a download button
download_button = tk.Button(update_window, text="Download", command=download_button_clicked)
download_button.pack()

update_window.mainloop()
