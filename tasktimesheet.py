# from flask import Flask, request, jsonify
# import requests
# from datetime import datetime, time, timedelta
# import pytz
 
# app = Flask(__name__)
 
# ERP_BASE_URL = "http://164.52.192.194:8000"
# API_KEY = "a886902c5c72450"
# API_SECRET = "6febe12f6f56698"
 
# def get_auth_headers():
#     return {
#         "Authorization": f"token {API_KEY}:{API_SECRET}",
#         "Content-Type": "application/json"
#     }
 
# def get_today_timesheet(user):
#     today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
#     url = f"{ERP_BASE_URL}/api/resource/Timesheet"
#     params = {
#         "fields": '["name","start_date"]',
#         "filters": f'[["user", "=", "{user}"], ["start_date", "=", "{today}"]]'
#     }
#     res = requests.get(url, headers=get_auth_headers(), params=params)
#     res.raise_for_status()
#     data = res.json()
#     if data["data"]:
#         return data["data"][0]["name"]
#     return None
 
# def generate_time_logs():
#     ist = pytz.timezone("Asia/Kolkata")
#     today = datetime.now(ist).date()
#     base_time = datetime.combine(today, time(10, 0))
#     time_logs = []
 
#     for i in range(9):
#         from_time = base_time + timedelta(hours=i)
#         to_time = from_time + timedelta(hours=1)
#         time_logs.append({
#             "from_time": from_time.isoformat(),
#             "to_time": to_time.isoformat(),
#             "project": "",
#             "task": ""
#         })
 
#     return time_logs
 
# def create_timesheet(user):
#     ist = pytz.timezone("Asia/Kolkata")
#     today = datetime.now(ist).date()
 
#     payload = {
#         "user": user,
#         "start_date": today.isoformat(),
#         "time_logs": generate_time_logs()
#     }
 
#     url = f"{ERP_BASE_URL}/api/resource/Timesheet"
#     res = requests.post(url, headers=get_auth_headers(), json=payload)
#     res.raise_for_status()
#     return res.json()["data"]["name"]
 
# def get_timesheet_doc(name):
#     url = f"{ERP_BASE_URL}/api/resource/Timesheet/{name}"
#     res = requests.get(url, headers=get_auth_headers())
#     res.raise_for_status()
#     return res.json()["data"]
 
# def update_timesheet_row(timesheet_doc, project, task):
#     ist = pytz.timezone("Asia/Kolkata")
#     now = datetime.now(ist)
 
#     for row in timesheet_doc.get("time_logs", []):
#         try:
#             from_time = datetime.fromisoformat(row["from_time"])
#             to_time = datetime.fromisoformat(row["to_time"])
 
#             from_time = ist.localize(from_time) if from_time.tzinfo is None else from_time.astimezone(ist)
#             to_time = ist.localize(to_time) if to_time.tzinfo is None else to_time.astimezone(ist)
 
#         except Exception:
#             continue
 
#         if from_time <= now < to_time:
#             row["project"] = project
#             row["task"] = task
#             return True
 
#     return False
 
# def save_timesheet(name, updated_doc):
#     url = f"{ERP_BASE_URL}/api/resource/Timesheet/{name}"
#     res = requests.put(url, headers=get_auth_headers(), json={"time_logs": updated_doc["time_logs"]})
#     res.raise_for_status()
#     return res.json()
 
# @app.route('/update_timesheet', methods=['POST'])
# def call_tasktimesheet():
#     return update_timesheet()
# def update_timesheet():
#     try:
#         data = request.json
#         user = data["user"]
#         project = data["project"]
#         task = data["task"]
 
#         timesheet_name = get_today_timesheet(user)
#         if not timesheet_name:
#             timesheet_name = create_timesheet(user)
 
#         timesheet = get_timesheet_doc(timesheet_name)
#         updated = update_timesheet_row(timesheet, project, task)
 
#         if updated:
#             result = save_timesheet(timesheet_name, timesheet)
#             return jsonify({"success": True, "timesheet": result["data"]["name"]})
#         else:
#             return jsonify({"error": "No matching 1-hour time slot found"}), 400
 
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
 
# if __name__ == '__main__':
#     app.run(debug=True, host='164.52.192.194', port=5000)
 

from flask import Flask, request, jsonify
import requests
from datetime import datetime, time, timedelta
import pytz
import json
import logging
 
app = Flask(__name__)
 
ERP_BASE_URL = "http://164.52.192.194:8000"
API_KEY = "a886902c5c72450"
API_SECRET = "6febe12f6f56698"
 
# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
 
