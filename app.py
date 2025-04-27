from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random
from collections import Counter

app = Flask(__name__)
CORS(app)  # Allow CORS

# ------------------ CONFIG ------------------
WEEKENDS = [5, 6]  # Saturday=5, Sunday=6

# ------------------ FUNCTIONS ------------------

def is_conflict(date_to_check, consultations):
    """Check if the date conflicts with existing consultations."""
    for consultation in consultations:
        start_date = consultation.get('start_date')
        end_date = consultation.get('end_date') or start_date  # fallback if end_date is None

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        if start <= date_to_check <= end:
            return True
    return False

def find_high_complaint_dates(consultations, threshold=3):
    """Find dates where complaints exceed a threshold."""
    date_counter = Counter()

    for consultation in consultations:
        start_date = consultation.get('start_date')
        if start_date:
            date_counter[start_date] += 1

    high_complaint_dates = [date for date, count in date_counter.items() if count > threshold]
    return high_complaint_dates

def suggest_available_dates(consultations, holidays):
    """Suggest available consultation dates based on complaints and holidays."""
    today = datetime.today()
    search_start = today + timedelta(days=7)
    search_end = today + timedelta(days=14)

    available_dates = []
    current_date = search_start

    while current_date <= search_end:
        date_str = current_date.strftime('%Y-%m-%d')

        if (
            date_str not in holidays and
            current_date.weekday() not in WEEKENDS and
            not is_conflict(current_date, consultations)
        ):
            available_dates.append(date_str)

        current_date += timedelta(days=1)

    return available_dates

# ------------------ API ROUTE ------------------

@app.route('/suggest_date', methods=['POST'])
def suggest_date():
    """API Endpoint to suggest date based on posted complaint data."""
    data = request.get_json()

    consultations = data.get('consultations', [])
    holidays = data.get('holidays', [])

    high_complaint_dates = find_high_complaint_dates(consultations, threshold=3)
    available_dates = suggest_available_dates(consultations, holidays)

    if high_complaint_dates:
        return jsonify({
            'success': True,
            'suggested_action': 'Create Consultation Event',
            'high_complaint_dates': high_complaint_dates,
            'message': f'Dates with high complaint volume detected: {", ".join(high_complaint_dates)}. Suggest scheduling a consultation event.'
        })
    elif available_dates:
        best_date = random.choice(available_dates)
        return jsonify({
            'success': True,
            'suggested_date': best_date,
            'message': 'Suggested date generated successfully.'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No available dates found. Please try again later.'
        })

# ------------------ MAIN ------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
