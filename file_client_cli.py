import os
import base64
import json
import socket
import logging

# Simpan alamat server secara global
server_address = ('127.0.0.1', 7777)

def set_server_address(ip, port):
    global server_address
    server_address = (ip, port)

def send_command(command_str=""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        if not command_str.endswith("\r\n\r\n"):
            command_str += "\r\n\r\n"
        sock.sendall(command_str.encode())

        data_received = ""
        while True:
            data = sock.recv(4096*4096)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        hasil = json.loads(data_received)
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    
    if isinstance(hasil, dict) and hasil.get('status') == 'OK':
        print("Daftar file:")
        for f in hasil['data']:
            print(f"- {f}")
        return True
    else:
        print("Gagal mengambil daftar file.")
        return False


def remote_get(filename):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    
    if isinstance(hasil, dict) and hasil.get('status') == 'OK':
        namafile = os.path.basename(hasil['data_namafile'])
        isifile = base64.b64decode(hasil['data_file'])
        base_dir = os.path.abspath('files')
        os.makedirs(base_dir, exist_ok=True)
        filepath = os.path.join(base_dir, namafile)
        with open(filepath, 'wb') as f:
            f.write(isifile)
        print(f"File {namafile} berhasil diunduh ke folder files/.")
        return True
    else:
        print(f"Gagal mengunduh file: {hasil['data'] if isinstance(hasil, dict) else 'Tidak ada respons dari server'}")
        return False


def remote_upload(filename):
    try:
        safe_filename = os.path.basename(filename)
        fullpath = os.path.join('files', safe_filename)
        with open(fullpath, 'rb') as f:
            filedata = base64.b64encode(f.read()).decode()
        payload = json.dumps({
            "command": "upload",
            "filename": filename,
            "filedata": filedata
        }) + "\r\n\r\n"
        hasil = send_command(payload)
        if isinstance(hasil, dict) and hasil.get('status') == 'OK':
            print(f"Upload berhasil: {hasil['data']}")
            return True
        else:
            print(f"Gagal upload: {hasil['data'] if isinstance(hasil, dict) else 'Tidak ada respons dari server'}")
            return False
    except Exception as e:
        print(f"Error saat upload: {e}")
        return False


def remote_delete(filename):
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    
    if isinstance(hasil, dict) and hasil.get('status') == 'OK':
        print(f"File {filename} berhasil dihapus.")
        return True
    else:
        print(f"Gagal menghapus file: {hasil['data'] if isinstance(hasil, dict) else 'Tidak ada respons dari server'}")
        return False

