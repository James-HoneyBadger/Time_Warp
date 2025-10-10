"""
Networking and Collaboration System
Real-time collaborative programming features for Time_Warp.
"""

import time
import json
import socket
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any


class CollaborationUser:
    """Represents a user in a collaborative session"""

    def __init__(self, user_id, username, color="#FF0000"):
        self.user_id = user_id
        self.username = username
        self.color = color
        self.cursor_position = {"line": 0, "column": 0}
        self.selection_range = None
        self.is_active = True
        self.last_seen = time.time()
        self.permissions = {"read": True, "write": True, "execute": False}
        self.status = "online"  # online, away, busy, offline

    def to_dict(self):
        """Convert user to dictionary for network transmission"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color,
            "cursor_position": self.cursor_position,
            "selection_range": self.selection_range,
            "is_active": self.is_active,
            "last_seen": self.last_seen,
            "permissions": self.permissions,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        """Create user from dictionary"""
        user = cls(data["user_id"], data["username"], data.get("color", "#FF0000"))
        user.cursor_position = data.get("cursor_position", {"line": 0, "column": 0})
        user.selection_range = data.get("selection_range")
        user.is_active = data.get("is_active", True)
        user.last_seen = data.get("last_seen", time.time())
        user.permissions = data.get(
            "permissions", {"read": True, "write": True, "execute": False}
        )
        user.status = data.get("status", "online")
        return user


class CollaborationSession:
    """Manages a collaborative programming session"""

    def __init__(self, session_id, owner_id, session_name="Untitled Session"):
        self.session_id = session_id
        self.owner_id = owner_id
        self.session_name = session_name
        self.created_time = time.time()
        self.users = {}  # user_id -> CollaborationUser
        self.document_content = ""
        self.document_version = 0
        self.change_history = []  # List of changes with timestamps
        self.chat_messages = []
        self.shared_variables = {}
        self.execution_queue = []
        self.lock_regions = {}  # line_range -> user_id (for editing locks)

        # Session settings
        self.max_users = 10
        self.allow_anonymous = True
        self.require_approval = False
        self.session_type = "programming"  # programming, game, presentation

    def add_user(self, user):
        """Add user to session"""
        if len(self.users) >= self.max_users:
            return False, "Session is full"

        if user.user_id in self.users:
            return False, "User already in session"

        self.users[user.user_id] = user
        return True, "User added successfully"

    def remove_user(self, user_id):
        """Remove user from session"""
        if user_id in self.users:
            # Release any locks held by this user
            self.release_user_locks(user_id)
            del self.users[user_id]
            return True
        return False

    def apply_text_change(self, user_id, change):
        """Apply text change from a user"""
        if user_id not in self.users:
            return False, "User not in session"

        user = self.users[user_id]
        if not user.permissions["write"]:
            return False, "User does not have write permission"

        # Record change in history
        change_record = {
            "user_id": user_id,
            "timestamp": time.time(),
            "change": change,
            "version": self.document_version,
        }
        self.change_history.append(change_record)

        # Apply change to document
        # This is a simplified implementation
        # Real implementation would use operational transforms
        self.document_content = change.get("new_content", self.document_content)
        self.document_version += 1

        return True, "Change applied"

    def add_chat_message(self, user_id, message):
        """Add chat message to session"""
        if user_id not in self.users:
            return False

        chat_message = {
            "user_id": user_id,
            "username": self.users[user_id].username,
            "message": message,
            "timestamp": time.time(),
        }
        self.chat_messages.append(chat_message)

        # Keep only recent messages
        if len(self.chat_messages) > 1000:
            self.chat_messages = self.chat_messages[-1000:]

        return True

    def lock_region(self, user_id, start_line, end_line):
        """Lock a region of code for exclusive editing"""
        region_key = f"{start_line}-{end_line}"

        # Check if region is already locked
        if region_key in self.lock_regions:
            return False, "Region already locked"

        self.lock_regions[region_key] = user_id
        return True, "Region locked"

    def unlock_region(self, user_id, start_line, end_line):
        """Unlock a code region"""
        region_key = f"{start_line}-{end_line}"

        if region_key in self.lock_regions and self.lock_regions[region_key] == user_id:
            del self.lock_regions[region_key]
            return True

        return False

    def release_user_locks(self, user_id):
        """Release all locks held by a user"""
        to_remove = []
        for region_key, lock_user_id in self.lock_regions.items():
            if lock_user_id == user_id:
                to_remove.append(region_key)

        for region_key in to_remove:
            del self.lock_regions[region_key]

    def get_session_state(self):
        """Get complete session state for synchronization"""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "document_content": self.document_content,
            "document_version": self.document_version,
            "users": {uid: user.to_dict() for uid, user in self.users.items()},
            "lock_regions": self.lock_regions,
            "shared_variables": self.shared_variables,
        }


class NetworkManager:
    """Handles network communication for collaboration"""

    def __init__(self, port=8888):
        self.port = port
        self.socket = None
        self.is_server = False
        self.is_client = False
        self.connections = {}  # connection_id -> socket
        self.message_handlers = {}
        self.running = False
        self.server_thread = None

    def start_server(self):
        """Start as collaboration server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(("localhost", self.port))
            self.socket.listen(5)

            self.is_server = True
            self.running = True

            self.server_thread = threading.Thread(target=self._server_loop)
            self.server_thread.daemon = True
            self.server_thread.start()

            print(f"🌐 Collaboration server started on port {self.port}")
            return True

        except Exception as e:
            print(f"🌐 Failed to start server: {e}")
            return False

    def connect_to_server(self, host="localhost", port=None):
        """Connect to collaboration server as client"""
        if port is None:
            port = self.port

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            self.is_client = True
            self.running = True

            # Start client message handler
            client_thread = threading.Thread(target=self._client_loop)
            client_thread.daemon = True
            client_thread.start()

            print(f"🌐 Connected to collaboration server at {host}:{port}")
            return True

        except Exception as e:
            print(f"🌐 Failed to connect to server: {e}")
            return False

    def _server_loop(self):
        """Server main loop"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                connection_id = f"client_{len(self.connections)}"
                self.connections[connection_id] = client_socket

                # Start handler for this client
                handler_thread = threading.Thread(
                    target=self._handle_client, args=(connection_id, client_socket)
                )
                handler_thread.daemon = True
                handler_thread.start()

                print(f"🌐 Client connected: {address}")

            except Exception as e:
                if self.running:
                    print(f"🌐 Server error: {e}")
                break

    def _handle_client(self, connection_id, client_socket):
        """Handle messages from a specific client"""
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break

                message = json.loads(data.decode())
                self._process_message(connection_id, message)

            except Exception as e:
                print(f"🌐 Client handler error: {e}")
                break

        # Clean up connection
        if connection_id in self.connections:
            del self.connections[connection_id]
        client_socket.close()

    def _client_loop(self):
        """Client message loop"""
        while self.running:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                message = json.loads(data.decode())
                self._process_message("server", message)

            except Exception as e:
                if self.running:
                    print(f"🌐 Client error: {e}")
                break

    def _process_message(self, sender_id, message):
        """Process received message"""
        message_type = message.get("type")

        if message_type in self.message_handlers:
            try:
                self.message_handlers[message_type](sender_id, message)
            except Exception as e:
                print(f"🌐 Message handler error: {e}")

    def send_message(self, message, target_id=None):
        """Send message to specific target or broadcast"""
        message_data = json.dumps(message).encode()

        if self.is_server:
            if target_id and target_id in self.connections:
                # Send to specific client
                try:
                    self.connections[target_id].send(message_data)
                except Exception as e:
                    print(f"🌐 Failed to send to {target_id}: {e}")
            else:
                # Broadcast to all clients
                for conn_id, client_socket in list(self.connections.items()):
                    try:
                        client_socket.send(message_data)
                    except Exception as e:
                        print(f"🌐 Failed to broadcast to {conn_id}: {e}")
                        # Remove failed connection
                        del self.connections[conn_id]

        elif self.is_client:
            # Send to server
            try:
                self.socket.send(message_data)
            except Exception as e:
                print(f"🌐 Failed to send to server: {e}")

    def register_message_handler(self, message_type, handler):
        """Register handler for specific message type"""
        self.message_handlers[message_type] = handler

    def stop(self):
        """Stop network manager"""
        self.running = False

        if self.socket:
            self.socket.close()

        for client_socket in self.connections.values():
            client_socket.close()

        self.connections.clear()
        print("🌐 Network manager stopped")


class CollaborationManager:
    """Main collaboration system manager"""

    def __init__(self):
        self.sessions = {}  # session_id -> CollaborationSession
        self.network_manager = NetworkManager()
        self.current_user = None
        self.current_session = None
        self.event_callbacks = {}

        # Register network message handlers
        self.network_manager.register_message_handler(
            "join_session", self._handle_join_session
        )
        self.network_manager.register_message_handler(
            "leave_session", self._handle_leave_session
        )
        self.network_manager.register_message_handler(
            "text_change", self._handle_text_change
        )
        self.network_manager.register_message_handler(
            "chat_message", self._handle_chat_message
        )
        self.network_manager.register_message_handler(
            "cursor_update", self._handle_cursor_update
        )

    def create_session(self, session_name, user_id, username):
        """Create new collaboration session"""
        session_id = f"session_{int(time.time())}"
        session = CollaborationSession(session_id, user_id, session_name)

        # Add creator as first user
        creator = CollaborationUser(user_id, username)
        creator.permissions["execute"] = True  # Session owner can execute
        session.add_user(creator)

        self.sessions[session_id] = session
        print(f"🤝 Created collaboration session: {session_name}")
        return session_id

    def join_session(self, session_id, user_id, username, color="#FF0000"):
        """Join existing collaboration session"""
        if session_id not in self.sessions:
            return False, "Session not found"

        session = self.sessions[session_id]
        user = CollaborationUser(user_id, username, color)

        success, message = session.add_user(user)
        if success:
            self.current_session = session_id
            self.current_user = user
            print(f"🤝 Joined session: {session.session_name}")

        return success, message

    def leave_session(self, session_id, user_id):
        """Leave collaboration session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.remove_user(user_id):
                print(f"🤝 Left session: {session.session_name}")
                return True
        return False

    def start_hosting(self, port=8888):
        """Start hosting collaboration sessions"""
        return self.network_manager.start_server()

    def connect_to_host(self, host="localhost", port=8888):
        """Connect to collaboration host"""
        return self.network_manager.connect_to_server(host, port)

    def _handle_join_session(self, sender_id, message):
        """Handle join session request"""
        session_id = message.get("session_id")
        user_id = message.get("user_id")
        username = message.get("username")
        color = message.get("color", "#FF0000")

        success, msg = self.join_session(session_id, user_id, username, color)

        response = {"type": "join_response", "success": success, "message": msg}

        if success and session_id in self.sessions:
            response["session_state"] = self.sessions[session_id].get_session_state()

        self.network_manager.send_message(response, sender_id)

    def _handle_leave_session(self, sender_id, message):
        """Handle leave session request"""
        session_id = message.get("session_id")
        user_id = message.get("user_id")

        self.leave_session(session_id, user_id)

    def _handle_text_change(self, sender_id, message):
        """Handle text change from remote user"""
        session_id = message.get("session_id")
        user_id = message.get("user_id")
        change = message.get("change")

        if session_id in self.sessions:
            session = self.sessions[session_id]
            success, msg = session.apply_text_change(user_id, change)

            if success:
                # Broadcast change to other users
                broadcast_message = {
                    "type": "text_change",
                    "session_id": session_id,
                    "user_id": user_id,
                    "change": change,
                }
                self.network_manager.send_message(broadcast_message)

    def _handle_chat_message(self, sender_id, message):
        """Handle chat message"""
        session_id = message.get("session_id")
        user_id = message.get("user_id")
        chat_text = message.get("message")

        if session_id in self.sessions:
            session = self.sessions[session_id]
            if session.add_chat_message(user_id, chat_text):
                # Broadcast chat message
                broadcast_message = {
                    "type": "chat_message",
                    "session_id": session_id,
                    "user_id": user_id,
                    "username": session.users[user_id].username,
                    "message": chat_text,
                    "timestamp": time.time(),
                }
                self.network_manager.send_message(broadcast_message)

    def _handle_cursor_update(self, sender_id, message):
        """Handle cursor position update"""
        session_id = message.get("session_id")
        user_id = message.get("user_id")
        cursor_pos = message.get("cursor_position")

        if session_id in self.sessions and user_id in self.sessions[session_id].users:
            self.sessions[session_id].users[user_id].cursor_position = cursor_pos

            # Broadcast cursor update
            broadcast_message = {
                "type": "cursor_update",
                "session_id": session_id,
                "user_id": user_id,
                "cursor_position": cursor_pos,
            }
            self.network_manager.send_message(broadcast_message)

    def register_event_callback(self, event_type, callback):
        """Register callback for collaboration events"""
        self.event_callbacks[event_type] = callback

    def stop(self):
        """Stop collaboration manager"""
        self.network_manager.stop()
        self.sessions.clear()
        print("🤝 Collaboration manager stopped")
