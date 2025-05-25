# server_processpool.py
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import logging
import json
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from file_protocol import FileProtocol

# Fungsi yang diproses di dalam child process
def handle_client_process(data_received):
    try:
        fp = FileProtocol()
        data_received = data_received.replace("\r\n\r\n", "")
        hasil = fp.proses_string(data_received)
        return hasil + "\r\n\r\n"
    except Exception as e:
        logging.warning(f"[PROCESS ERROR] {e}")
        return json.dumps({"status": "ERROR", "data": "internal error"}) + "\r\n\r\n"

# Fungsi utama server
def main():
    ip_address = '0.0.0.0'
    port = 8889
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind((ip_address, port))
    server_socket.listen(20)  # Naikkan backlog untuk stress test
    logging.warning(f"[PROCESS POOL] Server listening at {ip_address}:{port}")

    with ProcessPoolExecutor(max_workers=5) as executor:
        while True:
            try:
                conn, addr = server_socket.accept()
                logging.warning(f"[CONNECTION] From {addr}")

                data_received = ""
                while True:
                    data = conn.recv(4096*4096)
                    if not data:
                        break
                    data_received += data.decode()
                    if "\r\n\r\n" in data_received:
                        break

                # Kirim data ke proses pool
                future = executor.submit(handle_client_process, data_received)

                try:
                    hasil = future.result(timeout=30)
                    if isinstance(hasil, str):
                        conn.sendall(hasil.encode())
                    else:
                        logging.warning("[ERROR] hasil dari future bukan string")
                        conn.sendall(json.dumps({"status": "ERROR", "data": "invalid response"}).encode())

                except TimeoutError:
                    logging.warning("[TIMEOUT] Client processing timed out")
                    conn.sendall(json.dumps({"status": "ERROR", "data": "processing timeout"}).encode())

                except Exception as e:
                    logging.warning(f"[FUTURE ERROR] {e}")
                    conn.sendall(json.dumps({"status": "ERROR", "data": "internal error"}).encode())

                finally:
                    conn.close()

            except Exception as e:
                logging.warning(f"[SERVER ERROR] {e}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main()
