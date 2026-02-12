from flask import Flask, request
import requests
import jwt
import json

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698"
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

@app.route('/userInfo', methods=['POST'])
def call_user_details():
    return get_user_profile()
def get_user_profile():
    try:
        data = request.get_json()
        access_token = data.get("access_token")
        useruniqueid = data.get("useruniqueid")

        if not access_token and not useruniqueid:
            return {
                "success": False,
                "message": "All fields are required"
            }, 400

        try:
            decoded = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            username = decoded.get("user")
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}, 401

        headers = {"Authorization": f"token {API_KEY}"}
        user_response = requests.get(f"{ERP_URL}/api/resource/User/{username}", headers=headers)

        if user_response.status_code != 200:
            return {"success": False, "message": "User not found"}, 404

        user_data = user_response.json().get("data", {})

        response_data = {
            "success": True,
            "result": {
                "access_token": access_token,
                "username": username,
                "useruniqueid": user_data.get("name"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "full_name":user_data.get('full_name',None),
                "email": user_data.get("email"),
                "phone": user_data.get("phone"),
                "address": {
                    "street_address": user_data.get("street"),
                    "city": user_data.get("city"),
                    "state": user_data.get("state"),
                    "country": user_data.get("country"),
                    "postal_code": user_data.get("postal_code")
                }
            },
            "successMessage": {
                "message": "User Profile Is Fetched Successfully"
            }
        }

        return response_data, 200

    except Exception as e:
        return {"success": False, "message": "Server Error", "error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)