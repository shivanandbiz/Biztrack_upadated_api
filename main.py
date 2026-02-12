from flask import Flask
import Login
import reset_password
import check_break
import check_tracking
import End_break
import fetch_module_data
import Fetch_Task
import save_application
import Start_break
import Tracking_data
import tracking_start_event
import user_details
import tasktimesheet

app = Flask(__name__)

app.add_url_rule('/login', view_func=Login.call_Login, methods=['POST'])
app.add_url_rule('/ResetPassword', view_func=reset_password.call_reset_password, methods=['POST'])
app.add_url_rule('/checkBreakStart', view_func=check_break.call_check_break, methods=['POST'])
app.add_url_rule('/checkTrackingStart', view_func=check_tracking.call_check_tracking, methods=['POST'])
app.add_url_rule('/saveRecord', view_func=End_break.call_End_break, methods=['POST'])
app.add_url_rule('/listModuleAllRecords', view_func=fetch_module_data.call_fetch_module_data, methods=['POST'])
app.add_url_rule('/usertasks', view_func=Fetch_Task.call_Fetch_Task, methods=['POST'])
app.add_url_rule('/saveApp', view_func=save_application.call_save_application, methods=['POST'])
app.add_url_rule('/startBreak', view_func=Start_break.call_Start_break, methods=['POST'])
app.add_url_rule('/AppTrack', view_func=Tracking_data.call_Tracking_data, methods=['POST'])
app.add_url_rule('/saveTracking', view_func=tracking_start_event.call_tracking_start_event, methods=['POST'])
app.add_url_rule('/userInfo', view_func=user_details.call_user_details, methods=['POST'])
app.add_url_rule('/update_timesheet', view_func=tasktimesheet.call_tasktimesheet, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True, host='164.52.192.194', port=5000)