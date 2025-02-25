from flask import Flask, render_template, jsonify
import json
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/build-your-own')
def build_your_own():
    return render_template('build_your_own.html')

@app.route('/personal-stats')
def personal_stats():
    return render_template('personal_stats.html')

@app.route('/get_locks')
def get_locks():
    try:
        # Run locks.py to update progress and generate picks.json
        subprocess.run(['python', 'locks.py'], check=True)
        # Load and return the picks.json data
        with open('picks.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/progress')
def progress():
    try:
        with open('progress.json', 'r') as f:
            progress_data = json.load(f)
        return jsonify(progress_data)
    except Exception:
        return jsonify({"progress": 0, "message": "Not started"}), 200

# New route to serve selections.json from the "selections" folder
@app.route('/get_selections')
def get_selections():
    try:
        with open('selections/selections.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New route to return the current content of picks.json
@app.route('/get_picks')
def get_picks():
    try:
        with open('picks.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
