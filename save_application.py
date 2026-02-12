from flask import Flask, request
import requests
import json
import jwt

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698"
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

@app.route('/saveApp', methods=['POST'])
def call_save_application():
    return submit_tracking()
def submit_tracking():
    try:
        data = request.get_json()

        doctype = data.get('module')
        values = data.get('values', {})
        access_token = data.get("access_token")
        useruniqueid = data.get("useruniqueid")


        if not values or not doctype or not access_token:
            return {
                "success": False,
                "message": "Missing required fields"
            }, 400

        try:
            decoded = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            username = decoded.get("user")
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Access token expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid access token"}, 401

        headers = {"Authorization": f"token {API_KEY}"}
        payload = {
            "app_name": values.get("application_name")
        }

        headers["Content-Type"] = "application/json"
        response = requests.post(f"{ERP_URL}/api/resource/{doctype}", headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Saved the application successfully for user: {username}",
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