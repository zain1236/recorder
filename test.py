# import psutil
# import os
# import time
#
# def check_process_running(name):
#     for p in psutil.process_iter():
#         if p.name() == name:
#             return True
#     return False
#
#
#
# while True:
#     if not check_process_running('optimizev3.exe'):
#         exe_path = os.path.join(os.path.expanduser("~"),'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\optimizev3.exe')
#         os.startfile(exe_path)
#         print("Started again")
#         time.sleep(5)
import os
import soundfile as sf
from pydub import AudioSegment


input_file = '10747_26_05_2023_20_02_49.wav'
output_file = input_file.split('.')[0] + '.mp3'
AudioSegment.from_wav(input_file).export(output_file, format="mp3")

# # Append-adds at last
# output_file = input_file.split('.')[0] + ".flac"
# target_compression = 'FLAC'
# target_compression_subtype = 'PCM_S8'
#
# output_path = "Final_Upload"
# output_path = os.path.join(output_path, foldername)
# if not os.path.exists(output_path):
#     os.mkdir(output_path)
#
# output_file_path = os.path.join(output_path, output_file)
#
# audio, sample_rate = sf.read(input_file_path)
# sf.write(output_file_path, audio, sample_rate, subtype=target_compression_subtype, format=target_compression)

