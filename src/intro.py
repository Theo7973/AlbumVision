from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt
import subprocess
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/albumVisionSessionDB'
mongo = PyMongo(app)
script_path = os.path.abspath('app/gui/main_window.py')

@app.route('/start-python', methods=['GET'])
def start_python_app():
    try:
        log_file = open('app/gui/log.txt', 'w')
        subprocess.Popen(['python', script_path], stdout=log_file, stderr=log_file)
        return jsonify({'message': 'Python app started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Save Session Endpoint
@app.route('/save-session', methods=['POST'])
def save_session():
    data = request.json
    user_id = data.get('userId')
    session_data = data.get('sessionData')

    try:
        existing_session = mongo.db.sessions.find_one({'userId': user_id})
        if existing_session:
            mongo.db.sessions.update_one({'userId': user_id}, {'$set': {'sessionData': session_data, 'updatedAt': datetime.utcnow()}})
        else:
            mongo.db.sessions.insert_one({'userId': user_id, 'sessionData': session_data, 'createdAt': datetime.utcnow()})
        return jsonify({'message': 'Session saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Resume Session Endpoint
@app.route('/resume-session/<user_id>', methods=['GET'])
def resume_session(user_id):
    try:
        session = mongo.db.sessions.find_one({'userId': user_id})
        if session:
            return jsonify({'sessionData': session['sessionData']}), 200
        else:
            return jsonify({'error': 'No session found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001)
