import os
import threading
import time
import pyaudiowpatch as pyaudio
from datetime import datetime
import wave

class teamsRecorder:
    def __init__(self):

        # Set Basic
        # Get the active user's home directory path
        home_dir = os.path.expanduser("~")
        path1 = home_dir + "\AppData\Roaming\Microsoft\Teams"
        self.uploadPath = os.path.join(path1,'recording')
        if not os.path.exists(self.uploadPath):
            os.mkdir(self.uploadPath)
        self.path = os.path.join(path1,'logs.txt')
        self.erpIdPath = os.path.join(path1, 'erpid.txt')
        self.lastLine = os.path.join(path1,'lastline.txt')
        self.user_name = None

        # Recording start
        self.recording_in_progress = None
        self.audio = None

        # Recording Parameters
        self.FORMAT = pyaudio.paInt8
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 512
        self.default_speakers = None

        # MIc
        self.in_stream = None
        self.mic_file_path = None
        self.mic_wf = None

        # SPeaker
        self.out_stream = None
        self.speaker_file_path = None
        self.speaker_wf = None


    def set_start_position(self, local_log_file):
        try:
            with open(self.path, "r+") as f:
                last_pos = f.seek(0, os.SEEK_END)

            print(last_pos)

            with open(local_log_file, "w") as f:
                f.write(str(last_pos))
            return True
        except:
            return False

    def check_for_call(self):
        try:
            # Get Last Position from local log file
            with open(self.lastLine, "r") as f:
                last_pos = int(f.readline().strip())

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

            print("last pos",last_pos)

            with open(self.lastLine, "w") as f:
                f.write(str(last_pos))

            return True, new_lines
        except:
            # print("error")
            return False, None

    def start_recording_mic(self):
        while True:
            try:
                if self.recording_in_progress:
                    data = self.in_stream.read(self.CHUNK)
                    self.mic_wf.writeframes(data)
            except Exception as e:
                print(f"Error recording microphone: {str(e)}")
                pass

    def start_recording_speaker(self):
        while True:
            try:
                if self.recording_in_progress:
                    data = self.out_stream.read(self.CHUNK)
                    self.speaker_wf.writeframes(data)
            except Exception as e:
                print(f"Error recording Speaker: {str(e)}")
                pass

    def set_call_status(self):
        # set starting
        status = self.set_start_position(self.lastLine)
        while not status:
            status = self.set_start_position(self.lastLine)


        print("Call thread started")
        while True:
            try:
                status, new_lines = self.check_for_call()
                if status:
                    # Process the new lines
                    # print(new_lines)
                    for line in new_lines:
                        # Do something with each new line
                        if "name: desktop_call_state_change_send" in line:
                            if "isOngoing: true" in line:
                                print("Call started")


                                self.audio = pyaudio.PyAudio()

                                # Mic
                                # Open the audio stream
                                self.in_stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                                                 rate=self.RATE, input=True,
                                                                 frames_per_buffer=self.CHUNK)

                                # Speaker
                                wasapi_info = self.audio.get_host_api_info_by_type(pyaudio.paWASAPI)
                                default_speakers = self.audio.get_device_info_by_index(
                                    wasapi_info["defaultOutputDevice"])
                                if not default_speakers["isLoopbackDevice"]:
                                    for loopback in self.audio.get_loopback_device_info_generator():
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
                                self.out_stream = self.audio.open(format=pyaudio.paInt8,
                                                                  channels=default_speakers["maxInputChannels"],
                                                                  rate=int(default_speakers["defaultSampleRate"]),
                                                                  frames_per_buffer=pyaudio.get_sample_size(
                                                                      pyaudio.paInt8),
                                                                  input=True,
                                                                  input_device_index=default_speakers["index"],
                                                                  )

                                now = datetime.now()
                                filename = now.strftime('%d_%m_%Y_%H_%M_%S') + '.wav'

                                self.mic_file_path = os.path.join(self.uploadPath, f"mic_{filename}")
                                self.speaker_file_path = os.path.join(self.uploadPath, f"speaker_{filename}")

                                # MIC FILE
                                self.mic_wf = wave.open(self.mic_file_path, 'wb')
                                self.mic_wf.setnchannels(self.CHANNELS)
                                self.mic_wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt8))
                                self.mic_wf.setframerate(self.RATE)

                                # Speaker File
                                self.speaker_wf = wave.open(self.speaker_file_path, 'wb')
                                self.speaker_wf.setnchannels(self.default_speakers["maxInputChannels"])
                                self.speaker_wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt8))
                                self.speaker_wf.setframerate(int(self.default_speakers["defaultSampleRate"]))

                                self.recording_in_progress = True
                            else:
                                print("Call Ended")
                                self.recording_in_progress = None

                                # end mic
                                self.in_stream.stop_stream()
                                self.in_stream.close()

                                # end speaker
                                self.out_stream.stop_stream()
                                self.out_stream.close()

                                self.audio.terminate()

                                self.mic_wf.close()
                                self.speaker_wf.close()

                                print("Call Ended")
                time.sleep(2)
            except Exception as e:
                print("error2",e)
                pass

    def start(self):
        t1 = threading.Thread(target=self.set_call_status)
        t1.start()
        t1.join()

t = teamsRecorder()
t.start()
