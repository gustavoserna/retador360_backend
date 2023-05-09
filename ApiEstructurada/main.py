from flask import Flask, request
from apivideo import ApiVideo
# create the Flask app
app = Flask(__name__)

# GET requests will be blocked
@app.route('/ffmpeg', methods=['POST'])
def main():
    request_data = request.get_json()
    apiVideo = ApiVideo(request_data)
    result = apiVideo.processVideo()
    return result

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)