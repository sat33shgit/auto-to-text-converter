"""
Launcher script for the web-based audio to text converter.
Automatically finds an available port and starts the server.
"""

import socket
from web_converter import AudioToTextWebServer

def find_free_port():
    """Find a free port to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def main():
    """Start the web converter on an available port."""
    print("Finding available port...")
    
    # Try common ports first
    preferred_ports = [8080, 8081, 8000, 8888, 9000]
    
    for port in preferred_ports:
        try:
            server = AudioToTextWebServer(port)
            print(f"Trying port {port}...")
            server.start_server()
            break
        except OSError as e:
            if "Only one usage" in str(e) or "Address already in use" in str(e):
                print(f"Port {port} is already in use, trying next...")
                continue
            else:
                print(f"Error on port {port}: {e}")
                continue
        except KeyboardInterrupt:
            print("\nServer stopped by user.")
            break
        except Exception as e:
            print(f"Error on port {port}: {e}")
            continue
    else:
        # If all preferred ports fail, find any free port
        try:
            free_port = find_free_port()
            print(f"Using automatically found port: {free_port}")
            server = AudioToTextWebServer(free_port)
            server.start_server()
        except Exception as e:
            print(f"Failed to start server: {e}")

if __name__ == "__main__":
    main()
