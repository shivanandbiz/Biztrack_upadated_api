from flask import Flask, request, jsonify
import requests
import json
import jwt
 
app = Flask(__name__)
 
ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698"
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'
 
@app.route("/usertasks", methods=["POST"])
def call_Fetch_Task():
    return user_tasks()
def user_tasks():
    try:
        data = request.get_json()
        access_token = data.get("access_token")
        useruniqueid = data.get('useruniqueid')
 
        if not access_token:
            return jsonify({"status": 0, "message": "access_token missing", "data": []}), 400
 
        try:
            decoded = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            username = decoded.get("user") or decoded.get("user_id") or decoded.get("email")
        except jwt.ExpiredSignatureError:
            return jsonify({"status": 0, "message": "Access token expired", "data": []}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": 0, "message": "Invalid access token", "data": []}), 401
 
        headers = {"Authorization": f"token {API_KEY}"}
        params = {
            "filters": json.dumps([
                ["status", "in", ["Open", "In Progress"]],
                ["_assign", "like", f"%{username}%"]
            ]),
            "fields": json.dumps(["name", "subject", "status", "project", "priority", "owner"])
        }
 
        response = requests.get(f"{ERP_URL}/api/resource/Task", headers=headers, params=params)
 
        if response.status_code == 200:
            tasks = response.json().get("data", [])
 
            for task in tasks:
                project_id = task.get("project")
                if project_id:
                    proj_response = requests.get(f"{ERP_URL}/api/resource/Project/{project_id}", headers=headers)
                    if proj_response.status_code == 200:
                        project_data = proj_response.json().get("data", {})
                        task["project_name"] = project_data.get("project_name", "")
                    else:
                        task["project_name"] = ""
 
            return jsonify({"status": 1, "message": "Tasks fetched", "data": tasks}), 200
        else:
            return jsonify({
                "status": 0,
                "message": "Failed to fetch tasks from ERP",
                "error": response.text
            }), response.status_code
 
    except Exception as e:
        return jsonify({
            "status": 0,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500
   
if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)