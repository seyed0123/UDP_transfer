import socket
import os
import hashlib
import struct
import time

CHUNK_SIZE = 1024  # Define chunk size (1KB for example)
UDP_PORT = 10526  # UDP port for communication
BUFFER_SIZE = CHUNK_SIZE + 1024  # Buffer to receive chunk + extra data like sequence number

def compute_checksum(data):
    return hashlib.sha256(data).digest()

def compute_file_hash(file_name):
    sha256_hash = hashlib.sha256()
    with open(file_name, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def receive_file(file_name,port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(1)

    chunk_number,file_hash = find_server(file_name,client_socket,port)

    file_data = []
    expected_chunk_count = {_ for _ in range(chunk_number)}
    chunk_info = [0,0,0]
    
    while True:
        # Listen for chunks from server
        if len(expected_chunk_count) == 0:
            break
        try:
            data, _ = client_socket.recvfrom(65535)  # max UDP packet size

            # Extract the chunk_number and chunk_size first
            chunk_number, chunk_size = struct.unpack('!II', data[:8])

            # Extract chunk data and checksum
            chunk_data, checksum = struct.unpack(f'!{chunk_size}s32s', data[8:8 + chunk_size + 32])


            # Verify checksum
            if compute_checksum(chunk_data) == checksum:
                if chunk_number in expected_chunk_count:
                    file_data.append((chunk_number, chunk_data))
                    expected_chunk_count.remove(chunk_number)
                    chunk_info[0]+=1
                    # print(f"Received chunk {chunk_number}")
                else:
                    # print(f"Already has chunk {chunk_number}.Ignoring")
                    chunk_info[1]+=1
            else:
                # print(f"Checksum mismatch for chunk {chunk_number}. Retrying.")
                chunk_info[2]+=1

        except TimeoutError as t:
            print(f"send new broadcast to send the remaining data {len(expected_chunk_count)}")
            print(f"In this requests we have {chunk_info[0]} new chunk, {chunk_info[1]} duplicate chunk, {chunk_info[2]} chunk with error")
            chunk_info = [0,0,0]
            find_server(file_name,client_socket)

        except Exception as e:
            print(e)

    client_socket.close()

    # Sort chunks by sequence number and assemble file
    sha256_hash = hashlib.sha256()
    file_data.sort(key=lambda x: x[0])
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, file_name)
    with open(file_path, 'wb') as f:
        for _, chunk in file_data:
            f.write(chunk)
            sha256_hash.update(chunk)

    file_hash_cal = sha256_hash.hexdigest()
    if file_hash_cal == file_hash:
        print(f"File {file_path} received successfully.")
    else:
        print('There is a problem in the file.')

def find_server(file_name,client_socket,port=UDP_PORT,count=0):
    if count >10:
        raise TimeoutError('There is no active server in this network.')
    request_data = f"get {file_name}".encode('utf-8')
    client_socket.sendto(request_data, ('<broadcast>', port))
    print("Broadcasting request for file")

    # Listen for responses
    try:
        while True:
            data, server_address = client_socket.recvfrom(BUFFER_SIZE)
            data_list = data.decode('utf-8').split()
            if data_list[0] == 'except' and data_list[2] == 'chunks': 
                print(f"Server found: {server_address} the data is {data_list}")
                return int(data_list[1]),data_list[3]
    except Exception as e:
        return find_server(file_name,client_socket,port,count+1)

if __name__ == "__main__":
    
    file_name = "example.txt"
    receive_file(file_name)
