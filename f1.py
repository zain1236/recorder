from flask import Flask, request, send_from_directory
import os

app = Flask(__name__)

# Define the directory where uploaded files will be saved
UPLOAD_DIRECTORY = "uploads"

# Create the upload directory if it does not exist
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@app.route('/', methods=['GET'])
def test():
   return "I am working", 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file provided", 400
    file = request.files['file']
    if file.filename == '':
        return "Empty file name", 400

    folder = file.filename.split('_')[0]
    filepath = os.path.join(UPLOAD_DIRECTORY, folder)
    if not os.path.exists(filepath):
        os.mkdir(filepath)

    file.save(os.path.join(filepath, file.filename))
    return "File saved", 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_DIRECTORY, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True,host='192.168.100.24',port=3001)
