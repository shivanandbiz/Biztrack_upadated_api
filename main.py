from flask import Flask, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
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
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', logger=True, engineio_logger=True)

# Existing REST API routes
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

# WebRTC Signaling - Store active streams
active_streams = {}  # employee_id -> { 'socket_id': str, 'employee_name': str, 'viewers': [] }

@socketio.on('connect')
def handle_connect():
    print(f'[WebRTC] ✅ Client connected: {request.sid}')
    emit('connected', {'socket_id': request.sid})
    
    # Send list of currently active streamers to the new connection
    for employee_id, stream_info in active_streams.items():
        emit('streamer-available', {
            'employee_id': employee_id,
            'employee_name': stream_info['employee_name']
        }, room=request.sid)
        print(f'[WebRTC] 📤 Sent active streamer to new client: {employee_id}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[WebRTC] 🔌 Client disconnected: {request.sid}')
    # Clean up any active streams
    for employee_id, stream_info in list(active_streams.items()):
        if stream_info['socket_id'] == request.sid:
            print(f'[WebRTC] 🗑️ Removing streamer: {employee_id}')
            del active_streams[employee_id]
            emit('stream-ended', {'employee_id': employee_id}, broadcast=True)

@socketio.on('register-streamer')
def handle_register_streamer(data):
    """Employee registers as available for streaming"""
    employee_id = data['employee_id']
    active_streams[employee_id] = {
        'socket_id': request.sid,
        'employee_name': data['employee_name'],
        'viewers': []
    }
    print(f'[WebRTC] 📝 Streamer registered: {employee_id} ({data["employee_name"]})')
    emit('streamer-registered', {'employee_id': employee_id})
    # Notify all viewers that this employee is available
    emit('streamer-available', {
        'employee_id': employee_id,
        'employee_name': data['employee_name']
    }, broadcast=True)

@socketio.on('request-stream')
def handle_request_stream(data):
    """Admin requests to view employee stream"""
    employee_id = data['employee_id']
    viewer_id = request.sid
    
    print(f'[WebRTC] 📹 Stream requested: {employee_id} by {viewer_id}')
    
    if employee_id in active_streams:
        stream_info = active_streams[employee_id]
        stream_info['viewers'].append(viewer_id)
        
        # Tell employee to start streaming to this viewer
        emit('start-stream', {
            'viewer_id': viewer_id
        }, room=stream_info['socket_id'])
        
        print(f'[WebRTC] ✅ Stream request forwarded to employee')
    else:
        print(f'[WebRTC] ❌ Employee not available: {employee_id}')
        emit('stream-error', {'message': 'Employee not available'})

@socketio.on('offer')
def handle_offer(data):
    """Forward WebRTC offer from employee to admin"""
    target_id = data['target']
    emit('offer', {
        'offer': data['offer'],
        'from': request.sid
    }, room=target_id)
    print(f'[WebRTC] 📤 Offer forwarded: {request.sid} -> {target_id}')

@socketio.on('answer')
def handle_answer(data):
    """Forward WebRTC answer from admin to employee"""
    target_id = data['target']
    emit('answer', {
        'answer': data['answer'],
        'from': request.sid
    }, room=target_id)
    print(f'[WebRTC] 📨 Answer forwarded: {request.sid} -> {target_id}')

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    """Forward ICE candidates for NAT traversal"""
    target_id = data['target']
    emit('ice-candidate', {
        'candidate': data['candidate'],
        'from': request.sid
    }, room=target_id)

@socketio.on('stop-stream')
def handle_stop_stream(data):
    """Admin stops viewing stream"""
    employee_id = data['employee_id']
    viewer_id = request.sid
    
    print(f'[WebRTC] ⏹️ Stop stream: {employee_id} by {viewer_id}')
    
    if employee_id in active_streams:
        stream_info = active_streams[employee_id]
        if viewer_id in stream_info['viewers']:
            stream_info['viewers'].remove(viewer_id)
        
        # Tell employee to stop streaming to this viewer
        emit('stop-stream', {
            'viewer_id': viewer_id
        }, room=stream_info['socket_id'])

if __name__ == '__main__':
    print('[WebRTC] 🚀 Starting middleware API with WebSocket support...')
    print('[WebRTC] 🌐 Server: http://164.52.192.194:5000')
    socketio.run(app, host='164.52.192.194', port=5000, debug=True)