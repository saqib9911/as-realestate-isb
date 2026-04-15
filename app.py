from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from pymongo import MongoClient
from urllib.parse import quote_plus

app = Flask(__name__)

# --- SECURE CLOUD CONNECTION ---
# Is password ko apni jagah rehne dein agar ye theek hai
user = "saqibzaheersattirocklight_db_user"
password = "DsUTBwyxsi5sdYf2" 
encoded_password = quote_plus(password)

# Final MongoDB String
MONGO_URI = f"mongodb+srv://{user}:{encoded_password}@cluster0.vvzewi4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    # Connection logic with 5s timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client['realestate_db']
    collection = db['properties']
    rates_collection = db['live_rates']
    
    # Test if database is alive
    client.admin.command('ping')
    print(">>> CLOUD DATABASE CONNECTED SUCCESSFULLY <<<")
except Exception as e:
    print(f"!!! DATABASE CONNECTION ERROR: {e} !!!")

@app.route('/')
def index():
    """Main Website Route"""
    try:
        # Fetching latest rates for the marquee
        rates_data = rates_collection.find_one({"type": "headline"})
        current_rates = rates_data['text'] if rates_data else "A&S Management: Professional Property Solutions in Islamabad"
        return render_template('index.html', rates=current_rates)
    except:
        return render_template('index.html', rates="Connecting to live market...")

@app.route('/get_properties')
def get_properties():
    """Fetching properties for the frontend grid"""
    try:
        # Sorting by newest first
        props = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(props)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/save_property', methods=['POST'])
def save_property():
    """Adding new property to MongoDB Cloud"""
    try:
        new_property = {
            "title": request.form.get('title'),
            "price": request.form.get('price'),
            "area": request.form.get('area'),
            "map": request.form.get('map', '#'),
            "video": request.form.get('video', '#'),
            "type": "Premium"
        }
        # Insert into cloud collection
        collection.insert_one(new_property)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin_rates', methods=['GET', 'POST'])
def admin_rates():
    """Secret Page to update the live marquee rates"""
    if request.method == 'POST':
        new_text = request.form.get('new_rates')
        if new_text:
            rates_collection.update_one(
                {"type": "headline"},
                {"$set": {"text": new_text}},
                upsert=True
            )
            return "<h2>SUCCESS! Market Rates Updated.</h2><br><a href='/'>Go to Website</a>"
    
    return '''
    <body style="background:#0f172a; color:white; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0;">
        <div style="background:rgba(255,255,255,0.05); padding:40px; border-radius:30px; border:1px solid rgba(255,255,255,0.1); width:90%; max-width:500px; text-align:center;">
            <h2 style="color:#00ffcc;">A&S Management Admin</h2>
            <p style="opacity:0.7; margin-bottom:20px;">Type the new live rates for the marquee headline below:</p>
            <form method="post">
                <textarea name="new_rates" placeholder="e.g. Gold: 220k | Dollar: 282 | DHA Phase 4 Rates Up!" 
                style="width:100%; height:120px; border-radius:15px; padding:15px; background:#1e293b; color:white; border:1px solid #334155; outline:none; font-size:1rem;"></textarea>
                <br><br>
                <button type="submit" style="width:100%; padding:18px; border-radius:15px; border:none; background:#00ffcc; color:#000; font-weight:bold; font-size:1rem; cursor:pointer; transition:0.3s;">UPDATE LIVE WEBSITE</button>
            </form>
            <p style="margin-top:20px;"><a href="/" style="color:white; text-decoration:none; opacity:0.5;">Cancel and go back</a></p>
        </div>
    </body>
    '''

# --- PWA SERVICE HANDLERS ---
@app.route('/sw.js')
def sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/manifest.json')
def manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

# Vercel entry point
app = app

if __name__ == '__main__':
    app.run(debug=True)
