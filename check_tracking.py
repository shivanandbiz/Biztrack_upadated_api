from flask import Flask, request, jsonify
import jwt
import requests
from datetime import date

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"
API_KEY = 'a886902c5c72450'
API_SECRET = '6febe12f6f56698'
JWT_SECRET = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

HEADERS = {
    'Authorization': f'token {API_KEY}:{API_SECRET}',
    'Content-Type': 'application/json'
}

@app.route('/checkTrackingStart', methods=['POST'])
def call_check_tracking():
    return check_tracking_start()
def check_tracking_start():
    data = request.get_json()
    access_token = data.get('access_token')
    user_id = data.get('useruniqueid')

    try:
        decoded = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        if str(decoded.get("userid")) != str(user_id):
            return jsonify({
                "success": False,
                "result": {
                    "trackingId": "",
                    "applications": []
                },
                "successMessage": "User ID mismatch in token"
            }), 403
    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "result": {
                "trackingId": "",
                "applications": []
            },
            "successMessage": "Token expired"
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            "success": False,
            "result": {
                "trackingId": "",
                "applications": []
            },
            "successMessage": "Invalid access token"
        }), 401

    today = date.today().isoformat()
    result = {
        "trackingId": "",
        "applications": []
    }

    activity_url = f"{ERP_URL}/api/resource/Event"
    params = {
        'fields': '["name"]',
        'filters': f'[["Event", "status", "=", "Tracking Started"],'
                   f'["Event", "starts_on", "=", "{today}"],'
                   f'["Event", "custom_assign_user_id", "=", "{user_id}"]]',
        'limit_page_length': 1,
        'order_by': 'creation desc'
    }

    activity_res = requests.get(activity_url, headers=HEADERS, params=params)
    activity_data = activity_res.json()

    if activity_data.get('data'):
        activity_id = activity_data['data'][0]['name']
        result['trackingId'] = f"TRK{activity_id}"

        app_track_url = f"{ERP_URL}/api/resource/Applications Tracking"
        params = {
            'fields': '["application_id", "duration", "idleduration"]',
            'filters': f'[["Applications Tracking","event_id","=","{activity_id}"]]'
        }

        app_track_res = requests.get(app_track_url, headers=HEADERS, params=params)
        app_tracking = app_track_res.json().get('data', [])

        for app in app_tracking:
            app_name_res = requests.get(
                f'{ERP_URL}/api/resource/Applications/{app["application_id"]}',
                headers=HEADERS
            )
            app_name = app_name_res.json().get('data', {}).get('application_name', '')

            result['applications'].append({
                "ProcessName": app_name,
                "AppTrackingId": app["application_id"],
                "TrackedTime": app["duration"],
                "IdleTime": app["idleduration"]
            })

        return jsonify({
            "success": True,
            "result": result,
            "successMessage": "Tracking data fetched successfully"
        })

    else:
        return jsonify({
            "success": True,
            "result": result,
            "successMessage": "No tracking session found for today"
        })

if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)