import os
import threading
import time
import pyaudiowpatch as pyaudio
from datetime import datetime
import wave
from pydub import AudioSegment
import requests

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
        # self.err_log = open(os.path.join(path1,'errlog.txt'), "w")
        self.user_name = None

        # Recording start
        self.recording_in_progress = None
        self.audio = None

        # Recording Parameters
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 512
        self.default_speakers = None

        # MIc
        self.in_stream = None
        self.mic_file_path = None
        self.mic_wf = None
        self.in_mic = False

        # SPeaker
        self.out_stream = None
        self.speaker_file_path = None
        self.speaker_wf = None
        self.in_spk = False



    def set_start_position(self, local_log_file):
        try:
            with open(self.path, "r+") as f:
                last_pos = f.seek(0, os.SEEK_END)

            print(last_pos)

            with open(local_log_file, "w") as f:
                f.write(str(last_pos))
            return True
        except Exception as e:
            # self.err_log.write(f"Error Set start Speaker: {str(e)} \n")
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
        except Exception as e:
            # self.err_log.write(f"Error Check Call: {str(e)} \n")
            # print("error")
            return False, None

    def start_recording_mic(self):
        while True:
            try:
                if self.recording_in_progress and self.mic_wf:
                    self.in_mic = True
                    data = self.in_stream.read(self.CHUNK)
                    self.mic_wf.writeframes(data)
                    self.in_mic = False
            except Exception as e:
                # self.err_log.write(f"Error recording Speaker: {str(e)} \n")
                print(f"Error recording microphone: {str(e)}")
                pass

    def start_recording_speaker(self):
        while True:
            try:
                if self.recording_in_progress and self.speaker_wf:
                    self.in_spk = True
                    data = self.out_stream.read(self.CHUNK)
                    self.speaker_wf.writeframes(data)
                self.in_spk = False
            except Exception as e:
                # self.err_log.write(f"Error recording Speaker: {str(e)} \n")
                print(f"Error recording Speaker: {str(e)}")
                pass

    def compress_audio(self,audio_path, output_path, format='wav', bitrate='16k'):
        audio = AudioSegment.from_file(audio_path)
        compressed_audio = audio.export(output_path, format=format, bitrate=bitrate)
        return compressed_audio

    def mix(self,mic,spk):
        try:
            mic_recording = AudioSegment.from_wav(mic)
            spk_recording = AudioSegment.from_wav(spk)

            print("mixing")
            # Adjust the length of the audio files if needed
            mixed_audio = mic_recording.overlay(spk_recording)

            sp_mic = mic.split('_')[1:]

            fh = open(self.erpIdPath, 'r')
            self.user_name = fh.readlines()[0].strip()
            fh.close()
            filename = self.user_name
            for w in sp_mic:
                filename = filename + "_" + w


            output_path=os.path.join(self.uploadPath,filename)
            print("compressing")
            compress_output_file = output_path.split('.')[0] + '.mp3'
            mixed_audio.export(compress_output_file, format="mp3")
            # mixed_audio.export(output_path,format="wav")

            os.remove(mic)
            os.remove(spk)


            print("sending",compress_output_file)
            url = 'http://182.180.54.158:10202/upload'
            sound_file_path = compress_output_file
            if os.path.exists(sound_file_path):
                f2 = open(sound_file_path, 'rb')
                data = {'file': f2}
                response = requests.post(url, files=data)
                print(response.text)
                f2.close()
                if response.text == "File saved":
                    os.remove(sound_file_path)


        except Exception as e:
            print("error mixing",e)
            # self.err_log.write(f"Error Mixing : {str(e)} \n")

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
                            # print(line)
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
                                self.out_stream = self.audio.open(format=self.FORMAT,
                                                                  channels=default_speakers["maxInputChannels"],
                                                                  rate=int(default_speakers["defaultSampleRate"]),
                                                                  frames_per_buffer=pyaudio.get_sample_size(
                                                                      self.FORMAT),
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
                                self.mic_wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                                self.mic_wf.setframerate(self.RATE)

                                # Speaker File
                                self.speaker_wf = wave.open(self.speaker_file_path, 'wb')
                                self.speaker_wf.setnchannels(self.default_speakers["maxInputChannels"])
                                self.speaker_wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                                self.speaker_wf.setframerate(int(self.default_speakers["defaultSampleRate"]))

                                self.recording_in_progress = True

                            else:
                                print("Call Ended")
                                self.recording_in_progress = None

                                while self.in_mic or self.in_spk:
                                    continue

                                # end mic
                                self.in_stream.stop_stream()
                                self.in_stream.close()

                                # end speaker
                                self.out_stream.stop_stream()
                                self.out_stream.close()

                                self.audio.terminate()

                                self.mic_wf.close()
                                self.speaker_wf.close()

                                mix_th = threading.Thread(target=self.mix, args=(self.mic_file_path,self.speaker_file_path,))
                                mix_th.start()

                time.sleep(1)
            except Exception as e:
                # self.err_log.write(f"Error in main : {str(e)} \n")
                print("error2",e)
                pass

    def start(self):
        main_th = threading.Thread(target=self.set_call_status)
        main_th.start()

        # Threads
        mic_th = threading.Thread(target=self.start_recording_mic)
        mic_th.start()
        spk_th = threading.Thread(target=self.start_recording_speaker)
        spk_th.start()

        main_th.join()


t = teamsRecorder()
t.start()
