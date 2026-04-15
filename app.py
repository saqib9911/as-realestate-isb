from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATA_FILE = 'properties.json'

# Vercel fix: Folder banane ki koshish karein, agar error aaye to ignore karein
try:
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except:
    pass

# Data file check
if not os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_properties')
def get_properties():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        return jsonify([])
    except Exception as e:
        return jsonify([])

@app.route('/save_property', methods=['POST'])
def save_property():
    try:
        title = request.form.get('title')
        price = request.form.get('price')
        area = request.form.get('area')
        p_type = request.form.get('type')
        p_map = request.form.get('map')
        video = request.form.get('video')

        file = request.files.get('file')
        img_url = ""
        
        if file:
            filename = secure_filename(file.filename)
            # Vercel par file save karna aksar fail hoga, is liye try-except
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                img_url = f'/{UPLOAD_FOLDER}/{filename}'
            except Exception as e:
                # Agar save na ho (Vercel ki wajah se), to placeholder image de dein
                img_url = "https://via.placeholder.com/300"
        
        new_listing = {
            "title": title, "price": price, "area": area,
            "type": p_type, "map": p_map, "video": video, "img": img_url
        }

        # JSON update (Local laptop par kaam karega, Vercel par temporary hoga)
        try:
            with open(DATA_FILE, 'r+') as f:
                data = json.load(f)
                data.insert(0, new_listing)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except:
            return jsonify({"status": "error", "message": "Storage is read-only on Vercel"}), 200

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

# Vercel needs this variable
app = app

if __name__ == '__main__':
    app.run(debug=True)
