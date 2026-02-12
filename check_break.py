from flask import Flask, request, jsonify
import jwt
import requests

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"
API_KEY = 'a886902c5c72450'
API_SECRET = '6febe12f6f56698'
JWT_SECRET = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

HEADERS = {
    'Authorization': f'token {API_KEY}:{API_SECRET}',
    'Content-Type': 'application/json'
}

@app.route('/checkBreakStart', methods=['POST'])
def call_check_break():
    return check_break_start()
def check_break_start():
    data = request.get_json()
    access_token = data.get('access_token')
    user_id = data.get('useruniqueid')  

    try:
        decoded = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        if str(decoded.get("userid")) != str(user_id):
            return jsonify({
                "success": False,
                "result": None,
                "successMessage": "User ID mismatch in token"
            }), 403
    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "result": None,
            "successMessage": "Token expired"
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            "success": False,
            "result": None,
            "successMessage": "Invalid access token"
        }), 401


    event_url = f"{ERP_URL}/api/resource/Event"
    params = {
        'fields': '["name"]',
        'filters': f'[["Event", "status", "=", "Break Start"],'
                   f'["Event", "custom_assign_user_id", "=", "{user_id}"]]',
        'limit_page_length': 1
    }

    response = requests.get(event_url, headers=HEADERS, params=params)
    event_data = response.json()

    if event_data.get("data"):
        return jsonify({
            "success": True,
            "result": True,
            "successMessage": "Break Start found"
        })
    else:
        return jsonify({
            "success": True,
            "result": False,
            "successMessage": "No Break Start found"
        })

if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)