from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import json

# Vercel ke liye folders ki configuration
app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

DATA_FILE = 'properties.json'

# Ensure properties.json exists for the app to read
if not os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    except:
        pass

@app.route('/')
def index():
    # Flask auto-detects 'templates/index.html'
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
    # Vercel is read-only, so saving will only work locally or temporarily
    try:
        title = request.form.get('title')
        price = request.form.get('price')
        # Placeholder image as Vercel won't store permanent uploads
        img_url = "https://via.placeholder.com/300" 
        
        new_listing = {
            "title": title, 
            "price": price, 
            "area": request.form.get('area'),
            "type": request.form.get('type'),
            "map": request.form.get('map'),
            "video": request.form.get('video'),
            "img": img_url
        }
        return jsonify({"status": "success", "message": "Property added (Temporary)"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# PWA Support: In files ko main folder se serve karne ke liye
@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

# Critical for Vercel: expose the app object
app = app

if __name__ == '__main__':
    app.run(debug=True)
