from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurations for Local Laptop Storage
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATA_FILE = 'properties.json'

# Ensure folders and database file exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_properties')
def get_properties():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify([])


@app.route('/save_property', methods=['POST'])
def save_property():
    try:
        # Form fields read karna
        title = request.form.get('title')
        price = request.form.get('price')
        area = request.form.get('area')
        p_type = request.form.get('type')
        p_map = request.form.get('map')
        video = request.form.get('video')

        # Image file handle karna
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            # Laptop ke folder mein save karna
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # URL path jo HTML mein use hoga
            img_url = f'/{UPLOAD_FOLDER}/{filename}'
        else:
            return jsonify({"status": "error", "message": "No image uploaded"}), 400

        # Naya data object
        new_listing = {
            "title": title,
            "price": price,
            "area": area,
            "type": p_type,
            "map": p_map,
            "video": video,
            "img": img_url
        }

        # Database (JSON) update karna
        with open(DATA_FILE, 'r+') as f:
            data = json.load(f)
            data.insert(0, new_listing)
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# PWA Support
@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')


@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')


if __name__ == '__main__':
    app.run(debug=True)