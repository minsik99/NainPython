from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import searchnaver
import recode
import company
import emotion

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1", "http://localhost:3000"]}})

@app.route('/data', methods=['POST'])
def search_naver_news():
    return searchnaver.search_naver_news()

@app.route('/realtimeAnalysis', methods=['POST'])
def start():
    return recode.video_feed()

@app.route('/startVideo', methods=['POST'])
def startVideo():
    recode.video_feed()
    
@app.route('/save', methods=['POST'])
def save():
    file = request.files.get('video')
    itvNo = request.form.get('itvNo')

    if file and itvNo:
        response = recode.save_video(file, itvNo)
        return response, 200
    else:
        return jsonify({'error': 'Missing file or itvNo'}), 400

@app.route('/companylistsearch', methods=['POST'])
def companysearch():
    data = request.get_json()
    keyword = data.get('keyword')
    return company.companylist(keyword)

@app.route('/emotion', methods=['POST'])
def emotion():
    frame = start()
    return emotion.emotion_analysis(frame)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
