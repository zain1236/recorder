# import pywav
#
# wave_read = pywav.WavRead("10764_13_05_2023_04_54_21.wav")
# # print parameters like number of channels, sample rate, bits per sample, audio format etc
# # Audio format 1 = PCM (without compression)
# # Audio format 6 = PCMA (with A-law compression)
# # Audio format 7 = PCMU (with mu-law compression)
# print(wave_read.getparams())
#
# wave_write = pywav.WavWrite("output.wav", 1, 8000, 8, 6)
# # raw_data is the byte array. Write can be done only once for now.
# # Incremental write will be implemented later
# wave_write.write(wave_read)
# # close the file stream and save the file
# wave_write.close()
import threading

def log():
    print("hello world")

print("started")
th = threading.Thread(target=log)
th.start()
while not th.is_alive():
    th = threading.Thread(target=log)
    th.start()
