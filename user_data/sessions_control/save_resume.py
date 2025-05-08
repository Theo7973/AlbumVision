# app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/albumVisionSessionDB'
mongo = PyMongo(app)

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
    app.run(debug=True)