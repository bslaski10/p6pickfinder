from flask import Flask, render_template, jsonify, send_from_directory, request
import json
import subprocess
import os

app = Flask(__name__, template_folder='docs')  # Using 'docs' instead of 'templates'

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

# Serve files from the selections folder (including time.json)
@app.route('/selections/<path:filename>')
def serve_selections(filename):
    return send_from_directory('selections', filename)

# --- New endpoints for adding, editing, and deleting parlays ---

@app.route('/add_parlay', methods=['POST'])
def add_parlay():
    try:
        data = request.get_json()
        # Gather up to 3 selections and results (ignore empty fields)
        selections = []
        results = []
        for i in range(1, 4):
            sel = data.get(f'selection{i}', '').strip()
            res = data.get(f'result{i}', '')
            if sel:
                selections.append(sel)
                results.append(res)
        bet_amount = float(data.get('bet_amount', 0))
        base_pay = float(data.get('base_pay', 0))
        bonus_pay = float(data.get('bonus_pay', 0))
        total_pay = base_pay + bonus_pay
        profit = total_pay - bet_amount

        new_parlay = {
            "legs": selections,
            "result": results,
            "bet_amount": bet_amount,
            "base_pay": base_pay,
            "bonus_pay": bonus_pay,
            "total_pay": total_pay,
            "profit": profit
        }
        with open('profit.json', 'r') as f:
            json_data = json.load(f)
        json_data['parlays'].append(new_parlay)
        with open('profit.json', 'w') as f:
            json.dump(json_data, f, indent=4)
        return jsonify({"status": "success", "parlay": new_parlay}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/edit_parlay', methods=['POST'])
def edit_parlay():
    try:
        data = request.get_json()
        index = int(data.get('index'))
        selections = []
        results = []
        for i in range(1, 4):
            sel = data.get(f'selection{i}', '').strip()
            res = data.get(f'result{i}', '')
            if sel:
                selections.append(sel)
                results.append(res)
        bet_amount = float(data.get('bet_amount', 0))
        base_pay = float(data.get('base_pay', 0))
        bonus_pay = float(data.get('bonus_pay', 0))
        total_pay = base_pay + bonus_pay
        profit = total_pay - bet_amount

        updated_parlay = {
            "legs": selections,
            "result": results,
            "bet_amount": bet_amount,
            "base_pay": base_pay,
            "bonus_pay": bonus_pay,
            "total_pay": total_pay,
            "profit": profit
        }
        with open('profit.json', 'r') as f:
            json_data = json.load(f)
        json_data['parlays'][index] = updated_parlay
        with open('profit.json', 'w') as f:
            json.dump(json_data, f, indent=4)
        return jsonify({"status": "success", "parlay": updated_parlay}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_parlay', methods=['POST'])
def delete_parlay():
    try:
        data = request.get_json()
        index = int(data.get('index'))
        with open('profit.json', 'r') as f:
            json_data = json.load(f)
        deleted_parlay = json_data['parlays'].pop(index)
        with open('profit.json', 'w') as f:
            json.dump(json_data, f, indent=4)
        return jsonify({"status": "success", "deleted": deleted_parlay}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))  # Use Render's assigned port
    app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
