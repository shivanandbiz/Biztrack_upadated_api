from flask import Flask, request
import requests
import jwt
import json
from datetime import datetime
import pytz

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000"
API_KEY = "a886902c5c72450:6febe12f6f56698"
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

# Helper functions for duration calculation
def time_to_seconds(time_str):
    """Convert HH:mm:ss to seconds (Robust)"""
    if not time_str:
        return 0
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = map(float, parts)
            return int(h * 3600 + m * 60 + s)
        return 0
    except Exception as e:
        print(f"Time conversion error for {time_str}: {e}")
        return 0

def seconds_to_time(seconds):
    """Convert seconds to HH:mm:ss"""
    seconds = int(seconds) # Ensure int
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

@app.route('/saveTracking', methods=['POST'])
def call_tracking_start_event():
    return Tracking_Event()

def Tracking_Event():
    try:
        data = request.get_json()
        
        doctype = data.get('module')  # Should be "Applications Tracking"
        values = data.get('values', {})
        access_token = data.get('access_token')
        record_id = data.get('record')  # Correct key from crmapi.js

        if not values or not access_token:
            return {
                "success": False,
                "message": "Missing values or access_token"
            }, 400

        try:
            decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            employee_username = decoded_token.get("user")
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Access token expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid access token"}, 401

        headers = {"Authorization": f"token {API_KEY}"}
        user_info_url = f"{ERP_URL}/api/resource/User/{employee_username}"
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return {"success": False, "message": "User not found in ERP"}, 404
        
        user_data = user_info_response.json().get('data', {})
        employee_name = user_data.get('full_name', employee_username)
        
        # 1. Fetch Application Name
        app_name = ""
        app_id = values.get("application_id")
        if app_id:
            app_response = requests.get(f"{ERP_URL}/api/resource/Applications/{app_id}", headers=headers)
            if app_response.status_code == 200:
                app_name = app_response.json().get('data', {}).get('app_name', "")

        # 2. Fetch Event Name
        event_name = ""
        event_id = values.get("event_id")
        if event_id:
            event_response = requests.get(f"{ERP_URL}/api/resource/Event/{event_id}", headers=headers)
            if event_response.status_code == 200:
                event_name = event_response.json().get('data', {}).get('subject', "")
        
        # 3. Set Dates
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).strftime('%Y-%m-%d')

        headers["Content-Type"] = "application/json"
        
        # Update existing record or create new
        if record_id:
            # Fetch existing record for accumulation
            full_rec = requests.get(f"{ERP_URL}/api/resource/{doctype}/{record_id}", headers=headers)
            if full_rec.status_code == 200:
                cd = full_rec.json()["data"]
                
                # Window Title Accumulation
                existing_window_titles = cd.get("window_title", "").strip()
                new_window_title = values.get("window_title", "").strip()
                combined_window_title = existing_window_titles
                
                if new_window_title:
                    if existing_window_titles:
                        existing_titles_list = [t.strip() for t in existing_window_titles.split(',')]
                        if new_window_title not in existing_titles_list:
                            combined_window_title = f"{existing_window_titles}, {new_window_title}"
                    else:
                        combined_window_title = new_window_title

                # Duration Accumulation
                existing_duration = cd.get("duration", "00:00:00")
                new_duration = values.get("duration", "00:00:00")
                total_seconds = time_to_seconds(existing_duration) + time_to_seconds(new_duration)
                accumulated_duration = seconds_to_time(total_seconds)

                # Idle Accumulation
                existing_idle = cd.get("idle_duration", "00:00:00")
                new_idle = values.get("idleduration", "00:00:00")
                total_idle_seconds = time_to_seconds(existing_idle) + time_to_seconds(new_idle)
                accumulated_idle = seconds_to_time(total_idle_seconds)

                payload = {
                    "duration": accumulated_duration,
                    "idle_duration": accumulated_idle,
                    "window_title": combined_window_title,
                    "applications": app_name,
                    "event_name": event_name or f"Event {event_id}", # Fallback
                    "employee": employee_username,
                    "employee_name": employee_name,
                    "name1": employee_name, # Map Employee Name to 'Name' field
                    "from_date": today,
                    "to_date": today,
                    "category": app_name
                }
                
                response = requests.put(
                    f"{ERP_URL}/api/resource/{doctype}/{record_id}",
                    headers=headers,
                    data=json.dumps(payload)
                )
            else:
                 return {"success": False, "message": "Record not found for update"}, 404
        else:
            # Create new Applications Tracking record
            payload = {
                "duration": values.get("duration", "00:00:00"),
                "idle_duration": values.get("idleduration", "00:00:00"),
                "application_id": app_id,
                "event_id": event_id,
                "window_title": values.get("window_title", ""),
                "employee": employee_username,
                "employee_name": employee_name,
                "name1": employee_name, # Map Employee Name to 'Name' field
                "applications": app_name,
                "event_name": event_name or f"Event {event_id}", # Fallback
                "from_date": today,
                "to_date": today,
                "category": app_name
            }
            response = requests.post(
                f"{ERP_URL}/api/resource/{doctype}",
                headers=headers,
                data=json.dumps(payload)
            )

        if response.status_code in (200, 201):
            resp_data = response.json()
            return {
                "success": True,
                "message": "Tracking data saved successfully",
                "result": {"record": resp_data.get('data', {})},
            }, 200
        else:
            return {
                "success": False,
                "message": "Failed to submit to ERP",
                "error": response.text
            }, response.status_code
        
    except Exception as e:
        return {
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }, 500

if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)