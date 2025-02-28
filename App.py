from flask import Flask, render_template, jsonify, send_from_directory
import json
import subprocess

app = Flask(__name__, template_folder='docs')  # Updated to use 'docs' instead of 'templates'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/premade')
def premade():
    return render_template('premade.html')

@app.route('/build-your-own')
def build_your_own():
    return render_template('build_your_own.html')

@app.route('/personal-stats')
def personal_stats():
    return render_template('personal_stats.html')

@app.route('/get_locks')
def get_locks():
    try:
        subprocess.run(['python', 'locks.py'], check=True)
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

@app.route('/get_selections')
def get_selections():
    try:
        with open('selections/selections.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_picks')
def get_picks():
    try:
        with open('picks.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NEW: Serve files from the selections folder (including time.json)
@app.route('/selections/<path:filename>')
def serve_selections(filename):
    return send_from_directory('selections', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000, threaded=True)
