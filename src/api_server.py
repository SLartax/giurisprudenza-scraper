from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = "data/sentenza_oggi.json"

@app.route('/api/sentenza', methods=['GET'])
def get_sentenza():
    try:
        if not os.path.exists(DATA_FILE):
            return jsonify({"error": "No data available"}), 404
        
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify(data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
