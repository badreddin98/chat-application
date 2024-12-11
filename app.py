from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active rooms and users
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('chat.html', username=username, room=room)
    return redirect('/')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    if room not in rooms:
        rooms[room] = {"users": []}
    rooms[room]["users"].append(username)
    emit('join_announcement', {
        'user': username,
        'message': ' has joined the room.',
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    if room in rooms:
        rooms[room]["users"].remove(username)
        if not rooms[room]["users"]:
            del rooms[room]
    emit('leave_announcement', {
        'user': username,
        'message': ' has left the room.',
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    emit('message', {
        'user': data['username'],
        'message': data['message'],
        'timestamp': datetime.now().strftime('%H:%M')
    }, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
