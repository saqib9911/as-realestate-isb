# ==============================================================================
# PROJECT NAME: A&S RealEstate Isb - OFFICIAL MANAGEMENT SYSTEM
# VERSION: 6.5 (Final Production Build)
# CHIEF DEVELOPER: Saqib Zaheer Satti
# DATABASE ENGINE: MongoDB Atlas Cloud
# ==============================================================================

from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import os
import json
import base64
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime
from bson.objectid import ObjectId

# --- FLASK APPLICATION CORE ---
app = Flask(__name__)

# --- SECURE CLOUD DATABASE (A&S OFFICIAL) ---
# Credentials as specified by Saqib Zaheer Satti
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)

# MongoDB Connection for Cluster0 - Advanced Persistence Configuration
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Initializing Client with specialized timeout handlers for Pakistani ISP stability
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=15000, connectTimeoutMS=15000)
    db = client['AS_RealEstate_ISB_v7_Official']
    
    # Core System Collections
    properties_listing = db['real_estate_listings']
    app_settings = db['system_configurations']
    broadcast_marquee = db['media_broadcast_marquee']
    
    # Connectivity Authentication Ping
    client.admin.command('ping')
    print("\n" + "="*60)
    print(">>> SYSTEM STATUS: CLOUD DATABASE CONNECTED SUCCESSFULLY <<<")
    print(">>> PROJECT OWNER: SAQIB ZAHEER SATTI <<<")
    print("="*60 + "\n")
except Exception as connection_error:
    print(f"CRITICAL SYSTEM ERROR (DB): {str(connection_error)}")

# --- SYSTEM ROUTING LOGIC ---

@app.route('/')
def home_portal():
    """
    Main Interface Route.
    Fetches synchronized marquee text and live broadcast images for the landing page.
    """
    try:
        # Fetching dynamic marquee text from the cloud
        marquee_config = app_settings.find_one({"config_id": "active_live_marquee"})
        if marquee_config and 'text_content' in marquee_config:
            live_text = marquee_config['text_content']
        else:
            live_text = "Welcome to A&S RealEstate Isb - Your Trusted Partner in Islamabad & Rawalpindi."
        
        # Fetching visual broadcast images for the scrolling media strip
        live_media = list(broadcast_marquee.find().sort('_id', -1).limit(10))
        for media_item in live_media:
            media_item['_id'] = str(media_item['_id'])
            
        return render_template('index.html', rates=live_text, m_imgs=live_media)
    except Exception as e:
        print(f"Routing Error on Index: {e}")
        return render_template('index.html', rates="A&S RealEstate Isb Portal Online", m_imgs=[])

@app.route('/get_properties', methods=['GET'])
def fetch_all_listings():
    """
    Data API: Retrieves all verified property records from MongoDB.
    Sorted by the most recent uploads first.
    """
    try:
        cursor = list(properties_listing.find().sort('_id', -1))
        # Processing MongoDB BSON format into standard JSON strings
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
        return jsonify(cursor)
    except Exception as e:
        return jsonify({"status": "error", "message": "Failed to fetch cloud data", "raw": str(e)}), 500

@app.route('/save_property', methods=['POST'])
def create_listing():
    """
    Management API: Creates a new property entry with full metadata.
    Includes Social Media (YT, TikTok, FB, Insta) integration.
    """
    try:
        input_data = request.json
        
        # Mandatory Field Validation
        if not input_data.get('title') or not input_data.get('img_base64'):
            return jsonify({"status": "failed", "reason": "Missing critical fields"}), 400
            
        # Metadata Injection for Record Keeping
        input_data['created_at_dt'] = datetime.now()
        input_data['formatted_date'] = datetime.now().strftime("%d %B, %Y (%I:%M %p)")
        input_data['listing_id'] = "AS-" + datetime.now().strftime("%Y%m%d%H%M%S")
        input_data['verified_by'] = "Saqib Zaheer Satti"
        
        insert_op = properties_listing.insert_one(input_data)
        
        if insert_op.inserted_id:
            return jsonify({"status": "success", "ref_id": str(insert_op.inserted_id)})
        return jsonify({"status": "error", "msg": "Database write failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/upload_marquee_photo', methods=['POST'])
def add_marquee_media():
    """
    Broadcast API: Updates the marquee with a live picture of a plot or project.
    Allows Saqib to update the scrolling strip visually.
    """
    try:
        media_payload = request.json.get('image_data')
        if media_payload:
            broadcast_marquee.insert_one({
                "image_url": media_payload,
                "upload_timestamp": datetime.now(),
                "active_status": True
            })
            return jsonify({"status": "success"})
        return jsonify({"status": "failed", "msg": "No media stream detected"}), 400
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/remove_listing', methods=['POST'])
def delete_listing_permanently():
    """
    Admin Command: Permanently deletes a property record.
    Security: Access restricted via frontend PIN.
    """
    try:
        doc_id = request.json.get('target_id')
        if doc_id:
            deletion = properties_listing.delete_one({"_id": ObjectId(doc_id)})
            if deletion.deleted_count > 0:
                return jsonify({"status": "success", "msg": "Property Purged from Cloud"})
        return jsonify({"status": "not_found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/update_global_config', methods=['POST'])
def sync_app_settings():
    """
    Control API: Updates Marquee Text and Security Access PIN.
    """
    try:
        config_data = request.json
        
        # Updating Live Scrolling Text
        if 'marquee_text' in config_data:
            app_settings.update_one(
                {"config_id": "active_live_marquee"},
                {"$set": {"text_content": config_data['marquee_text']}},
                upsert=True
            )
            
        # Updating Security Authentication PIN
        if 'new_pin' in config_data:
            app_settings.update_one(
                {"config_id": "admin_security_credentials"},
                {"$set": {"pin_code": config_data['new_pin']}},
                upsert=True
            )
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

@app.route('/get_auth_key', methods=['GET'])
def retrieve_security_pin():
    """Fetches the active PIN. Internal default fallback: as123"""
    try:
        security_doc = app_settings.find_one({"config_id": "admin_security_credentials"})
        if security_doc and 'pin_code' in security_doc:
            return jsonify({"pin": security_doc['pin_code']})
        return jsonify({"pin": "as123"})
    except:
        return jsonify({"pin": "as123"})

# --- PWA SERVICE WORKER HANDLERS ---
@app.route('/sw.js')
def handle_service_worker():
    return send_from_directory(os.getcwd(), 'sw.js', mimetype='application/javascript')

@app.route('/manifest.json')
def handle_app_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json', mimetype='application/json')

# --- PRODUCTION SERVER BOOTSTRAP ---
if __name__ == '__main__':
    # Initializing server on local gateway
    app.run(debug=True, host='0.0.0.0', port=5000)
