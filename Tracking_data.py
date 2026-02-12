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
    """Convert HH:mm:ss to seconds"""
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return 0

def seconds_to_time(seconds):
    """Convert seconds to HH:mm:ss"""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"
 
@app.route('/AppTrack', methods=['POST'])
def call_Tracking_data():
    return submit_tracking()
 
def submit_tracking():
    try:
        data = request.get_json()
        
        doctype = data.get('module')
        values = data.get('values', {})
        access_token = data.get('access_token')
        useruniqueid = data.get('useruniqueid')
        
        if not doctype or not values or not access_token:
            return {
                "success": False,
                "message": "Missing doctype, values, or access_token"
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
        
        full_name = user_info_response.json().get('data', {}).get('full_name', employee_username)
        
        app_name = ""
        app_id = values.get("application_id")
        if app_id:
            app_response = requests.get(f"{ERP_URL}/api/resource/Applications/{app_id}", headers=headers)
            if app_response.status_code == 200:
                app_name = app_response.json().get('data', {}).get('app_name', "")
        
        event_name = ""
        event_id = values.get("event_id")
        if event_id:
            event_response = requests.get(f"{ERP_URL}/api/resource/Event/{event_id}", headers=headers)
            if event_response.status_code == 200:
                event_name = event_response.json().get('data', {}).get('subject', "")
        
        # Find today's record (using IST timezone)
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).strftime('%Y-%m-%d')
        filters = [
            ["employee","=",employee_username],
            ["applications","=",app_name],
            ["creation","like",f"{today}%"]
        ]
        search = requests.get(
            f"{ERP_URL}/api/resource/{doctype}?filters={json.dumps(filters)}",
            headers=headers
        )
        existing = None
        if search.status_code==200:
            rows = search.json().get("data",[])
            if rows:
                existing = rows[0]
 
        headers["Content-Type"] = "application/json"
        
        # Handle window_title accumulation
        new_window_title = values.get("window_title", "").strip()
        
        if existing:
            name = existing["name"]
            full_rec = requests.get(f"{ERP_URL}/api/resource/{doctype}/{name}", headers=headers)
            if full_rec.status_code!=200:
                return {"success":False,"message":"Failed fetch","error":full_rec.text},500
            cd = full_rec.json()["data"]
            
            # Get existing window titles
            existing_window_titles = cd.get("window_title", "").strip()
            
            # Combine window titles
            if existing_window_titles:
                # Split existing titles and check if new title already exists
                existing_titles_list = [title.strip() for title in existing_window_titles.split(',')]
                if new_window_title and new_window_title not in existing_titles_list:
                    combined_window_title = f"{existing_window_titles}, {new_window_title}"
                else:
                    combined_window_title = existing_window_titles
            else:
                combined_window_title = new_window_title
            
            # Accumulate duration instead of replacing
            existing_duration = cd.get("duration", "00:00:00")
            new_duration = values.get("duration", "00:00:00")
            
            # Convert to seconds, add, and convert back
            total_seconds = time_to_seconds(existing_duration) + time_to_seconds(new_duration)
            accumulated_duration = seconds_to_time(total_seconds)
            
            # Accumulate idle duration as well
            existing_idle = cd.get("idle_duration", "00:00:00")
            new_idle = values.get("idleduration", "00:00:00")
            total_idle_seconds = time_to_seconds(existing_idle) + time_to_seconds(new_idle)
            accumulated_idle = seconds_to_time(total_idle_seconds)
            
            cd.update({
                "name1": full_name,
                "duration": accumulated_duration,
                "idle_duration": accumulated_idle,
                "window_title": combined_window_title,
                "application_id": app_id,
                "event_id": event_id,
                "applications": app_name,
                "event_name": event_name,
                "employee": employee_username,
                "category": app_name  # Auto-populate category with application name
            })
            response = requests.put(f"{ERP_URL}/api/resource/{doctype}/{name}",
                                 headers=headers, data=json.dumps(cd))
        else:
            payload = {
                "name1": full_name,
                "duration": values.get("duration"),
                "idle_duration": values.get("idleduration"),
                "application_id": app_id,
                "event_id": event_id,
                "applications": app_name,
                "event_name": event_name,
                "window_title": new_window_title,
                "employee": employee_username,
                "category": app_name  # Auto-populate category with application name
            }
            response = requests.post(f"{ERP_URL}/api/resource/{doctype}", headers=headers, data=json.dumps(payload))
 
        if response.status_code in (200, 201):
            saved_data = response.json().get("data", {})
            return {
                "success": True,
                "result": {
                   "record": {
                    "id": saved_data.get("name")
                    }
                }
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
    # Use 0.0.0.0 to allow access from network (including localhost)
    # Change to specific IP when deploying to server
    app.run(debug=True, host='0.0.0.0', port=5000)