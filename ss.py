###############################################
# Group Name  : MC/TC/TS

# Member1 Name: Michael Cucina
# Member1 CSU ID: 832-740-147
# Member1 Login eID: mcucina

# Member2 Name: Tani Cath
# Member2 CSU ID: 835-261-302
# Member2 Login eID: tcath

# Member3 Name: Travis Schroeder
# Member3 CSU ID: 831-499-908
# Member3 Login ID: tschroe
###############################################

import sys
import socket
import selectors
import types

import random
import ast
import os


sel = selectors.DefaultSelector()

tmp = "tmp-"+socket.gethostname()
filename = "file-"+socket.gethostname()

# this routine is called when the LISTENING SOCKET gets a 
# connection request from a new client

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print("Accepted connection from", addr)
    data = types.SimpleNamespace(addr=addr, messages=[], inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


# this routine is called when a client is ready to read or write data  

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    chunk_size = 1024
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            try:
                byte_data = process_data(recv_data, sock)
                data.messages = byte_data
            except:
                print("error", sys.exc_info()[0])
                data.outb += recv_data
        else:
            print("Closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        i = 0
        prev_chunk = None
        with open(filename, 'rb') as in_file:
            while True:
                chunk = in_file.read(chunk_size)
                i += len(chunk)
                if chunk == prev_chunk:
                    print('Done. Closing socket.')
                    try:
                        os.system(f'rm -f {filename}')
                    except:
                        print()
                    sock.send(b'end')
                    sock.close()
                    sel.close()
                    exit(0)
                prev_chunk = chunk
                sock.send(chunk)
                
def process_data(recv_data, sock):
    byte_data = None
    data = recv_data.decode()
    url, chainlist = data.split(' ', 1)
    chainlist = ast.literal_eval(chainlist)
    
    if chainlist[0] == 0:
        os.system(f'wget -O {filename} {url}')
        byte_data = [] 
    else:
        url, chainlist, ip, port = read_input(url, chainlist)
        payload = create_payload(url, chainlist)
        print(payload)
        byte_data = connect_to_next(ip, port, payload)
        
        
    return byte_data 
        
def read_file():
    chunk_size = 1024
    data = []
    
    with open(filename, "rb") as in_file:
        while True:
            chunk = in_file.read(chunk_size)
            if chunk == b"":
                try:
                    os.system(f'rm -f {filename}')
                except:
                    print()
                break
            data.append(chunk)
            
    print("File read. Deleting file.")
    x = 0
    for i in data:
        x += len(i)
    print(f'File read. Total: {x}')
    return data

def read_input(url, chainlist):
    print("Request file from: " + url)
    print(f'Chainlist ({chainlist[0]}):')
    for i in range(int(chainlist[0])):
        ss = chainlist[i+1].split(' ')
        print(ss[0] + ', ' + ss[1])
    
    next_socket = random.choice(chainlist[1:])
    chainlist.remove(next_socket)
    chainlist[0] = int(chainlist[0]) - 1
    ip, port = next_socket.split()
    return url, chainlist, ip, int(port)

def create_payload(url, chainlist):
    test_tuple = (url,str(chainlist))
    payload = bytes(' '.join(test_tuple), 'utf-8')
    
    return payload

def connect_to_next(host, port, payload):
    server_addr = (host, port)
    print(f'Connecting to {host} on port {port}.')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_addr)
    sock.sendall(payload)
    recv_data = []
    i = 0
    with open(tmp, "wb") as in_file:
        while True:
            data = sock.recv(1024)
            if data == b'end' or data == b'' or data == None:
                print("File received.")
                print(f'Received Total: {i}')
                try:
                    os.system(f'mv -f {tmp} {filename}')
                except:
                    print()
                break
            in_file.write(data)
            i += len(data) 
    sock.close()
        
    return recv_data

            
def get_host():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return host, ip


# main program: set up the host address and port; change them if you need to

if sys.argv[1] != "-p" or len(sys.argv) > 3:
    print("Invalid arguments, usage: ./python ss.py [-p portnum]")
    exit(1)
try:
    port = int(sys.argv[2])
except:
    print("Invalid literal for port number, port number must be an int")
    exit(1)
if(port < 1024 or port > 49151):
    print("Invalid port number, must be in between 1024 and 49151")
    exit(1)
# set up the listening socket and register it with the SELECT mechanism
host, ip = get_host()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Attempting to bind to port ", port)
sock.bind((ip, port))
print("Binding successful")
sock.listen()
print(f'This host is \"{host}\" with IP {ip}.\nListening on port {port}...')
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, data=None)

# the main event loop
try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    print("\nCaught keyboard interrupt. Exiting.")
finally:
    sel.close()