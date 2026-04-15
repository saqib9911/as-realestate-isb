from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient

app = Flask(__name__)

# --- MONGODB CONNECTION ---
# Password laazmi <db_password> ki jagah likhein
MONGO_URI = "mongodb+srv://saqibzaheersattirocklight_db_user:<DsUTBwyxsi5sdYf2>@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['realestate_db']
    collection = db['properties']
    rates_collection = db['live_rates'] # Naya feature: Rates ke liye
    client.admin.command('ping')
    print("MongoDB Connected Successfully!")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

@app.route('/')
def index():
    # Database se latest headline rates uthana
    rates_data = rates_collection.find_one({"type": "headline"})
    current_rates = rates_data['text'] if rates_data else "Market Updates Coming Soon..."
    return render_template('index.html', rates=current_rates)

@app.route('/get_properties')
def get_properties():
    try:
        props = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(props)
    except Exception as e:
        return jsonify([])

@app.route('/save_property', methods=['POST'])
def save_property():
    try:
        new_data = {
            "title": request.form.get('title'),
            "price": request.form.get('price'),
            "area": request.form.get('area'),
            "type": request.form.get('type'),
            "map": request.form.get('map'),
            "video": request.form.get('video'),
            "img": "https://via.placeholder.com/400x250"
        }
        collection.insert_one(new_data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ADMIN PANEL: Headline update karne ke liye
@app.route('/admin_rates', methods=['GET', 'POST'])
def admin_rates():
    if request.method == 'POST':
        new_text = request.form.get('new_rates')
        rates_collection.update_one({"type": "headline"}, {"$set": {"text": new_text}}, upsert=True)
        return "<h2>Update Successful!</h2><a href='/'>Go to App</a>"
    return '''
        <body style="background:#0f172a; color:white; font-family:sans-serif; padding:20px; text-align:center;">
            <h2>A&S Management Admin</h2>
            <form method="post">
                <p>Type New Headline Below:</p>
                <textarea name="new_rates" style="width:90%; height:100px; padding:10px; border-radius:10px;"></textarea><br><br>
                <button type="submit" style="padding:15px 30px; background:#00ffcc; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">Update Marquee</button>
            </form>
        </body>
    '''

@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

app = app

if __name__ == '__main__':
    app.run(debug=True)
