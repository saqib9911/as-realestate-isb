# ==============================================================================
# PROJECT: A&S REAL ESTATE ISLAMABAD - ENTERPRISE MANAGEMENT SYSTEM
# VERSION: 10.0.0 (ULTIMATE MASTER BUILD)
# CHIEF DEVELOPER: SAQIB ZAHEER SATTI
# TEAM CORE: UMER AFTAB, BILAL AFTAB, TALHA AFTAB
# ==============================================================================

import os
import json
import logging
from datetime import datetime
from urllib.parse import quote_plus
from flask import Flask, render_template, request, jsonify, send_from_directory

# Advanced Database Connectivity Drivers
try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
except ImportError:
    print("CRITICAL: Pymongo or BSON not found. Please run 'pip install pymongo'")

# --- FLASK APPLICATION CORE SETUP ---
app = Flask(__name__)

# --- SECURE CLOUD DATABASE CONFIGURATION ---
# Owner Identity: Saqib Zaheer Satti (Authorized Only)
DB_USERNAME = "saqibzaheersattirocklight_db_user"
DB_PASSWORD = "DsUTBwyxsi5sdYf2"
SAFE_PASSWORD = quote_plus(DB_PASSWORD)

# MongoDB Connection String Optimized for Islamabad Region
MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{SAFE_PASSWORD}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# --- GLOBAL DATABASE INITIALIZATION LOGIC ---
try:
    # Established connection with 20-second high-latency handshake for stable ISP performance
    cloud_client = MongoClient(
        MONGO_URI, 
        serverSelectionTimeoutMS=20000,
        connectTimeoutMS=20000,
        socketTimeoutMS=20000
    )
    
    # Target Production Database: A&S Official Store
    as_db = cloud_client['AS_Management_System_v10_Official']
    
    # Mapping Business Collections
    listings_col = as_db['property_listing_data']
    settings_col = as_db['global_application_settings']
    broadcast_col = as_db['marquee_media_broadcast']
    
    # Diagnostic Handshake
    cloud_client.admin.command('ping')
    print("\n" + "*" * 65)
    print("STATUS: A&S CLOUD INFRASTRUCTURE IS ONLINE")
    print("REGISTERED DEVELOPER: SAQIB ZAHEER SATTI")
    print("TEAM ACCESS: UMER AFTAB | BILAL AFTAB | TALHA AFTAB")
    print("*" * 65 + "\n")
    
except Exception as cloud_err:
    print(f"FATAL CLOUD CONNECTION FAILURE: {str(cloud_err)}")

# --- SYSTEM CONTROLLERS (API & ROUTING) ---

@app.route('/')
def load_portal_interface():
    """
    Primary Entry Point for A&S Portal.
    Synchronizes Scrolling Text and Broadcast Images from Cloud.
    """
    try:
        # 1. Fetching Dynamic Marquee Content
        marquee_query = settings_col.find_one({"meta_key": "active_marquee_rates"})
        if marquee_query and 'text_content' in marquee_query:
            current_rates = marquee_query['text_content']
        else:
            current_rates = "A&S Real Estate: Premium Property Solutions in Islamabad & Rawalpindi."
            
        # 2. Fetching Visual Media Stream (Last 15 Uploads)
        broadcast_stream = list(broadcast_col.find().sort('_id', -1).limit(15))
        for item in broadcast_stream:
            item['_id'] = str(item['_id'])
            
        return render_template(
            'index.html', 
            rates=current_rates, 
            m_imgs=broadcast_stream
        )
    except Exception as route_err:
        print(f"Interface Loading Error: {route_err}")
        return render_template('index.html', rates="A&S Portal Ready", m_imgs=[])

@app.route('/get_properties', methods=['GET'])
def api_fetch_listings():
    """
    Public API: Retrieves all verified property records.
    Ordered by latest timestamp.
    """
    try:
        data_cursor = list(listings_col.find().sort('_id', -1))
        # Processing MongoDB IDs for Frontend Compatibility
        for document in data_cursor:
            document['_id'] = str(document['_id'])
        return jsonify(data_cursor)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def api_submit_listing():
    """
    Admin Command: Commits a new property record to the database.
    Captures Title, Price, Location, and Base64 Images.
    """
    try:
        payload = request.json
        
        # Security & Metadata Stamping
        payload['submission_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload['verified_by'] = "Saqib Satti"
        payload['access_token'] = "AS-PRODUCTION-MASTER"
        
        # Cloud Persistence
        insertion_op = listings_col.insert_one(payload)
        
        if insertion_op.inserted_id:
            return jsonify({
                "status": "success", 
                "record_id": str(insertion_op.inserted_id)
            })
        return jsonify({"status": "database_error"}), 500
        
    except Exception as submission_err:
        return jsonify({"status": "error", "message": str(submission_err)}), 500

@app.route('/update_live_rates', methods=['POST'])
def api_sync_marquee():
    """
    Management Control: Updates the scrolling marquee text dynamically.
    """
    try:
        new_text = request.json.get('text_data')
        if not new_text:
            return jsonify({"status": "missing_data"}), 400
            
        settings_col.update_one(
            {"meta_key": "active_marquee_rates"},
            {"$set": {"text_content": new_text}},
            upsert=True
        )
        return jsonify({"status": "success", "sync_timestamp": str(datetime.now())})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/push_marquee_media', methods=['POST'])
def api_add_broadcast_img():
    """
    Broadcast Management: Adds a visual asset to the marquee stream.
    """
    try:
        image_payload = request.json.get('image_stream')
        if image_payload:
            broadcast_col.insert_one({
                "media_url": image_payload,
                "upload_time": datetime.now()
            })
            return jsonify({"status": "success"})
        return jsonify({"status": "empty_payload"}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/purge_listing', methods=['POST'])
def api_delete_property():
    """
    Admin Authority: Permanently deletes a property listing.
    """
    try:
        target_id = request.json.get('id_to_delete')
        listings_col.delete_one({"_id": ObjectId(target_id)})
        return jsonify({"status": "success", "action": "deleted"})
    except Exception as e:
        return jsonify({"status": "fail", "msg": str(e)}), 500

@app.route('/fetch_security_pin', methods=['GET'])
def api_get_admin_pin():
    """
    Security Protocol: Retrieves the Master PIN for Admin authentication.
    """
    pin_doc = settings_col.find_one({"meta_key": "system_admin_pin"})
    if pin_doc and 'pin_value' in pin_doc:
        return jsonify({"pin": pin_doc['pin_value']})
    # Safe Fallback
    return jsonify({"pin": "as123"})

# --- PWA & OFFLINE INFRASTRUCTURE ---

@app.route('/sw.js')
def serve_service_worker():
    """Serving Service Worker for PWA Offline Caching"""
    return send_from_directory(os.getcwd(), 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def serve_app_manifest():
    """Serving Manifest for Home Screen Installation"""
    return send_from_directory(os.getcwd(), 'manifest.json', mimetype='application/json')

# --- APPLICATION EXECUTION ---
if __name__ == '__main__':
    # Initializing in Debug mode for Saqib's development environment
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000
    )
