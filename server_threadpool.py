# server_threadpool.py
from socket import *
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

fp = FileProtocol()

def handle_client(connection, address):
    try:
        data_received = ""
        while True:
            data = connection.recv(4096*4096)
            if not data:
                break
            data_received += data.decode()
            if "\r\n\r\n" in data_received:
                break

        data_received = data_received.replace("\r\n\r\n", "")
        hasil = fp.proses_string(data_received)
        hasil = hasil + "\r\n\r\n"
        connection.sendall(hasil.encode())

    except Exception as e:
        logging.warning(f"Exception: {e}")
    finally:
        connection.close()

def main():
    ip_address = '0.0.0.0'
    port = 7777  # Port khusus untuk thread pool server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip_address, port))
    server_socket.listen(10)
    logging.warning(f"[THREAD POOL] Server berjalan di {ip_address}:{port}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            conn, addr = server_socket.accept()
            logging.warning(f"[THREAD POOL] Connection from {addr}")
            executor.submit(handle_client, conn, addr)

if __name__ == '__main__':
    main()
