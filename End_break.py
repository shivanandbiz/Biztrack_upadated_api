from flask import Flask, request
import requests
import jwt
import json

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698" 
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

@app.route('/saveRecord', methods=['POST'])
def call_End_break():
    return Break_Start()
def Break_Start():
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
            return {
                "success": True,
                "message": "End break updated successfully",
                "employee": employee_username
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