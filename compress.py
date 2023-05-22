import soundfile as sf


input_file = '10764_13_05_2023_04_54_21.wav'
output_file = input_file.split('.')[0] + ".flac"
target_compression = 'FLAC'
target_compression_subtype = 'PCM_S8'

audio, sample_rate = sf.read(input_file)
sf.write(output_file, audio, sample_rate, subtype=target_compression_subtype, format=target_compression)
