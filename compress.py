import soundfile as sf
import os




def compress_file(path,input_file):
    try:
        file_path = os.path.join(path,input_file)

        output_file = input_file.split('.')[0] + ".flac"
        target_compression = 'FLAC'
        target_compression_subtype = 'PCM_S8'
        output_file_path = os.path.join(path,output_file)
        audio, sample_rate = sf.read(file_path)
        sf.write(output_file_path, audio, sample_rate, subtype=target_compression_subtype, format=target_compression)
        os.remove(file_path)
        print("done",input_file)
    except Exception as e:
        print("error",path,input_file,e)

UPLOAD_DIRECTORY = 'uploads'

folders = os.listdir(UPLOAD_DIRECTORY)
for folder in folders:
    folder_path = os.path.join(UPLOAD_DIRECTORY,folder)
    files = os.listdir(folder_path)
    for file in files:
        compress_file(folder_path,file)