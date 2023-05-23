from flask import Flask, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from apivideo import ApiVideo
from uploadVideo import UploadVideo
import os
UPLOAD_FOLDER = os.getcwd() + '\\uploads'
# create the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# GET requests will be blocked
@app.route('/ffmpeg', methods=['POST'])
def main():
    request_data = request.get_json()
    apiVideo = ApiVideo(request_data)
    result = apiVideo.processVideo()
    return result

# GET requests will be blocked
@app.route('/test', methods=['get'])
def test():
    return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
            </form>
            '''

# GET requests will be blocked
@app.route('/uploadVideo', methods=['POST'])
def uploadVideos():
    """upload = UploadVideo(request=request, flash=flash)
    result = upload.upload_file()
    return result"""
    if request.method == 'POST':
    # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and UploadVideo.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file',
            #                        filename=filename))
            return 'Video uploaded'
        return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
            <input type=file name=file>
            <input type=submit value=Upload>
            </form>
            '''

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)