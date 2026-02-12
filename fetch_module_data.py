from flask import Flask, request, jsonify
import requests
import json
import jwt
from jwt.exceptions import InvalidTokenError
 
app = Flask(__name__)
 
ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698"
JWT_SECRET_KEY = "8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y"  
 
 
@app.route('/listModuleAllRecords', methods=['POST'])
def call_fetch_module_data():
    return fetch_data()
 
def fetch_data():
    try:
        data = request.get_json()
        doctype = data.get('module')
        access_token = data.get('access_token')
        useruniqueid = data.get('useruniqueid')
 
        if not doctype or not access_token:
            return jsonify({
                "success": False,
                "message": "Missing 'module' or 'access_token'",
                "result": {}
            }), 400
 
        try:
            decoded = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get("userid")
        except InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid or expired access token",
                "result": {}
            }), 401
 
        headers = {"Authorization": f"token {API_KEY}"}
        url = f"{ERP_URL}/api/resource/{doctype}"
 
        params = {
            "fields": json.dumps(["name", "app_name"])
        }
 
        response = requests.get(url, headers=headers, params=params)
 
        if response.status_code == 200:
            raw_data = response.json().get("data", [])
 
            formatted_data = [
                {
                    "application_name": record.get("app_name"),
                    "applicationsid": record.get("name")
                } for record in raw_data
            ]
 
            return jsonify({
                "success": True,
                "result": {
                    "records": formatted_data
                }
            }), 200
        else:
            print("ERP Error:", response.status_code, response.text)
            return jsonify({
                "success": False,
                "message": "Failed to fetch data from ERP",
                "erp_error": response.text,
                "result": {}
            }), response.status_code
 
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Internal Server Error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)