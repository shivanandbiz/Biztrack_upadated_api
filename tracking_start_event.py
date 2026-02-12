# from flask import Flask, request, jsonify
# import requests
# import jwt
# import json
# from datetime import datetime, time, timedelta
# import pytz
 
# app = Flask(__name__)
 
# ERP_URL = "http://164.52.192.194:8000"
# API_KEY = "a886902c5c72450:6febe12f6f56698"
# SECRET_KEY = "8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y"
 
# def get_auth_headers():
#     return {
#         "Authorization": f"token {API_KEY}",
#         "Content-Type": "application/json"
#     }
 
# def get_today_timesheet(user):
#     today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
#     url = f"{ERP_URL}/api/resource/Timesheet"
#     params = {
#         "fields": '["name"]',
#         "filters": f'[["user","=", "{user}"], ["start_date","=", "{today}"]]'
#     }
#     res = requests.get(url, headers=get_auth_headers(), params=params)
#     res.raise_for_status()
#     data = res.json().get("data", [])
#     return data[0]["name"] if data else None
 
# def generate_time_logs():
#     ist = pytz.timezone("Asia/Kolkata")
#     today = datetime.now(ist).date()
#     base = datetime.combine(today, time(10, 0))
#     slots = []
#     for i in range(9):
#         frm = base + timedelta(hours=i)
#         to  = frm + timedelta(hours=1)
#         slots.append({
#             "from_time": frm.isoformat(),
#             "to_time": to.isoformat(),
#             "event": ""
#         })
#     return slots
 
# def create_timesheet(user):
#     today = datetime.now(pytz.timezone("Asia/Kolkata")).date().isoformat()
#     payload = {
#         "user": user,
#         "start_date": today,
#         "time_logs": generate_time_logs()
#     }
#     url = f"{ERP_URL}/api/resource/Timesheet"
#     res = requests.post(url, headers=get_auth_headers(), json=payload)
#     res.raise_for_status()
#     return res.json()["data"]["name"]
 
# def get_timesheet_doc(name):
#     url = f"{ERP_URL}/api/resource/Timesheet/{name}"
#     res = requests.get(url, headers=get_auth_headers())
#     res.raise_for_status()
#     return res.json()["data"]
 
# def update_timesheet_event(timesheet_doc, event_subject):
#     ist = pytz.timezone("Asia/Kolkata")
#     now = datetime.now(ist)
#     for row in timesheet_doc.get("time_logs", []):
#         try:
#             frm = datetime.fromisoformat(row["from_time"])
#             to = datetime.fromisoformat(row["to_time"])
#             frm = ist.localize(frm) if frm.tzinfo is None else frm.astimezone(ist)
#             to = ist.localize(to) if to.tzinfo is None else to.astimezone(ist)
#         except Exception:
#             continue
#         if frm <= now < to:
#             existing_event = row.get("event", "").strip()
#             if existing_event:
#                 events = [e.strip() for e in existing_event.split(",")]
#                 if event_subject not in events:
#                     events.append(event_subject)
#                 row["event"] = ", ".join(events)
#             else:
#                 row["event"] = event_subject
#             return True
#     return False
 
# def save_timesheet(name, timesheet_doc):
#     url = f"{ERP_URL}/api/resource/Timesheet/{name}"
#     res = requests.put(url, headers=get_auth_headers(),
#                        json={"time_logs": timesheet_doc["time_logs"]})
#     res.raise_for_status()
#     return res.json()
 
# @app.route('/saveTracking', methods=['POST'])
# def call_tracking_start_event():
#     return Tracking_Event()
 
# def Tracking_Event():
#     try:
#         data = request.get_json()
#         doctype = data.get('module')
#         values = data.get('values', {})
#         access_token = data.get('access_token')
#         useruniqueid = data.get("useruniqueid")
 
#         if not values or not access_token:
#             return jsonify({
#                 "success": False,
#                 "message": "Missing values or access_token"
#             }), 400
 
#         try:
#             decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
#             employee_username = decoded_token.get("user")
#         except jwt.ExpiredSignatureError:
#             return jsonify({"success": False, "message": "Access token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"success": False, "message": "Invalid access token"}), 401
 
#         headers = get_auth_headers()
       
#         user_info_url = f"{ERP_URL}/api/resource/User/{employee_username}"
#         user_info_response = requests.get(user_info_url, headers=headers)
 
#         if user_info_response.status_code != 200:
#             return jsonify({"success": False, "message": "User not found in ERP"}), 404
 
#         payload = {
#             "subject": values.get("subject"),
#             "status": values.get("activitytype"),
#             "custom_assign_user_id": values.get("assigned_user_id")
#         }
 
#         response = requests.post(f"{ERP_URL}/api/resource/{doctype}", headers=headers, json=payload)
 
#         if response.status_code != 200:
#             return jsonify({
#                 "success": False,
#                 "message": "Failed to submit to ERP",
#                 "error": response.text
#             }), response.status_code
 
#         ts_name = get_today_timesheet(employee_username) or create_timesheet(employee_username)
#         ts_doc = get_timesheet_doc(ts_name)
 
#         updated = update_timesheet_event(ts_doc, values.get("subject"))
#         if not updated:
#             return jsonify({
#                 "success": False,
#                 "message": "No matching 1-hour time slot found in timesheet"
#             }), 400
 
#         saved = save_timesheet(ts_name, ts_doc)
#         today_str = datetime.now(pytz.timezone("Asia/Kolkata")).date().isoformat()
 
#         return jsonify({
#             "success": True,
#             "message": f"Tracking event updated and logged to timesheet for user '{employee_username}' on {today_str}",
#             "tracking_event": response.json().get("data", {}),
#             "timesheet_name": saved.get("data", {}).get("name"),
#         }), 200
 
#     except Exception as e:
#         return jsonify({
#             "success": False,
#             "message": "Internal Server Error",
#             "error": str(e)
#         }), 500
 
# if __name__ == '__main__':
#     app.run(debug=True, host='164.52.192.194', port=5000)

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
       
        doctype = data.get('module')
        values = data.get('values', {})
        access_token = data.get('access_token')
        useruniqueid = data.get('useruniqueid')
 
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
       
       
        payload = {
           "subject":values.get("subject"),
           "status": values.get("activitytype"),
           "custom_assign_user_id":values.get("assigned_user_id")
          
        }
 
        headers["Content-Type"] = "application/json"
        response = requests.post(f"{ERP_URL}/api/resource/{doctype}", headers=headers, data=json.dumps(payload))
 
        if response.status_code == 200:
            resp_data = response.json()
            return {
                "success": True,
                "message": "Tracking event updated successfully",
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
 
 