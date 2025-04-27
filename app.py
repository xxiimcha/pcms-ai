from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random
from collections import Counter, defaultdict

app = Flask(__name__)
CORS(app)

# ------------------ CONFIG ------------------
WEEKENDS = [5, 6]

# ------------------ FUNCTIONS ------------------

def is_conflict(date_to_check, consultations):
    for consultation in consultations:
        start_date = consultation.get('start_date')
        end_date = consultation.get('end_date') or start_date

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        if start <= date_to_check <= end:
            return True
    return False

def find_high_complaint_dates_and_types(consultations, threshold=3):
    """Find dates and types where complaints exceed threshold."""
    date_type_counter = defaultdict(Counter)

    for consultation in consultations:
        start_date = consultation.get('start_date')
        complaint_type = consultation.get('type', 'Unknown')
        if start_date:
            date_type_counter[start_date][complaint_type] += 1

    high_complaints_info = []
    for date, types in date_type_counter.items():
        for complaint_type, count in types.items():
            if count > threshold:
                high_complaints_info.append({
                    'date': date,
                    'type': complaint_type,
                    'count': count
                })
    return high_complaints_info

def suggest_available_dates(consultations, holidays):
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
    data = request.get_json()

    consultations = data.get('consultations', [])
    holidays = data.get('holidays', [])

    high_complaints_info = find_high_complaint_dates_and_types(consultations, threshold=3)
    available_dates = suggest_available_dates(consultations, holidays)

    if high_complaints_info:
        messages = [
            f"{info['date']} — {info['type']} — {info['count']} complaints"
            for info in high_complaints_info
        ]
        return jsonify({
            'success': True,
            'suggested_action': 'Create Consultation Event',
            'high_complaints_info': high_complaints_info,
            'message': "High complaint volume detected:<br>" + "<br>".join(messages)
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
