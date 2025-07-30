import argparse
import sys
from client.receive import receive_file
from server.serve import handle_client
import socket

def main():
    parser = argparse.ArgumentParser(description="File Transfer System over UDP Protocol")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # Server command
    server_parser = subparsers.add_parser('server', help='Start the file server')
    server_parser.add_argument('-p', '--port', type=int, default=10526,
                             help='UDP port to listen on (default: 10526)')

    # Client command
    client_parser = subparsers.add_parser('get', help='Request a file from servers')
    client_parser.add_argument('filename', help='Name of the file to request')
    client_parser.add_argument('-p', '--port', type=int, default=10526,
                             help='UDP port to broadcast on (default: 10526)')

    args = parser.parse_args()

    if args.command == 'server':
        # print(f"Starting server on port {args.port}")
        handle_client(args.port)
    elif args.command == 'get':
        # print(f"Requesting file '{args.filename}' from servers on port {args.port}")
        
        try:
            receive_file(args.filename, args.port)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()