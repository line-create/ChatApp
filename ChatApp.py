from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QTextBrowser, QLineEdit, QPushButton, QListWidget, QHBoxLayout, QListWidgetItem
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QTextCursor
import socket
import threading

class ChatApplication1(QMainWindow):
    
    new_message_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()  

        self.setWindowTitle("Chat Application")
        self.connected_user_list = QListWidget()
        self.message_display = QTextBrowser()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("SEND")
        self.app_name_label = QLabel("Chat Application")

        main_layout = QVBoxLayout()

        # User Zone
        connnected_user_layout = QVBoxLayout()
        connnected_user_layout.addWidget(self.connected_user_list)
        connected_user_zone = QWidget()
        connected_user_zone.setLayout(connnected_user_layout)
        main_layout.addWidget(connected_user_zone)

        # User message zone
        message_display_layout = QVBoxLayout()
        message_display_layout.addWidget(self.message_display)
        user_message_display = QWidget()
        user_message_display.setLayout(message_display_layout)
        main_layout.addWidget(user_message_display)

        # Input and send button
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_zone = QWidget()
        input_zone.setLayout(input_layout)
        main_layout.addWidget(input_zone)

        # Central Widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        

        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(self.send_message)
        self.new_message_received.connect(self.display_received_message)

        # Create socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("127.0.0.1", 4444))

        received_thread = threading.Thread(target=self.received_message)
        received_thread.daemon = True
        received_thread.start()

        
    def update_connected_users(self, users):
        self.connected_user_list.clear()
        for user in users:
            item = QListWidgetItem(user)
            self.connected_user_list.addItem(item)
        
    def send_message(self):
        message = self.message_input.text()
        if message:
            # Send message
            self.client_socket.send(message.encode())
            # Append message
            self.message_display.append(f"Message Sent: {message}")
            # Clear the message zone after sending
            self.message_input.clear()

    def received_message(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    break
                if data.startswith("/Users"):
                    # Received an updated user list
                    users = data[7:].split(", ")
                    self.update_connected_users(users)
                else:
                    # Regular message
                    self.new_message_received.emit(data)
            except Exception as e:
                print(f"Error receiving message {str(e)}")
                break
    
    def display_received_message(self, message):
        self.message_display.append(f"{message}")
        self.message_display.moveCursor(QTextCursor.End)

        

if __name__ == "__main__":
    app = QApplication([])
    window = ChatApplication1()
    window.show()
    app.exec_()

