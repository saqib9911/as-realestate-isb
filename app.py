from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# --- SECURE DATABASE CONFIGURATION ---
# Saqib Bhai, ye aapka official MongoDB Cluster connection hai
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Connection setup with timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['as_management_system_v4']
    collection = db['properties']
    settings_col = db['settings']
    
    # Ping test to confirm connection
    client.admin.command('ping')
    print("-" * 40)
    print(">>> A&S CLOUD DATABASE CONNECTED <<<")
    print("-" * 40)
except Exception as e:
    print(f"!!! DATABASE ERROR: {e} !!!")

# --- CORE APPLICATION ROUTES ---

@app.route('/')
def index():
    """Main Website Landing with Live Marquee Integration"""
    try:
        # Fetching latest marquee data from cloud
        rates_doc = settings_col.find_one({"type": "marquee_system"})
        market_rates = rates_doc['text'] if rates_doc else "Welcome to A&S Real Estate | Specialists in Islamabad Sectors"
        return render_template('index.html', rates=market_rates)
    except:
        return render_template('index.html', rates="A&S Management: Quality Property Solutions")

@app.route('/get_properties', methods=['GET'])
def get_properties():
    """API for Frontend to fetch all listings (Newest First)"""
    try:
        listings = list(collection.find().sort('_id', -1))
        # Convert BSON ID to String for JavaScript compatibility
        for item in listings:
            item['_id'] = str(item['_id'])
        return jsonify(listings)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def save_property():
    """Secure Route to upload property with Base64 Image"""
    try:
        data = request.json
        if not data.get('title') or not data.get('price'):
            return jsonify({"status": "fail", "message": "Required fields missing"}), 400
        
        # Add metadata
        data['upload_date'] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # Insert into MongoDB
        collection.insert_one(data)
        return jsonify({"status": "success", "message": "Listing Live!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_property', methods=['POST'])
def delete_property():
    """Admin Only: Delete a listing from Cloud"""
    try:
        prop_id = request.json.get('id')
        if prop_id:
            res = collection.delete_one({"_id": ObjectId(prop_id)})
            if res.deleted_count > 0:
                return jsonify({"status": "success"})
        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update Dynamic Marquee or Security PIN"""
    try:
        data = request.json
        if 'marquee' in data:
            settings_col.update_one(
                {"type": "marquee_system"},
                {"$set": {"text": data['marquee']}},
                upsert=True
            )
        if 'pin' in data:
            settings_col.update_one(
                {"type": "admin_auth"},
                {"$set": {"pin_code": data['pin']}},
                upsert=True
            )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_pin', methods=['GET'])
def get_pin():
    """Fetch stored PIN for login verification"""
    try:
        doc = settings_col.find_one({"type": "admin_auth"})
        return jsonify({"pin": doc['pin_code'] if doc else "as123"})
    except:
        return jsonify({"pin": "as123"})

# --- SYSTEM FILES ---
@app.route('/sw.js')
def service_worker():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest_file():
    return send_from_directory(os.getcwd(), 'manifest.json')

if __name__ == '__main__':
    # Running locally on Laptop
    app.run(debug=True, host='0.0.0.0', port=5000)
