from flask import Flask, request
import requests
import jwt
import json
 
app = Flask(__name__)
 
ERP_URL = "http://164.52.192.194:8000/"
API_KEY = "a886902c5c72450:6febe12f6f56698"
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'
 
@app.route('/saveTracking', methods=['POST'])
def call_tracking_start_event():
    return Tracking_Event()

def Tracking_Event():
    try:
        data = request.get_json()
       
        doctype = data.get('module')  # Should be "Applications Tracking"
        values = data.get('values', {})
        access_token = data.get('access_token')
        record_id = data.get('useruniqueid')  # Existing record ID for updates

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
        user_info_url = f"{ERP_URL}api/resource/User/{employee_username}"
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code != 200:
            return {"success": False, "message": "User not found in ERP"}, 404
       
        user_data = user_info_response.json().get('data', {})
        employee_name = user_data.get('full_name', employee_username)
       
        # Build payload for Applications Tracking doctype
        payload = {
            "duration": values.get("duration"),  # HH:mm:ss format (e.g., "00:00:10")
            "idleduration": values.get("idleduration", "00:00:00"),
            "application_id": values.get("application_id"),  # Link to Applications doctype
            "event_id": values.get("event_id"),  # Link to Event (tracking session)
            "window_title": values.get("window_title", ""),
            "employee": employee_username,
            "employee_name": employee_name
        }

        headers["Content-Type"] = "application/json"
       
        # Update existing record or create new
        if record_id:
            # Update existing Applications Tracking record
            response = requests.put(
                f"{ERP_URL}api/resource/{doctype}/{record_id}",
                headers=headers,
                data=json.dumps(payload)
            )
        else:
            # Create new Applications Tracking record
            response = requests.post(
                f"{ERP_URL}api/resource/{doctype}",
                headers=headers,
                data=json.dumps(payload)
            )

        if response.status_code == 200:
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