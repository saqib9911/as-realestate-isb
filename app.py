# ==========================================================
# PROJECT: A&S RealEstate Isb - OFFICIAL BACKEND v6.0
# DEVELOPER: Saqib Zaheer Satti
# DATABASE: MongoDB Cloud (Cluster0)
# ==========================================================

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

# --- SECURE CLOUD DATABASE CONFIGURATION ---
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

# MongoDB Connection String (Updated for A&S RealEstate Isb)
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['AS_RealEstate_ISB_Final']
    
    # Collection Definitions
    properties_col = db['listings_v6']
    settings_col = db['system_config']
    broadcast_col = db['marquee_media']
    
    client.admin.command('ping')
    print("\n" + "="*50)
    print("A&S REAL ESTATE CLOUD: ONLINE & SYNCED")
    print("="*50 + "\n")
except Exception as e:
    print(f"CRITICAL DB ERROR: {str(e)}")

# --- CORE BACKEND LOGIC ---

@app.route('/')
def index():
    """Main Landing Controller"""
    try:
        # Fetching Marquee Text
        m_doc = settings_col.find_one({"type": "live_marquee"})
        marquee_text = m_doc['text'] if m_doc else "A&S RealEstate Isb: Luxury Living in Islamabad"
        
        # Fetching Broadcast Images
        m_imgs = list(broadcast_col.find().sort('_id', -1).limit(8))
        for img in m_imgs: img['_id'] = str(img['_id'])
        
        return render_template('index.html', rates=marquee_text, m_imgs=m_imgs)
    except:
        return render_template('index.html', rates="A&S RealEstate Isb", m_imgs=[])

@app.route('/get_properties', methods=['GET'])
def get_properties():
    """Fetch All Property Listings"""
    try:
        listings = list(properties_col.find().sort('_id', -1))
        for item in listings: item['_id'] = str(item['_id'])
        return jsonify(listings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def save_property():
    """Save Property with Social Media Integration"""
    try:
        data = request.json
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['status'] = "Verified"
        
        res = properties_col.insert_one(data)
        return jsonify({"status": "success", "id": str(res.inserted_id)})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/upload_broadcast_img', methods=['POST'])
def upload_broadcast():
    """Upload Marquee Broadcast Pictures"""
    try:
        payload = request.json
        broadcast_col.insert_one({
            "image": payload.get('image'),
            "date": datetime.now()
        })
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/delete_property', methods=['POST'])
def delete_property():
    """Admin Only: Delete Listing"""
    try:
        pid = request.json.get('id')
        properties_col.delete_one({"_id": ObjectId(pid)})
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update Marquee and Security PIN"""
    try:
        data = request.json
        if 'marquee' in data:
            settings_col.update_one({"type": "live_marquee"}, {"$set": {"text": data['marquee']}}, upsert=True)
        if 'pin' in data:
            settings_col.update_one({"type": "security_pin"}, {"$set": {"code": data['pin']}}, upsert=True)
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error"}), 500

@app.route('/get_pin', methods=['GET'])
def get_pin():
    """Verify Security PIN"""
    doc = settings_col.find_one({"type": "security_pin"})
    return jsonify({"pin": doc['code'] if doc else "as123"})

# --- PWA AND MANIFEST SUPPORT ---
@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json', mimetype='application/json')

@app.route('/offline')
def offline_page():
    return "Check your internet connection."

# Server Startup
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
