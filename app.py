from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import base64
from pymongo import MongoClient
from urllib.parse import quote_plus
from datetime import datetime

app = Flask(__name__)

# --- DATABASE CONNECTION ---
DB_USER = "saqibzaheersattirocklight_db_user"
DB_PASS = "DsUTBwyxsi5sdYf2"
ENCODED_PASS = quote_plus(DB_PASS)
MONGO_URI = f"mongodb+srv://{DB_USER}:{ENCODED_PASS}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['as_realestate_final']
    collection = db['properties']
    settings_col = db['settings']
    print("Cloud Database Connected!")
except Exception as e:
    print(f"DB Error: {e}")

# --- ROUTES ---

@app.route('/')
def index():
    rates_doc = settings_col.find_one({"type": "rates"})
    marquee_text = rates_doc['text'] if rates_doc else "Welcome to A&S Real Estate Islamabad"
    return render_template('index.html', rates=marquee_text)

@app.route('/get_properties')
def get_properties():
    props = list(collection.find().sort('_id', -1))
    for p in props: p['_id'] = str(p['_id'])
    return jsonify(props)

@app.route('/save_property', methods=['POST'])
def save_property():
    data = request.json
    # Image base64 mein save hogi takay URL ki tension na ho
    collection.insert_one(data)
    return jsonify({"status": "success"})

@app.route('/delete_property', methods=['POST'])
def delete_property():
    from bson.objectid import ObjectId
    prop_id = request.json.get('id')
    collection.delete_one({"_id": ObjectId(prop_id)})
    return jsonify({"status": "deleted"})

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    if 'rates' in data:
        settings_col.update_one({"type": "rates"}, {"$set": {"text": data['rates']}}, upsert=True)
    if 'pin' in data:
        settings_col.update_one({"type": "admin_pin"}, {"$set": {"value": data['pin']}}, upsert=True)
    return jsonify({"status": "ok"})

@app.route('/get_pin')
def get_pin():
    pin_doc = settings_col.find_one({"type": "admin_pin"})
    return jsonify({"pin": pin_doc['value'] if pin_doc else "as123"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
