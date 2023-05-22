import os
import threading
import pyaudiowpatch as pyaudio
import wave
# import requests
from datetime import datetime
# from pydub import AudioSegment


class teamsRecorder:

    def __init__(self):
        # Get the active user's home directory path
        home_dir = os.path.expanduser("~")
        path1 = home_dir + "\AppData\Roaming\Microsoft\Teams"
        self.uploadPath = os.path.join(path1,'recording')
        if not os.path.exists(self.uploadPath):
            os.mkdir(self.uploadPath)
        self.path = os.path.join(path1,'logs.txt')
        self.erpIdPath = os.path.join(path1, 'erpid.txt')
        self.lastLine = os.path.join(path1,'lastline.txt')
        self.recording_in_progress = None
        self.start_record = None
        self.stop_record = None
        # self.pc_name = get_logged_in_user_email()
        self.user_name = None

        # Recording Parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 48000
        self.CHUNK = 1024
        self.default_speakers = None

        self.audio = pyaudio.PyAudio()

        # MIc
        self.in_stream = None
        self.mic_frames = []

        # SPeaker
        self.out_audio = None
        self.speaker_frames = []

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

            # print("last pos",last_pos)

            with open(self.lastLine, "w") as f:
                f.write(str(last_pos))

            return True, new_lines
        except:
            # print("error")
            return False, None

    def save_recording(self, frames,src):
        if src == 'mic':
            try:
                # Save the recorded audio as a WAV file
                now = datetime.now()
                filename = 'mic_' + now.strftime('%d_%m_%Y_%H_%M_%S') + '.wav'
                print(filename)

                mic_file_path = os.path.join(self.uploadPath,filename)
                wf = wave.open(mic_file_path, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                print("mic saved")
                return True,filename
            except:
                print("Error saving file")
                return False,None
                pass
        else:
            try:
                # Save the recorded audio as a WAV file
                now = datetime.now()
                filename = 'test_speaker_' + now.strftime('%d_%m_%Y_%H_%M_%S') + '.wav'
                # print(filename)

                speaker_file_path = os.path.join(self.uploadPath, filename)
                # Save the mixed audio to a single WAV file
                wavefile = wave.open(speaker_file_path, 'wb')
                wavefile.setnchannels(self.default_speakers["maxInputChannels"])
                wavefile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                wavefile.setframerate(int(self.default_speakers["defaultSampleRate"]))
                wavefile.writeframes(b''.join(frames))
                wavefile.close()
                print("Speaker saved")
                return True, filename
            except:
                return False, None
                # print("Error saving file1")
                pass


    def set_call_status(self):
        # set starting
        status = self.set_start_position(self.lastLine)
        while not status:
            status = self.set_start_position(self.lastLine)
            # print(status)

        # print("Call thread started")
        while True:
            try:
                status, new_lines = self.check_for_call()
                if status:
                    # Process the new lines
                    for line in new_lines:
                        # Do something with each new line
                        if "name: desktop_call_state_change_send" in line:
                            # call = eval(line)
                            # print(call)
                            if "isOngoing: true" in line:

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
                                self.out_stream = self.audio.open(format=pyaudio.paInt16,
                                                                      channels=default_speakers["maxInputChannels"],
                                                                      rate=int(default_speakers["defaultSampleRate"]),
                                                                      frames_per_buffer=pyaudio.get_sample_size(
                                                                          pyaudio.paInt16),
                                                                      input=True,
                                                                      input_device_index=default_speakers["index"],
                                                                      )
                                self.recording_in_progress = True

                                print("Call started")
                            else:
                                self.recording_in_progress = None

                                # end mic
                                self.in_stream.stop_stream()
                                self.in_stream.close()

                                # end speaker
                                self.out_stream.stop_stream()
                                self.out_stream.close()

                                self.audio.terminate()

                                print("Call Ended")
                                mic_status,mic_rec = self.save_recording(self.mic_frames,'mic')
                                spk_status,spk_rec = self.save_recording(self.speaker_frames,'speaker')
                                self.mic_frames = []
                                self.speaker_frames = []

                                # if mic_status and spk_status:
                                #     th = threading.Thread(target=self.mix_and_send,args=(mic_rec,spk_rec,))
                                #     th.start()
            except Exception as e:
                print("error2",e)
                continue

    def start_recording_mic(self):
        # print("recording thread started")
        while True:
            try:
                if self.recording_in_progress:
                    # print("recording")
                    data = self.in_stream.read(self.CHUNK)
                    self.mic_frames.append(data)
            except:
                print("record mic error")
                continue

    def start_recording_speaker(self):
        # print("recording thread started")
        while True:
            try:
                if self.recording_in_progress:
                    data = self.out_stream.read(self.CHUNK)
                    self.speaker_frames.append(data)
            except:
                print("record speaker error")
                continue

    def start(self):
        t2 = threading.Thread(target=self.start_recording_mic)
        t2.start()

        t3 = threading.Thread(target=self.start_recording_speaker)
        t3.start()

        t1 = threading.Thread(target=self.set_call_status)
        t1.start()

        t1.join()
        t2.join()
        t3.join()

t = teamsRecorder()
t.start()
