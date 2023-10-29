import os
from werkzeug.utils import secure_filename

from flask import Flask
from flask import request, jsonify

from ocr_analyse import main

UPLOAD_FOLDER = 'images'  # todo endre her
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#! path: http://127.0.0.1:5000/media/upload
@app.route('/media/upload', methods=['POST'])
def upload_media():
    print(request.files)
    if 'file' not in request. files:
        return jsonify({'error': 'media not provided or not correct filetype'}), 400
    file = request. files['file']
    if file. filename == "":
        return jsonify({'error': 'no file selected'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        text = main(path)
        print(text)
        return jsonify({'msg': text}), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
