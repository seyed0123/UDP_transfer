import socket
import os
import hashlib
import struct
import random
import multiprocessing

CHUNK_SIZE = 1024  # 1KB chunks

def compute_checksum(data):
    return hashlib.sha256(data).digest()

def compute_fingerprint(file_name):
    sha256_hash = hashlib.sha256()
    with open(file_name, 'rb') as f:
        chunk_number = 0
        file_data = []
        while True:
            chunk_data = f.read(CHUNK_SIZE)
            if not chunk_data:
                break  # EOF reached

            checksum = compute_checksum(chunk_data)
            file_data.append((chunk_number, chunk_data, checksum))
            sha256_hash.update(chunk_data)
            chunk_number += 1

    file_hash = sha256_hash.hexdigest()
    return chunk_number,file_hash,file_data

def send_file(file_chunks, client_address,server_socket:socket.socket):
    random.shuffle(file_chunks)
    for chunk_number, chunk_data, checksum in file_chunks:
        chunk_size = len(chunk_data)
        data = struct.pack(f'!II{chunk_size}s32s', chunk_number, chunk_size, chunk_data, checksum)
        server_socket.sendto(data, client_address)
        print(f"Sent chunk {chunk_number}")


def handle_client(UDP_PORT):
    # Create UDP socket to listen for incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', UDP_PORT))
    server_socket.settimeout(60)

    print("Server listening for incoming requests")

    
    while True:
        try:
            print('Waiting for client to request')
            data, client_address = server_socket.recvfrom(1024)

            if data.startswith(b"get"):
                file_name = data.decode().split(" ")[1]
                print(f"Received request for file: {file_name}")

                base_dir = os.path.dirname(os.path.abspath(__file__))
                data_dir = os.path.join(base_dir, 'data')
                file_path = os.path.join(data_dir, file_name)
                
                if os.path.exists(file_path):
                    
                    chunk_number,file_hash,file_data = compute_fingerprint(file_path)
                    server_socket.sendto(f"except {chunk_number} chunks {file_hash}".encode('utf-8'), client_address)
                    print(f"Sending {file_name} to {client_address}")
                    send_file(file_data, client_address,server_socket)
                else:
                    print(f"File {file_name} not found on server.")

        except TimeoutError as t:
            print(t)
            break

    server_socket.close()

if __name__ == "__main__":
    UDP_PORT = 10526
    handle_client(UDP_PORT)
