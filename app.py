from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# ------------------ CONFIG ------------------
WEEKENDS = [5, 6]  # Saturday=5, Sunday=6

# ------------------ FUNCTIONS ------------------

def is_conflict(date_to_check, consultations):
    """Check if the date conflicts with existing consultations."""
    for consultation in consultations:
        start = datetime.strptime(consultation['start_date'], '%Y-%m-%d')
        end = datetime.strptime(consultation['end_date'], '%Y-%m-%d')
        if start <= date_to_check <= end:
            return True
    return False

def suggest_available_dates(consultations, holidays):
    """Suggest available consultation dates based on data passed from PHP."""
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
    """API Endpoint to suggest date based on posted consultation and holiday data."""
    data = request.get_json()

    consultations = data.get('consultations', [])
    holidays = data.get('holidays', [])

    available_dates = suggest_available_dates(consultations, holidays)

    if available_dates:
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
