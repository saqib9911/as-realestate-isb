from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime

app = Flask(__name__)

# --- DATABASE CONFIGURATION (A&S CLOUD) ---
# Saqib Bhai, ye credentials aapke project ko online rakhne ke liye hain
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

# MongoDB Connection String with Cluster0
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['realestate_db']
    collection = db['properties']
    rates_collection = db['live_rates']
    # Server testing
    client.admin.command('ping')
    print("------------------------------------------")
    print(">>> A&S CLOUD DATABASE CONNECTED <<<")
    print("------------------------------------------")
except Exception as e:
    print(f"!!! DATABASE ERROR: {e} !!!")

# --- ROUTES ---

@app.route('/')
def index():
    """Main Website Landing Page"""
    try:
        # Fetching latest market rates for the Marquee
        rates_doc = rates_collection.find_one({"type": "headline"})
        market_rates = rates_doc['text'] if rates_doc else "Welcome to A&S Real Estate Islamabad Specialist"
        return render_template('index.html', rates=market_rates)
    except:
        return render_template('index.html', rates="A&S Management: Quality Property Solutions")

@app.route('/get_properties')
def get_properties():
    """API for Frontend to get listings"""
    try:
        # Sorting by newest first using MongoDB _id
        all_listings = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(all_listings)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/save_property', methods=['POST'])
def save_property():
    """Secure Route to save data to MongoDB"""
    try:
        data = request.json
        # Adding Timestamp for record keeping
        data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert to Cloud
        collection.insert_one(data)
        return jsonify({"status": "success", "message": "Listing published online!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_rates', methods=['POST'])
def update_rates():
    """Admin route to update the marquee rates"""
    try:
        new_text = request.json.get('text')
        rates_collection.update_one(
            {"type": "headline"},
            {"$set": {"text": new_text}},
            upsert=True
        )
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- PWA & SYSTEM FILES ---

@app.route('/sw.js')
def service_worker():
    """PWA Service Worker for Offline Mode"""
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest_file():
    """PWA Manifest for Installability"""
    return send_from_directory(os.getcwd(), 'manifest.json')

# Entry point for laptop and Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
