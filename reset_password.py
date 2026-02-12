# from flask import Flask, request
# import requests
# import jwt
# import json

# app = Flask(__name__)

# ERP_URL = "http://grofresh.crm-doctor.com:8000/"  
# API_KEY = "d296ff153c0517b:bac0fe4670c7c5d"
# SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

# @app.route('/ResetPassword', methods=['POST'])
# def change_password():
#     try:
#         data = request.get_json()
#         access_token = data.get("access_token")
#         old_password = data.get("oldPassword")
#         new_password = data.get("newPassword")
#         repeat_new_password = data.get("repeatnewPassword")


#         if not all([access_token, old_password, new_password, repeat_new_password]):
#             return {
#                 "success": False,
#                 "message": "All fields are required"
#             }, 400

#         if new_password != repeat_new_password:
#             return {
#                 "success": False,
#                 "message": "New password and repeat password do not match"
#             }, 400

#         try:
#             decoded = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
#             username = decoded.get("user")
#         except jwt.ExpiredSignatureError:
#             return {"success": False, "message": "Token expired"}, 401
#         except jwt.InvalidTokenError:
#             return {"success": False, "message": "Invalid token"}, 401

#         login_url = f"{ERP_URL}/api/method/login"
#         login_data = {"usr": username, "pwd": old_password}
#         login_headers = {"Content-Type": "application/x-www-form-urlencoded"}

#         login_response = requests.post(login_url, data=login_data, headers=login_headers)

#         if login_response.status_code != 200:
#             return {
#                 "success": False,
#                 "message": "Old password is incorrect"
#             }, 401

#         headers = {
#             "Authorization": f"token {API_KEY}",
#             "Content-Type": "application/json"
#         }

#         update_data = {
#             "new_password": new_password
#         }

#         response = requests.put(
#             f"{ERP_URL}/api/resource/User/{username}",
#             headers=headers,
#             data=json.dumps(update_data)
#         )

#         if response.status_code == 200:
#             return {
#                 "success": True,
#                 "message": "Password changed successfully"
#             }, 200
#         else:
#             return {
#                 "success": False,
#                 "message": "Failed to change password",
#                 "error": response.text
#             }, response.status_code

#     except Exception as e:
#         return {"success": False, "message": "Server Error", "error": str(e)}, 500


# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request
import requests
import jwt
import json

app = Flask(__name__)

ERP_URL = "http://164.52.192.194:8000/"  
API_KEY = "a886902c5c72450:6febe12f6f56698" 
SECRET_KEY = '8481cc547794ffc785537003eb752d0a8b7d0fcd83b9432f05915634e9e7b9f7y'

@app.route('/ResetPassword', methods=['POST'])
def call_reset_password():
    return change_password()
def change_password():
    try:
        data = request.get_json()
        access_token = data.get("access_token")
        uid = data.get("uid")  
        old_password = data.get("oldPassword")
        new_password = data.get("newPassword")
        repeat_new_password = data.get("repeatnewPassword")
        

        if not all([access_token, uid, old_password, new_password, repeat_new_password]):
            return {
                "success": False,
                "message": "All fields are required (access_token, uid, oldPassword, newPassword, repeatnewPassword)"
            }, 400

        if new_password != repeat_new_password:
            return {
                "success": False,
                "message": "New password and repeat password do not match"
            }, 400

        try:
            decoded = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])
            token_username = decoded.get("user")
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}, 401

        login_url = f"{ERP_URL}/api/method/login"
        login_data = {"usr": uid, "pwd": old_password}
        login_headers = {"Content-Type": "application/x-www-form-urlencoded"}

        login_response = requests.post(login_url, data=login_data, headers=login_headers)

        if login_response.status_code != 200:
            return {
                "success": False,
                "message": f"Old password is incorrect for user: {uid}"
            }, 401


        headers = {
            "Authorization": f"token {API_KEY}",
            "Content-Type": "application/json"
        }

        update_data = {
            "new_password": new_password
        }

        response = requests.put(
            f"{ERP_URL}/api/resource/User/{uid}",
            headers=headers,
            data=json.dumps(update_data)
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": f"Password changed successfully for user: {uid}",
                "changed_by": token_username,
                "target_user": uid
            }, 200
        else:
            return {
                "success": False,
                "message": f"Failed to change password for user: {uid}",
                "error": response.text
            }, response.status_code

    except Exception as e:
        return {"success": False, "message": "Server Error", "error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)