def get_auth_headers():
    return {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
 
def get_today_timesheet(user):
    today_str = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    url = f"{ERP_BASE_URL}/api/resource/Timesheet"
    params = {
        "fields": '["name","start_date"]',
        "filters": f'[["user", "=", "{user}"], ["start_date", "=", "{today_str}"]]'
    }
    logging.debug(f"Fetching today's timesheet for user '{user}', params: {params}")
    res = requests.get(url, headers=get_auth_headers(), params=params)
    logging.debug(f"ERP response status: {res.status_code}")
    res.raise_for_status()
    data = res.json()
    logging.debug(f"ERP GET Timesheet response data: {json.dumps(data, indent=2)}")
    if data["data"]:
        return data["data"][0]["name"]
    return None
 
def generate_time_logs():
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    base_time = datetime.combine(today, time(10, 0))  # start from 10:00
    time_logs = []
    for i in range(9):
        from_time = base_time + timedelta(hours=i)
        to_time = from_time + timedelta(hours=1)
        time_logs.append({
            "from_time": from_time.isoformat(),
            "to_time": to_time.isoformat(),
            "project": "",
            "task": "",
            "screen_images": ""  # Initialize empty string for text field
        })
    logging.debug(f"Generated time logs: {json.dumps(time_logs, indent=2)}")
    return time_logs
 
def create_timesheet(user):
    ist = pytz.timezone("Asia/Kolkata")
    today = datetime.now(ist).date()
    payload = {
        "user": user,
        "start_date": today.isoformat(),
        "time_logs": generate_time_logs()
    }
    url = f"{ERP_BASE_URL}/api/resource/Timesheet"
    logging.debug(f"Creating timesheet with payload: {json.dumps(payload, indent=2)}")
    res = requests.post(url, headers=get_auth_headers(), json=payload)
    logging.debug(f"ERP POST response status: {res.status_code}")
    res.raise_for_status()
    resp_data = res.json()
    logging.debug(f"ERP POST response data: {json.dumps(resp_data, indent=2)}")
    return resp_data["data"]["name"]
 
def get_timesheet_doc(name):
    url = f"{ERP_BASE_URL}/api/resource/Timesheet/{name}"
    logging.debug(f"Fetching timesheet document '{name}'")
    res = requests.get(url, headers=get_auth_headers())
    logging.debug(f"ERP GET timesheet doc status: {res.status_code}")
    res.raise_for_status()
    data = res.json()
    logging.debug(f"ERP GET timesheet doc data: {json.dumps(data, indent=2)}")
    return data["data"]
 
def update_timesheet_row(timesheet_doc, project, task, screen_media=None):
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    updated = False
 
    logging.debug(f"Updating timesheet rows at current IST time: {now.isoformat()}")
 
    for idx, row in enumerate(timesheet_doc.get("time_logs", [])):
        try:
            from_time = datetime.fromisoformat(row["from_time"])
            to_time = datetime.fromisoformat(row["to_time"])
 
            from_time = ist.localize(from_time) if from_time.tzinfo is None else from_time.astimezone(ist)
            to_time = ist.localize(to_time) if to_time.tzinfo is None else to_time.astimezone(ist)
        except Exception as e:
            logging.error(f"Error parsing from_time/to_time in row {idx}: {e}")
            continue
 
        logging.debug(f"Row {idx} from_time: {from_time.isoformat()}, to_time: {to_time.isoformat()}")
 
        if from_time <= now < to_time:
            logging.debug(f"Current time falls in row {idx} time slot")
 
            if project:
                logging.debug(f"Setting project: {project}")
                row["project"] = project
            if task:
                logging.debug(f"Setting task: {task}")
                row["task"] = task
 
            if screen_media:
                urls_to_add = screen_media.get("urls", [])
                if not isinstance(urls_to_add, list):
                    urls_to_add = [str(urls_to_add)]
 
                existing_urls_str = row.get("screen_images", "")
                existing_urls = [u.strip() for u in existing_urls_str.split(",")] if existing_urls_str else []
 
                for url in urls_to_add:
                    url = url.strip()
                    if url and url not in existing_urls:
                        existing_urls.append(url)
                row["screen_images"] = ",".join(existing_urls)
                logging.debug(f"Updated screen_images: {row['screen_images']}")
 
            updated = True
            logging.debug(f"Row {idx} after update: {json.dumps(row, indent=2)}")
            break
 
    if not updated:
        logging.debug("No matching time slot for current time; no update made.")
    return updated
 
def save_timesheet(name, updated_doc):
    url = f"{ERP_BASE_URL}/api/resource/Timesheet/{name}"
    payload = { "time_logs": updated_doc["time_logs"] }
    logging.debug(f"Saving timesheet '{name}' with payload: {json.dumps(payload, indent=2)}")
    res = requests.put(url, headers=get_auth_headers(), json=payload)
    logging.debug(f"ERP PUT response status: {res.status_code}")
    res.raise_for_status()
    data = res.json()
    logging.debug(f"ERP PUT response data: {json.dumps(data, indent=2)}")
    return data

@app.route('/update_timesheet', methods=['POST'])
def call_tasktimesheet():
    return update_timesheet()


def update_timesheet():
    try:
        data = request.json
        logging.debug(f"Received update_timesheet request data: {json.dumps(data, indent=2)}")
 
        user = data["user"]
        project = data.get("project")
        task = data.get("task")
        screen_media = data.get("screen_media")  
        logging.debug(f"Parsed params - user: {user}, project: {project}, task: {task}, screen_media: {screen_media}")
 
        timesheet_name = get_today_timesheet(user)
        if not timesheet_name:
            logging.debug(f"No timesheet for user {user} today, creating one.")
            timesheet_name = create_timesheet(user)
        else:
            logging.debug(f"Using existing timesheet: {timesheet_name}")
 
        timesheet_doc = get_timesheet_doc(timesheet_name)
 
        updated = update_timesheet_row(timesheet_doc, project, task, screen_media)
 
        if updated:
            logging.debug("Timesheet updated, saving now.")
            save_result = save_timesheet(timesheet_name, timesheet_doc)
            return jsonify({"success": True, "timesheet": save_result["data"]["name"]})
        else:
            logging.warning("No matching time slot found to update.")
            return jsonify({"error": "No matching 1-hour time slot found"}), 400
 
    except Exception as e:
        logging.error(f"Exception in /update_timesheet endpoint: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
 
if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)
 
 