from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

# --- DATABASE CONNECTION ---
# Saqib Bhai, ye password aur user wahi hai jo humne pehle set kiya tha
user = "saqibzaheersattirocklight_db_user"
password = "DsUTBwyxsi5sdYf2"
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb+srv://{user}:{encoded_password}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['realestate_db']
    collection = db['properties']
    # Test connection
    client.admin.command('ping')
    print("Cloud Database Connected!")
except Exception as e:
    print(f"Connection Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_properties')
def get_properties():
    try:
        # Latest properties pehle dikhane ke liye sort kiya hai
        props = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(props)
    except:
        return jsonify([])

@app.route('/save_property', methods=['POST'])
def save_property():
    try:
        data = request.json
        collection.insert_one(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

if __name__ == '__main__':
    # Laptop par debug mode on rakhein taake error foran dikhe
    app.run(debug=True, host='0.0.0.0', port=5000)
