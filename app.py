# app.py — ROBUST WITH REAL FLIGHT CALLS (TRAVELPAYOUTS) AND MOCK FALLBACK
from flask import Flask, request, render_template_string
import requests
import datetime

app = Flask(__name__)

TRAVELPAYOUTS_TOKEN = '35651821b8771a0780673b5c05b06d4c'  # Paste your TravelPayouts token (get from travelpayouts.com/developers/api)

# === REAL FLIGHTS (TRAVELPAYOUTS API WITH ROBUST FALLBACK) ===
def get_flights(origin, dest, date_str):
    try:
        print(f"Fetching real flights: {origin} → {dest} on {date_str}")
        url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
        params = {
            'origin': origin,
            'destination': dest,
            'departure_at': date_str,
            'currency': 'GBP',
            'token': TRAVELPAYOUTS_TOKEN,
            'limit': 3,
            'one_way': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise if bad status
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            flights = []
            for item in data['data']:
                airline = item.get('airline', 'Unknown')
                flight_num = item.get('flight_number', 'N/A')
                status = 'Available'
                price = f"£{item.get('price', 100)}"
                duration_min = item.get('duration', 150)
                duration = f"{duration_min // 60}h {duration_min % 60}m"
                flights.append({
                    'airline': airline,
                    'flight': flight_num,
                    'price': price,
                    'duration': duration,
                    'status': status
                })
            print(f"REAL FLIGHTS FOUND: {len(flights)}")
            return flights
        else:
            print("No flights from API (date may be too far or no schedules) — using mock.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err} (check token or limits) — using mock.")
    except Exception as e:
        print(f"API Error: {e} — using mock.")
    
    # MOCK FALLBACK
    return [
        {"airline": "British Airways", "flight": "BA730", "price": "£145", "duration": "2h 30m", "status": "Scheduled"},
        {"airline": "easyJet", "flight": "U22433", "price": "£89", "duration": "2h 45m", "status": "Available"},
        {"airline": "Swiss", "flight": "LX345", "price": "£198", "duration": "1h 50m", "status": "On Time"}
    ]

# === RESORTS ===
def get_ski_resorts(skill, budget):
    resorts = [
        {"name": "Chamonix", "country": "France", "skill": "Advanced", "cost": 850, "vibe": "Extreme off-piste with Mont Blanc views"},
        {"name": "Courchevel", "country": "France", "skill": "Intermediate", "cost": 1200, "vibe": "Luxury slopes and fine dining"},
        {"name": "Val Thorens", "country": "France", "skill": "All Levels", "cost": 950, "vibe": "Europe's highest resort, snow-sure all season"},
        {"name": "St Anton", "country": "Austria", "skill": "Advanced", "cost": 780, "vibe": "Legendary après-ski and challenging terrain"},
        {"name": "Zermatt", "country": "Switzerland", "skill": "Intermediate", "cost": 1400, "vibe": "Car-free village with Matterhorn magic"}
    ]
    filtered = [r for r in resorts if skill in r["skill"] and r["cost"] <= budget]
    if not filtered:
        print("No resorts found for skill/budget; using fallback.")
    return filtered

# === TRAINS ===
def get_trains(resort):
    trains = {
        "Chamonix": {"route": "Eurostar → Paris → Chamonix", "price": "£95", "duration": "7h 30m"},
        "Courchevel": {"route": "Eurostar → Moûtiers (bus to resort)", "price": "£110", "duration": "8h 15m"},
        "Val Thorens": {"route": "Eurostar → Moûtiers (bus to resort)", "price": "£105", "duration": "8h 0m"},
        "St Anton": {"route": "Eurostar → Zurich → St Anton", "price": "£120", "duration": "9h 0m"},
        "Zermatt": {"route": "Eurostar → Geneva → Zermatt", "price": "£130", "duration": "9h 30m"}
    }
    train = trains.get(resort, {})
    if not train:
        print("No train found for resort; using fallback.")
    return train

# === HOTELS ===
def get_accommodation(resort, nights=5):
    hotels = {
        "Chamonix": [
            {"name": "Hotel Mont Blanc", "price_night": 180, "rating": 4.6},
            {"name": "Auberge du Bois Prin", "price_night": 240, "rating": 4.9}
        ],
        "Courchevel": [
            {"name": "Le Lana", "price_night": 450, "rating": 5.0},
            {"name": "Hotel Les Suites", "price_night": 320, "rating": 4.7}
        ],
        "Val Thorens": [
            {"name": "Altapura", "price_night": 300, "rating": 4.8},
            {"name": "Fitz Roy", "price_night": 350, "rating": 4.9}
        ],
        "St Anton": [
            {"name": "Mooser Hotel", "price_night": 280, "rating": 4.7},
            {"name": "Raffl's St. Antoner Hof", "price_night": 400, "rating": 5.0}
        ],
        "Zermatt": [
            {"name": "Mont Cervin Palace", "price_night": 380, "rating": 4.9},
            {"name": "Riffelalp Resort", "price_night": 450, "rating": 5.0}
        ]
    }
    base_hotels = hotels.get(resort, [])
    if not base_hotels:
        print("No hotels found for resort; using fallback.")
    return [
        {
            "name": h["name"],
            "price": f"£{h['price_night'] * nights}",
            "per_night": f"£{h['price_night']}",
            "rating": h["rating"]
        } for h in base_hotels[:2]
    ]

# === AI TIP ===
def ai_tip(skill, resort):
    tips = {
        "Advanced": f"For {skill} skiers, {resort} has world-class off-piste — rent a guide for safety!",
        "Intermediate": f"{resort} is ideal for {skill} skiers with perfect blue/red runs and progression areas.",
        "Beginner": f"Great for {skill} skiers! {resort} has gentle nursery slopes and English-speaking instructors."
    }
    tip = tips.get(skill, "Enjoy the snow and stay safe!")
    return tip

# === HTML ===
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Ski Trip Planner</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel=stylesheet>
</head>
<body class="container mt-5">
  <h1>Plan Your Ski Holiday</h1>
  <form method="post">
    <div class="mb-3"><label>From UK Airport:</label><input type="text" name="origin" class="form-control" value="LHR"></div>
    <div class="mb-3"><label>Dest Airport:</label><input type="text" name="dest" class="form-control" value="GVA"></div>
    <div class="mb-3"><label>Date:</label><input type="date" name="date" class="form-control"></div>
    <div class="mb-3"><label>Skill Level:</label><select name="skill" class="form-select"><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
    <div class="mb-3"><label>Budget (£):</label><input type="number" name="budget" class="form-control" value="1000"></div>
    <button type="submit" class="btn btn-primary">Search!</button>
  </form>
  {% if flights %}
  <h2>Your Itinerary</h2>
  <h3>Flights:</h3><ul>{% for f in flights %}<li>{{ f.airline }} {{ f.flight }} - {{ f.price }} ({{ f.duration }}) - {{ f.status }}</li>{% endfor %}</ul>
  <h3>Trains:</h3><ul>{% if trains %}<li>{{ trains.route }} - {{ trains.price }} ({{ trains.duration }})</li>{% endif %}</ul>
  <h3>Best Spot:</h3><ul>{% if resort %}<li>{{ resort.name }} - {{ resort.vibe }} (Under budget!)</li>{% endif %}</ul>
  <h3>Accom:</h3><ul>{% for a in accom %}<li>{{ a.name }} - {{ a.per_night }}/night ({{ a.rating }} stars) - Total {{ a.price }}</li>{% endfor %}</ul>
  <h3>AI Tip:</h3><p>{{ ai_rec }}</p>
  {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        origin = request.form['origin']
        dest = request.form['dest']
        date = request.form['date']
        skill = request.form['skill']
        budget = int(request.form['budget'])
        flights = get_flights(origin, dest, date)
        resorts = get_ski_resorts(skill, budget)
        resort = resorts[0] if resorts else None
        trains = get_trains(resort["name"]) if resort else {}
        accom = get_accommodation(resort["name"]) if resort else []
        ai_rec = ai_tip(skill, resort["name"]) if resort else "No resorts found. Try adjusting your budget or skill level."
        return render_template_string(HTML, flights=flights, trains=trains, resort=resort, accom=accom, ai_rec=ai_rec)
    return render_template_string(HTML)

if __name__ == '__main__':
   # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)  # Use 0.0.0.0 for Render; debug=False for production
