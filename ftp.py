import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

class FTPClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FTP Client")

        # 服务器地址输入
        tk.Label(root, text="Server Address:").grid(row=0, column=0, padx=10, pady=5)
        self.server_entry = tk.Entry(root)
        self.server_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # 服务端端口号输入
        tk.Label(root, text="Server Port:").grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = tk.Entry(root)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)

        # 用户名输入
        tk.Label(root, text="Username:").grid(row=2, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.grid(row=2, column=1, padx=10, pady=5)

        # 密码输入
        tk.Label(root, text="Password:").grid(row=3, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        # 连接按钮
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_ftp)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)

        # 文件列表框
        self.file_listbox = tk.Listbox(root, width=50, height=10)
        self.file_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # 操作按钮
        self.download_button = tk.Button(root, text="Download", command=self.download_file)
        self.download_button.grid(row=6, column=0, pady=5)
        
        self.upload_button = tk.Button(root, text="Upload", command=self.upload_file)
        self.upload_button.grid(row=6, column=1, pady=5)
        
        self.delete_button = tk.Button(root, text="Delete", command=self.delete_file)
        self.delete_button.grid(row=7, column=0, pady=5)
        
        self.rename_button = tk.Button(root, text="Rename", command=self.rename_file)
        self.rename_button.grid(row=7, column=1, pady=5)

        # 响应文本框
        self.response_text = scrolledtext.ScrolledText(root, width=50, height=10)
        self.response_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def connect_to_ftp(self):
        server = self.server_entry.get()
        port = self.port_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            # 建立 socket
            self.ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ftp_socket.connect((server, int(port)))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 发送 USER 命令
            self.ftp_socket.sendall(f"USER {username}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 发送 PASS 命令
            self.ftp_socket.sendall(f"PASS {password}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            if response.startswith('230'):
                messagebox.showinfo("Info", "Login successful!")
                # List directory contents
                self.list_directory()
            else:
                messagebox.showerror("Error", "Login failed!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to FTP server: {e}")

    def list_directory(self):
        try:
            # 进入被动模式
            self.ftp_socket.sendall("PASV\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 解析 PASV 响应
            pasv_info = response.split('(')[1].split(')')[0].split(',')
            data_ip = '.'.join(pasv_info[:4])
            data_port = int(pasv_info[4]) * 256 + int(pasv_info[5])

            # 建立数据连接
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((data_ip, data_port))

            # 发送 LIST 命令
            self.ftp_socket.sendall("LIST\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 接收数据
            data_response = data_socket.recv(4096).decode('utf-8')
            self.file_listbox.delete(0, tk.END)
            for line in data_response.splitlines():
                self.file_listbox.insert(tk.END, line)

            # 关闭数据连接
            data_socket.close()

            # 接收服务器响应
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to list directory: {e}")

    def download_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return

        filename = self.file_listbox.get(selected[0]).split()[-1]  # 假设文件名在最后

        try:
            # 进入被动模式
            self.ftp_socket.sendall("PASV\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 解析 PASV 响应
            pasv_info = response.split('(')[1].split(')')[0].split(',')
            data_ip = '.'.join(pasv_info[:4])
            data_port = int(pasv_info[4]) * 256 + int(pasv_info[5])

            # 建立数据连接
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((data_ip, data_port))

            # 发送 RETR 命令
            self.ftp_socket.sendall(f"RETR {filename}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 检查 RETR 命令的响应
            if response.startswith('150') or response.startswith('125'):
                with open(filename, 'wb') as f:
                    while True:
                        data = data_socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                self.response_text.insert(tk.END, f"Downloaded {filename}\n")
                data_socket.close()

                # 接收服务器响应
                response = self.ftp_socket.recv(1024).decode('utf-8')
                self.response_text.insert(tk.END, response + '\n')
            else:
                messagebox.showerror("Error", "Failed to download file!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {e}")

    def upload_file(self):
        filename = simpledialog.askstring("Input", "Enter the file path to upload:")
        if not filename:
            return

        try:
            # 进入被动模式
            self.ftp_socket.sendall("PASV\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 解析 PASV 响应
            pasv_info = response.split('(')[1].split(')')[0].split(',')
            data_ip = '.'.join(pasv_info[:4])
            data_port = int(pasv_info[4]) * 256 + int(pasv_info[5])

            # 建立数据连接
            data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            data_socket.connect((data_ip, data_port))

            # 发送 STOR 命令
            remote_filename = filename.split("/")[-1]
            self.ftp_socket.sendall(f"STOR {remote_filename}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            # 检查 STOR 命令的响应
            if response.startswith('150') or response.startswith('125'):
                with open(filename, 'rb') as f:
                    while True:
                        data = f.read(4096)
                        if not data:
                            break
                        data_socket.sendall(data)
                self.response_text.insert(tk.END, f"Uploaded {remote_filename}\n")
                data_socket.close()

                # 接收服务器响应
                response = self.ftp_socket.recv(1024).decode('utf-8')
                self.response_text.insert(tk.END, response + '\n')
                self.list_directory()
            else:
                messagebox.showerror("Error", "Failed to upload file!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload file: {e}")

    def delete_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return

        filename = self.file_listbox.get(selected[0]).split()[-1]  # 假设文件名在最后

        try:
            # 发送 DELE 命令
            self.ftp_socket.sendall(f"DELE {filename}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            if response.startswith('250'):
                self.response_text.insert(tk.END, f"Deleted {filename}\n")
                self.list_directory()
            else:
                messagebox.showerror("Error", "Failed to delete file!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {e}")

    def rename_file(self):
        selected = self.file_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "No file selected")
            return

        old_filename = self.file_listbox.get(selected[0]).split()[-1]  # 假设文件名在最后
        new_filename = simpledialog.askstring("Input", "Enter the new file name:")
        if not new_filename:
            return

        try:
            # 发送 RNFR 命令
            self.ftp_socket.sendall(f"RNFR {old_filename}\r\n".encode('utf-8'))
            response = self.ftp_socket.recv(1024).decode('utf-8')
            self.response_text.insert(tk.END, response + '\n')

            if response.startswith('350'):
                # 发送 RNTO 命令
                self.ftp_socket.sendall(f"RNTO {new_filename}\r\n".encode('utf-8'))
                response = self.ftp_socket.recv(1024).decode('utf-8')
                self.response_text.insert(tk.END, response + '\n')

                if response.startswith('250'):
                    self.response_text.insert(tk.END, f"Renamed {old_filename} to {new_filename}\n")
                    self.list_directory()
                else:
                    messagebox.showerror("Error", "Failed to rename file!")
            else:
                messagebox.showerror("Error", "Failed to rename file!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FTPClientGUI(root)
    root.mainloop()


#101.43.149.67
