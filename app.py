from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pymongo import MongoClient

app = Flask(__name__)

# --- MONGODB CONNECTION ---
# Yahan <DsUTBwyxsi5sdYf2> ki jagah apna asli password likhein
MONGO_URI = "mongodb+srv://saqibzaheersattirocklight_db_user:<db_password>@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['realestate_db'] # Database ka naam
    collection = db['properties'] # Collection ka naam
    # Connection test karne ke liye
    client.admin.command('ping')
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_properties')
def get_properties():
    try:
        # MongoDB se latest properties nikalna (ulta order mein)
        props = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(props)
    except Exception as e:
        return jsonify([])

@app.route('/save_property', methods=['POST'])
def save_property():
    try:
        new_data = {
            "title": request.form.get('title'),
            "price": request.form.get('price'),
            "area": request.form.get('area'),
            "type": request.form.get('type'),
            "map": request.form.get('map'),
            "video": request.form.get('video'),
            "img": "https://via.placeholder.com/300" # Placeholder kyunke Vercel file save nahi karta
        }
        # MongoDB mein data insert karna
        collection.insert_one(new_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# PWA Support
@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

# Vercel integration
app = app

if __name__ == '__main__':
    app.run(debug=True)
