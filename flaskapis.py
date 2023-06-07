import time

from flask import Flask, render_template,request, send_from_directory
import os
import wave
import datetime
app = Flask(__name__)

# Define the directory where uploaded files will be saved
UPLOAD_DIRECTORY = "uploads"

# Create the upload directory if it does not exist
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@app.route('/', methods=['GET'])
def test():
    return "working", 200

def get_last_seen(path):
    p = os.path.join(path, 'lastseen.txt')
    lastseen = "Not known"
    if os.path.exists(p):
        with open(p, 'r') as l:
            lastseen = l.read().strip()

    return lastseen



@app.route('/ids', methods=['GET'])
def get_ids():
    dirs = os.listdir('uploads')

    dirs = [(dir, len(os.listdir(os.path.join('uploads', dir))),get_last_seen(os.path.join('uploads', dir))) for dir in dirs]
    # tags = [f"<a href='{item}'>{item}</a>" for item in dirs]
    return render_template('index.html',my_array=dirs)

def get_audio_duration(path):
    mywav = wave.open(path)
    duration_seconds = mywav.getnframes() / mywav.getframerate()
    duration_time = round(duration_seconds/60,2)
    return duration_time

@app.route('/ids/<path>', methods=['GET'])
def get_recs(path):

    u_path = 'uploads'
    if path:
        u_path = os.path.join(u_path,path)

    p = os.path.join(u_path,'lastseen.txt')
    lastseen = "Not known"
    if os.path.exists(p):
        with open(p,'r') as l:
            lastseen = l.read().strip()

    # print(u_path)
    dirs = os.listdir(u_path)
    dirs = [(d,round(os.path.getsize(os.path.join(u_path,d))/(1024*1024),2),get_audio_duration(os.path.join(u_path,d))) for d in dirs if not d == 'lastseen.txt']
    return render_template('download.html',lastseen=lastseen, my_array=dirs,path=path)
    # return dirs, 200


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file provided", 400

    file = request.files['file']
    if file.filename == '':
        return "Empty file name", 400

    # Get folder
    folder = file.filename.split('_')[0]
    f_path = os.path.join(UPLOAD_DIRECTORY, folder)
    if not os.path.exists(f_path):
        os.mkdir(f_path)

    # Get full path
    a = os.path.join(f_path, file.filename)
    file.save(os.path.join(a))

    with open(os.path.join(f_path,'lastseen.txt'),'w') as t_file:
        curr_time = time.strftime('%Y-%m-%d %H:%M:%S')
        t_file.write(curr_time)


    # with wave.open(a) as mywav:
    #     duration_seconds = mywav.getnframes() / mywav.getframerate()
    #
    # if round(duration_seconds / 60, 2) < 0.10:
    #     os.remove(a)
    #     print("removed",a)


    return "File saved", 200


@app.route('/ids/download/<path>/<filename>', methods=['GET'])
def download_file(path,filename):
    # print(path)
    # print(filename)
    path = os.path.join(UPLOAD_DIRECTORY,path)
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/checkupdate', methods=['POST'])
def check_updated_file():
    data = request.json
    client_time = data.get('mod_time')
    server_time = os.path.getmtime('rec/optimizev3.exe')
    client_time = datetime.datetime.fromtimestamp(client_time)
    server_time = datetime.datetime.fromtimestamp(server_time)

    print(client_time,server_time)

    if client_time < server_time:
        print("need")
        return "Need Update"
    else:
        print("no need")
        return "Up To Date"
    # path = 'rec'
    # return send_from_directory(path,'optimizev3.exe', as_attachment=True)


@app.route('/updatedfile', methods=['GET'])
def get_updated_file():
    # print(path)
    # print(filename)
    path = 'rec'
    return send_from_directory(path,'optimizev3.exe', as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True,host="192.168.100.24",port=3001)