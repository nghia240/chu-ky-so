import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import socket
import threading
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64

class FileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng Truyền File với Ký Số")
        self.root.geometry("800x600")
        
        # Tạo khóa RSA
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.peer_public_key = None  # Khóa công khai của bên kia
        
        # Giao diện
        self.create_widgets()
        
        # Khởi tạo server
        self.server_socket = None
        self.client_socket = None
        self.is_server = False
        
    def create_widgets(self):
        # Frame cho việc chọn file
        file_frame = ttk.LabelFrame(self.root, text="Chọn File", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side="left", padx=5)
        ttk.Button(file_frame, text="Chọn File", command=self.select_file).pack(side="left", padx=5)
        
        # Frame cho việc kết nối
        conn_frame = ttk.LabelFrame(self.root, text="Kết nối", padding=10)
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(conn_frame, text="IP:").pack(side="left", padx=5)
        self.ip_entry = ttk.Entry(conn_frame, width=15)
        self.ip_entry.pack(side="left", padx=5)
        self.ip_entry.insert(0, "localhost")
        
        ttk.Label(conn_frame, text="Port:").pack(side="left", padx=5)
        self.port_entry = ttk.Entry(conn_frame, width=6)
        self.port_entry.pack(side="left", padx=5)
        self.port_entry.insert(0, "5000")
        
        ttk.Button(conn_frame, text="Tạo Server", command=self.create_server).pack(side="left", padx=5)
        ttk.Button(conn_frame, text="Kết nối", command=self.connect_to_server).pack(side="left", padx=5)
        
        # Frame cho việc gửi/nhận
        transfer_frame = ttk.LabelFrame(self.root, text="Truyền File", padding=10)
        transfer_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(transfer_frame, text="Gửi File", command=self.send_file).pack(side="left", padx=5)
        ttk.Button(transfer_frame, text="Nhận File", command=self.receive_file).pack(side="left", padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill="both", expand=True)
        
    def select_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path.set(filename)
            self.log(f"Đã chọn file: {filename}")
            
    def create_server(self):
        try:
            port = int(self.port_entry.get())
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('', port))
            self.server_socket.listen(1)
            self.is_server = True
            self.log(f"Server đang chạy trên port {port}")
            
            # Chạy server trong thread riêng
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except Exception as e:
            self.log(f"Lỗi khi tạo server: {str(e)}")
            
    def serialize_public_key(self, public_key):
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def deserialize_public_key(self, key_bytes):
        return serialization.load_pem_public_key(
            key_bytes,
            backend=default_backend()
        )

    def accept_connections(self):
        while True:
            try:
                self.client_socket, addr = self.server_socket.accept()
                self.log(f"Đã kết nối với {addr}")
                
                # Gửi khóa công khai
                public_key_bytes = self.serialize_public_key(self.public_key)
                self.client_socket.send(len(public_key_bytes).to_bytes(4, 'big'))
                self.client_socket.send(public_key_bytes)
                
                # Nhận khóa công khai từ client
                key_length = int.from_bytes(self.client_socket.recv(4), 'big')
                peer_key_bytes = self.client_socket.recv(key_length)
                self.peer_public_key = self.deserialize_public_key(peer_key_bytes)
                self.log("Đã nhận khóa công khai từ client")
                
            except Exception as e:
                self.log(f"Lỗi trong quá trình trao đổi khóa: {str(e)}")
                break
                
    def connect_to_server(self):
        try:
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.log(f"Đã kết nối tới {ip}:{port}")
            
            # Nhận khóa công khai từ server
            key_length = int.from_bytes(self.client_socket.recv(4), 'big')
            peer_key_bytes = self.client_socket.recv(key_length)
            self.peer_public_key = self.deserialize_public_key(peer_key_bytes)
            self.log("Đã nhận khóa công khai từ server")
            
            # Gửi khóa công khai
            public_key_bytes = self.serialize_public_key(self.public_key)
            self.client_socket.send(len(public_key_bytes).to_bytes(4, 'big'))
            self.client_socket.send(public_key_bytes)
            
        except Exception as e:
            self.log(f"Lỗi khi kết nối: {str(e)}")
            
    def sign_file(self, file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            
        signature = self.private_key.sign(
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode()
        
    def verify_signature(self, file_data, signature, public_key):
        try:
            signature_bytes = base64.b64decode(signature)
            public_key.verify(
                signature_bytes,
                file_data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            self.log(f"Lỗi xác thực chữ ký: {str(e)}")
            return False
            
    def send_file(self):
        if not self.client_socket:
            self.log("Chưa kết nối!")
            return
            
        file_path = self.file_path.get()
        if not file_path:
            self.log("Vui lòng chọn file!")
            return
            
        try:
            # Ký file
            signature = self.sign_file(file_path)
            
            # Đọc file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Gửi tên file
            filename = os.path.basename(file_path)
            filename_bytes = filename.encode()
            self.client_socket.send(len(filename_bytes).to_bytes(4, 'big'))
            self.client_socket.send(filename_bytes)
            
            # Gửi chữ ký
            signature_bytes = signature.encode()
            self.client_socket.send(len(signature_bytes).to_bytes(4, 'big'))
            self.client_socket.send(signature_bytes)
            
            # Gửi kích thước file
            self.client_socket.send(len(file_data).to_bytes(8, 'big'))
            
            # Gửi nội dung file
            self.client_socket.sendall(file_data)
                
            self.log(f"Đã gửi file {filename} thành công!")
        except Exception as e:
            self.log(f"Lỗi khi gửi file: {str(e)}")
            
    def receive_file(self):
        if not self.client_socket:
            self.log("Chưa kết nối!")
            return
            
        if not self.peer_public_key:
            self.log("Chưa có khóa công khai của người gửi!")
            return
            
        try:
            # Nhận tên file
            filename_length = int.from_bytes(self.client_socket.recv(4), 'big')
            filename = self.client_socket.recv(filename_length).decode()
            
            # Nhận chữ ký
            signature_length = int.from_bytes(self.client_socket.recv(4), 'big')
            signature = self.client_socket.recv(signature_length).decode()
            
            # Nhận kích thước file
            file_size = int.from_bytes(self.client_socket.recv(8), 'big')
            
            # Nhận nội dung file
            file_data = b""
            bytes_received = 0
            while bytes_received < file_size:
                chunk = self.client_socket.recv(min(4096, file_size - bytes_received))
                if not chunk:
                    break
                file_data += chunk
                bytes_received += len(chunk)
                
            if bytes_received != file_size:
                self.log("Lỗi: Không nhận đủ dữ liệu file!")
                return
                
            # Xác thực chữ ký
            if self.verify_signature(file_data, signature, self.peer_public_key):
                # Lưu file
                save_path = filedialog.asksaveasfilename(
                    defaultextension=os.path.splitext(filename)[1],
                    initialfile=filename
                )
                if save_path:
                    with open(save_path, 'wb') as f:
                        f.write(file_data)
                    self.log(f"Đã nhận và xác thực file {filename} thành công!")
            else:
                self.log("Chữ ký không hợp lệ!")
        except Exception as e:
            self.log(f"Lỗi khi nhận file: {str(e)}")
            
    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop() 