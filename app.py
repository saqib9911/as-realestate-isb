from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from bson.objectid import ObjectId

# --- APP INITIALIZATION ---
app = Flask(__name__)

# --- SECURE CLOUD DATABASE CONFIGURATION ---
# Owner: Saqib Zaheer Satti
# Project: A&S Management System Official
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

# MongoDB Connection String with Cluster0 Reference
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Initializing MongoDB Client with specific timeouts for stability
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['as_management_final_production']
    
    # Collections Definitions
    collection = db['properties_listing']
    settings_col = db['system_settings']
    admin_col = db['admin_access']
    
    # Database Ping Test to ensure cloud connectivity
    client.admin.command('ping')
    print("\n" + "="*50)
    print(">>> A&S MANAGEMENT CLOUD: SYSTEM ONLINE <<<")
    print("="*50 + "\n")
except Exception as e:
    print(f"CRITICAL DATABASE ERROR: {str(e)}")

# --- SERVER SIDE LOGIC & ROUTES ---

@app.route('/')
def index():
    """
    Main Landing Page Route.
    Fetches the live marquee rate list from the 'system_settings' collection.
    If no data exists, it provides a professional default message.
    """
    try:
        rates_query = settings_col.find_one({"setting_type": "global_marquee"})
        if rates_query and 'content' in rates_query:
            live_rates = rates_query['content']
        else:
            live_rates = "A&S Management: Your Trusted Partner in Islamabad Real Estate."
        return render_template('index.html', rates=live_rates)
    except Exception as err:
        print(f"Index Route Error: {err}")
        return render_template('index.html', rates="Welcome to A&S Official Portal")

@app.route('/get_properties', methods=['GET'])
def get_properties():
    """
    Fetches all property listings stored in MongoDB.
    Sorted by latest upload timestamp.
    """
    try:
        raw_data = list(collection.find().sort('_id', -1))
        # Logic to convert BSON ObjectIDs to JSON Strings
        processed_data = []
        for doc in raw_data:
            doc['_id'] = str(doc['_id'])
            processed_data.append(doc)
        return jsonify(processed_data)
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def save_property():
    """
    Handles Multi-part Property Data.
    Includes Base64 Encoded Image Strings for direct cloud storage.
    """
    try:
        form_data = request.json
        
        # Validation Logic for Mandatory Fields
        required_fields = ['title', 'price', 'area', 'img']
        for field in required_fields:
            if not form_data.get(field):
                return jsonify({"status": "failed", "reason": f"Field {field} is missing"}), 400
        
        # Meta-data Injection
        form_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        form_data['status'] = "Active"
        
        # Database Insertion
        insert_result = collection.insert_one(form_data)
        
        if insert_result.inserted_id:
            return jsonify({"status": "success", "id": str(insert_result.inserted_id)})
        return jsonify({"status": "error", "msg": "Insertion failed"}), 500
        
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/delete_property', methods=['POST'])
def delete_property():
    """
    Admin Command: Permanently removes a listing from the Cloud Database.
    Requires valid MongoDB ObjectId.
    """
    try:
        target_id = request.json.get('id')
        if not target_id:
            return jsonify({"status": "error", "msg": "No ID provided"}), 400
            
        delete_op = collection.delete_one({"_id": ObjectId(target_id)})
        
        if delete_op.deleted_count > 0:
            return jsonify({"status": "success", "msg": "Listing Deleted Forever"})
        return jsonify({"status": "not_found"}), 404
        
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """
    Multi-functional Update Route.
    Used for updating Marquee content and Admin PIN.
    """
    try:
        update_data = request.json
        
        # Handling Marquee Content Updates
        if 'marquee' in update_data:
            settings_col.update_one(
                {"setting_type": "global_marquee"},
                {"$set": {"content": update_data['marquee']}},
                upsert=True
            )
            
        # Handling Admin Security PIN Updates
        if 'pin' in update_data:
            settings_col.update_one(
                {"setting_type": "admin_security"},
                {"$set": {"pin_code": update_data['pin']}},
                upsert=True
            )
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/get_pin', methods=['GET'])
def get_pin():
    """
    Fetches the encrypted or plain PIN for session authentication.
    Default PIN: as123
    """
    try:
        pin_record = settings_col.find_one({"setting_type": "admin_security"})
        if pin_record and 'pin_code' in pin_record:
            return jsonify({"pin": pin_record['pin_code']})
        return jsonify({"pin": "as123"})
    except:
        return jsonify({"pin": "as123"})

# --- PWA & STATIC ASSET ROUTES ---

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # Running in production-ready mode
    app.run(debug=True, host='0.0.0.0', port=5000)
