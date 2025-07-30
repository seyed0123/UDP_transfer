# File Transfer System over UDP Protocol

This project implements a reliable file transfer system using the UDP protocol, designed to ensure accurate and efficient data transmission even in environments prone to packet loss or errors. The system supports parallel server connections for redundancy and faster transfers, while incorporating error checking with SHA-256 checksums to guarantee data integrity. Communication occurs over port 10526, with clients broadcasting requests and servers responding if they host the requested file.

The transfer process begins when a client broadcasts a request across the network. Servers listening on the designated port check if they have the requested file and respond with metadata including the number of chunks and a hash of the original file. Each file is divided into 1KB chunks, which are sent in random order to avoid congestion and improve efficiency. As the client receives these chunks, it verifies each one using its checksum, tracks missing pieces, and requests retransmission as needed. Once all chunks are received and validated, the client reconstructs the file and performs a final hash comparison to ensure complete accuracy.

To use the system, run the server module to make files available for transfer and the client module to request specific files from the network. Multiple servers can serve the same file simultaneously, increasing reliability and speed by allowing the client to receive different chunks from different sources. While best suited for local networks due to UDP broadcast constraints, this implementation demonstrates how reliability and efficiency can be achieved over an inherently unreliable transport protocol through thoughtful design and error-handling strategies.

## Project Structure

```
project/
├── client/              # Client implementation
│   └── data/            # Directory for downloaded files
└── server/              # Server implementation
    └── data/            # Directory for served files
```

## How It Works

### Communication Flow

1. **Initial Request Phase**
   - Client broadcasts `get <filename>` request
   - Waits 10 seconds for responses (retries up to 10 times)

2. **Server Response**
   - Server checks for requested file
   - If available, responds with:
     ```
     except <chunk_count> chunks <file_hash>
     ```
   - Prepares shuffled chunks of file data (1KB each)

3. **Data Transfer Phase**
   - Server sends chunks in random order with format:
     ```
     struct.pack(f'!II{chunk_size}s32s', chunk_number, chunk_size, chunk_data, checksum)
     ```
   - Client:
     - Maintains list of received chunks
     - Verifies each chunk's checksum
     - Tracks missing chunks
     - Requests retransmission if needed

4. **Completion Phase**
   - Client assembles file when all chunks received
   - Verifies final file hash matches server's original hash

## Example Usage

**Server Output:**
```txt
Waiting for client to request
Received request for file: example.txt
Sending example.txt to ('192.168.161.26', 52072)
Sent chunk 1
Sent chunk 2
Sent chunk 0
```

**Client Output:**
```txt
Broadcasting request for file
Server found: ('192.168.161.26', 10526) the data is ['except', '3', 'chunks', '29265671788ccd39a7cb18aa66ed535a4896a781269880aad609b93bfc2588f3']
File /home/seyed/code/python/network/client/data/example.txt received successfully.
```

## Command Line Usage

### Basic Commands

**Start server:**
```bash
python main.py server [--port 10526]
```

**Request file:**
```bash
python main.py get filename [--port 10526]
```

### Help Options

View server options:
```bash
python main.py server --help
```

View client options:
```bash
python main.py get --help
```

## Key Features

- **Parallel Server Support**: Multiple servers can respond simultaneously
- **Error Resilience**:
  - Checksum verification for each chunk
  - Automatic retransmission of missing chunks
  - Final file hash verification
- **Efficient Transfer**:
  - Shuffled chunk order prevents network congestion
  - Duplicate chunk detection

## Notes

- The system works best in local networks due to UDP broadcast limitations
- File chunks are 1KB by default (adjustable via `CHUNK_SIZE`)
- Multiple servers serving the same file will automatically provide redundancy
