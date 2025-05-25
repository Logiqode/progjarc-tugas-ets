import time
import concurrent.futures
import os
import csv
from file_client_cli import remote_upload, remote_get, set_server_address

# Konfigurasi global
SERVER_IP = "127.0.0.1"
THREADPOOL_PORT = 7777
PROCESSPOOL_PORT = 8889

FILES_DIR = "files"
os.makedirs(FILES_DIR, exist_ok=True)

# Kombinasi parameter stress test
OPERATIONS = ["upload", "download"]
CLIENT_WORKERS = [1, 5, 50]
SERVER_WORKERS = [1, 5, 50]

# Pilihan volume
def pilih_volume():
    print("Pilih workload volume:")
    print("1. 10MB")
    print("2. 50MB")
    print("3. 100MB")
    pilihan = input("Masukkan pilihan (1/2/3): ").strip()
    mapping = {'1': 10, '2': 50, '3': 100}
    return mapping.get(pilihan, 10)  # Default ke 10MB

# Pembuatan semua file uji di awal
def generate_all_test_files():
    for volume in [10, 50, 100]:
        fname = f"testfile_{volume}MB.dat"
        size_bytes = volume * 1024 * 1024
        path = os.path.join(FILES_DIR, fname)
        if not os.path.exists(path) or os.path.getsize(path) != size_bytes:
            print(f"🔧 Membuat file {fname} ({volume}MB)...")
            with open(path, "wb") as f:
                f.write(os.urandom(size_bytes))
        else:
            print(f"✅ File {fname} sudah ada, dilewati.")

def run_task(op, filename):
    if op == "upload":
        return remote_upload(filename)
    elif op == "download":
        return remote_get(filename)
    return False

def run_stress_test(op, volume, client_worker, server_worker, use_thread=True):
    port = THREADPOOL_PORT if use_thread else PROCESSPOOL_PORT
    set_server_address(SERVER_IP, port)

    fname = f"testfile_{volume}MB.dat"

    # Upload dulu kalau download
    if op == "download":
        set_server_address(SERVER_IP, THREADPOOL_PORT)
        remote_upload(fname)
        set_server_address(SERVER_IP, port)

    start_time = time.perf_counter()
    success = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=client_worker) as executor:
        futures = [executor.submit(run_task, op, fname) for _ in range(client_worker)]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1
    end_time = time.perf_counter()

    duration = end_time - start_time
    total_bytes = volume * 1024 * 1024 * success
    throughput = total_bytes / duration if duration > 0 else 0

    return {
        "operation": op,
        "volume": volume,
        "client_worker": client_worker,
        "server_worker": server_worker,
        "time_total": round(duration, 4),
        "throughput": round(throughput, 2),
        "client_success": success,
        "client_failed": failed,
        "server_success": success,
        "server_failed": failed,
        "server_type": "thread" if use_thread else "process"
    }

def save_results(results, volume):
    filename = f"stress_test_results_{volume}MB.csv"
    with open(filename, "w", newline="") as csvfile:
        fieldnames = [
            "operation", "volume", "client_worker", "server_worker",
            "time_total", "throughput", "client_success", "client_failed",
            "server_success", "server_failed", "server_type"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    print("📁 Mengecek dan membuat file uji...")
    generate_all_test_files()

    selected_volume = pilih_volume()
    all_results = []

    for op in OPERATIONS:
        for cw in CLIENT_WORKERS:
            for sw in SERVER_WORKERS:
                print(f"▶️  Running {op}, {selected_volume}MB, client {cw}, server {sw} [THREAD]")
                res_thread = run_stress_test(op, selected_volume, cw, sw, use_thread=True)
                all_results.append(res_thread)

                print(f"▶️  Running {op}, {selected_volume}MB, client {cw}, server {sw} [PROCESS]")
                res_process = run_stress_test(op, selected_volume, cw, sw, use_thread=False)
                all_results.append(res_process)

    save_results(all_results, selected_volume)
    print(f"✅ Stress test selesai. Hasil disimpan di stress_test_results_{selected_volume}MB.csv")

    import sys
    sys.exit(0)


if __name__ == "__main__":
    main()
