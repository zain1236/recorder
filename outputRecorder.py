import pyaudiowpatch as pyaudio
import wave

# import pyaudiowpatch as pyaudio

mic_buffer = []
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

p = pyaudio.PyAudio()

wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
print(wasapi_info)

default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

if not default_speakers["isLoopbackDevice"]:
    for loopback in p.get_loopback_device_info_generator():
        """
        Try to find loopback device with same name(and [Loopback suffix]).
        Unfortunately, this is the most adequate way at the moment.
        """
        if default_speakers["name"] in loopback["name"]:
            default_speakers = loopback
            break
    else:
        print("Default device not found")

print(default_speakers)

stream = p.open(format=pyaudio.paInt16,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt16),
                    input=True,
                    input_device_index=default_speakers["index"],
                    )

print('* recording microphone')
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    print(data)
    mic_buffer.append(data)

print("* done recording microphone")
stream.stop_stream()
stream.close()
p.terminate()

# Save the mixed audio to a single WAV file
waveFile = wave.open('loopback.wav', 'wb')
waveFile.setnchannels(["maxInputChannels"])
waveFile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
waveFile.setframerate(int(default_speakers["defaultSampleRate"]))
waveFile.writeframes(b''.join(mic_buffer))
waveFile.close()
