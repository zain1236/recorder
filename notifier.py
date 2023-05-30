import os
import threading
import time

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
                            else:
                                print("Call Ended")
                # time.sleep(2)
            except Exception as e:
                print("error2",e)
                pass

    def start(self):
        t1 = threading.Thread(target=self.set_call_status)
        t1.start()
        t1.join()

t = teamsRecorder()
t.start()
