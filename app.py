from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# --- DATABASE CONNECTION (A&S CLOUD) ---
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

# MongoDB Connection with Cluster0
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['as_realestate_final_v3']
    collection = db['properties']
    settings_col = db['settings']
    # Server Ping Test
    client.admin.command('ping')
    print("------------------------------------------")
    print(">>> A&S CLOUD DATABASE: ONLINE <<<")
    print("------------------------------------------")
except Exception as e:
    print(f"!!! DATABASE CONNECTION ERROR: {e} !!!")

# --- CORE LOGIC ROUTES ---

@app.route('/')
def index():
    """Main Landing Page - Pulls Live Marquee from Cloud"""
    try:
        rates_doc = settings_col.find_one({"type": "marquee_data"})
        market_rates = rates_doc['text'] if rates_doc else "Welcome to A&S Management | Islamabad's Premier Real Estate"
        return render_template('index.html', rates=market_rates)
    except:
        return render_template('index.html', rates="A&S Management: Quality Property Solutions")

@app.route('/get_properties', methods=['GET'])
def get_properties():
    """Fetches all property listings for the grid"""
    try:
        all_listings = list(collection.find().sort('_id', -1))
        # Convert ObjectId to string for JSON compatibility
        for item in all_listings:
            item['_id'] = str(item['_id'])
        return jsonify(all_listings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def save_property():
    """Saves new property with Base64 Image to MongoDB"""
    try:
        data = request.json
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Validation
        if not data.get('title') or not data.get('price'):
            return jsonify({"status": "error", "message": "Missing Data"}), 400
            
        collection.insert_one(data)
        return jsonify({"status": "success", "message": "Property Published Successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_property', methods=['POST'])
def delete_property():
    """Deletes a specific property using its ID"""
    try:
        data = request.json
        prop_id = data.get('id')
        if prop_id:
            result = collection.delete_one({"_id": ObjectId(prop_id)})
            if result.deleted_count > 0:
                return jsonify({"status": "success", "message": "Deleted"})
        return jsonify({"status": "error", "message": "ID not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Updates Marquee text or Admin PIN in Cloud"""
    try:
        data = request.json
        if 'marquee' in data:
            settings_col.update_one(
                {"type": "marquee_data"},
                {"$set": {"text": data['marquee']}},
                upsert=True
            )
        if 'pin' in data:
            settings_col.update_one(
                {"type": "admin_security"},
                {"$set": {"pin_value": data['pin']}},
                upsert=True
            )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_pin', methods=['GET'])
def get_pin():
    """Securely fetches the current PIN for verification"""
    try:
        pin_doc = settings_col.find_one({"type": "admin_security"})
        current_pin = pin_doc['pin_value'] if pin_doc else "as123"
        return jsonify({"pin": current_pin})
    except:
        return jsonify({"pin": "as123"})

# --- PWA SUPPORT ---
@app.route('/sw.js')
def service_worker():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest_file():
    return send_from_directory(os.getcwd(), 'manifest.json')

if __name__ == '__main__':
    # Running on port 5000 for local development
    app.run(debug=True, host='0.0.0.0', port=5000)
