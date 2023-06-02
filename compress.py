import soundfile as sf
import os




def compress_file(path,foldername,input_file):
    try:
        input_file_path = os.path.join(path,input_file)

        output_file = input_file.split('.')[0] + ".flac"
        target_compression = 'FLAC'
        target_compression_subtype = 'PCM_S8'

        output_path = "Final_Upload"
        output_path = os.path.join(output_path,foldername)
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        output_file_path = os.path.join(output_path,output_file)

        audio, sample_rate = sf.read(input_file_path)
        sf.write(output_file_path, audio, sample_rate, subtype=target_compression_subtype, format=target_compression)
        print("done",input_file)
    except Exception as e:
        print("error",path,input_file,e)

UPLOAD_DIRECTORY = 'uploads'
output_path = "Final_Upload"
if not os.path.exists(output_path):
    os.mkdir(output_path)

folders = os.listdir(UPLOAD_DIRECTORY)
print("Compressing ",len(folders)," folders.")
for folder in folders:
    folder_path = os.path.join(UPLOAD_DIRECTORY,folder)
    files = os.listdir(folder_path)
    print("Doing Folder ",folder," with ",len(files)," files.")
    for file in files:
        compress_file(folder_path,folder,file)