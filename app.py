from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

# --- SAFE CONNECTION LOGIC ---
user = "saqibzaheersattirocklight_db_user"
password = "DsUTBwyxsi5sdYf2"  # AGAR PASSWORD YAHI HAI TO THEEK HAI
encoded_password = quote_plus(password)

MONGO_URI = f"mongodb+srv://{user}:{encoded_password}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['realestate_db']
    collection = db['properties']
    rates_collection = db['live_rates']
    # Connection check
    client.admin.command('ping')
except Exception as e:
    print(f"Connection Error: {e}")

@app.route('/')
def index():
    try:
        rates_data = rates_collection.find_one({"type": "headline"})
        current_rates = rates_data['text'] if rates_data else "Market Updates Coming Soon..."
        return render_template('index.html', rates=current_rates)
    except Exception as e:
        # Agar error aaye to wo screen par nazar aaye ga
        return f"Database Error: {str(e)}", 500

@app.route('/get_properties')
def get_properties():
    try:
        props = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(props)
    except:
        return jsonify([])

@app.route('/admin_rates', methods=['GET', 'POST'])
def admin_rates():
    if request.method == 'POST':
        new_text = request.form.get('new_rates')
        rates_collection.update_one({"type": "headline"}, {"$set": {"text": new_text}}, upsert=True)
        return "<h2>Update Successful!</h2><a href='/'>Go Home</a>"
    return '''<form method="post" style="padding:50px;"><textarea name="new_rates" style="width:100%;height:100px;"></textarea><br><button type="submit">Update</button></form>'''

@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

app = app

if __name__ == '__main__':
    app.run(debug=True)
