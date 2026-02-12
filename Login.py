from flask import Flask, request
import requests
import jwt
import datetime
import json
 
app = Flask(__name__)
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'  
 
ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698"  
 
def get_user_details(username, password):
    url = f"{ERP_URL}/api/method/login"
    headers = {"Authorization": f"token {API_KEY}"}
    response = requests.post(url, data={'usr': username, 'pwd': password}, headers=headers)
 
    if response.status_code != 200:
        return None
   
    user_info_url = f"{ERP_URL}/api/resource/User/{username}"
    user_info_response = requests.get(user_info_url, headers=headers)
 
    if user_info_response.status_code == 200:
        user_data = user_info_response.json().get('data', {})
        return {
            "user_id": user_data.get('name', None),
            "email": user_data.get('email', None),
            "first_name": user_data.get('first_name', None),
            "last_name": user_data.get('last_name', None),
            "full_name":user_data.get('full_name',None),
        }
    return None

def generate_token(username):
    payload = {
        'user': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  
    return token

@app.route('/login', methods=['POST'])
def call_Login():
    return login()
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username:
        return app.response_class(
            response=json.dumps({
                "StatusMessage": "Username is Missing",
                "Status Code": 0,
                "data": {}
            }, indent=4),
            status=400,
            mimetype='application/json'
        )

    if not password:
        return app.response_class(
            response=json.dumps({
                "StatusMessage": "Password is Missing",
                "Status Code": 0,
                "data": {}
            }, indent=4),
            status=400,
            mimetype='application/json'
        )

    user_details = get_user_details(username, password)

    if user_details:
        token = generate_token(username)
        return app.response_class(
            response=json.dumps({
                "StatusMessage": "Successfully Logged-In",
                "Status Code": 1,
                "data": {
                    "access_token": token,
                    "useruniqeid": user_details["user_id"],
                    "email": user_details["email"],
                    "first_name": user_details["first_name"],
                    "last_name": user_details["last_name"],
                    "full_name":user_details["full_name"]
                }
            }, indent=4),
            status=200,
            mimetype='application/json'
        )
    else:
        return app.response_class(
            response=json.dumps({
                "StatusMessage": "Invalid Credentials",
                "Status Code": 0,
                "data": {}
            }, indent=4),
            status=401,
            mimetype='application/json'
        )
 
if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)