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
from time import sleep


sel = selectors.DefaultSelector()


# this routine is called to create each of the many ECHO CLIENTs we want to create

def start_connection(host, port, payload):
    messages = [payload]
    server_addr = (host, port)
    print(f'Connecting to {host} on port {port}.')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
        msg_total=len(payload),
        recv_total=0,
        messages=list(messages),
        outb=b"",
        )
    sel.register(sock, events, data=data)

# this routine is called when a client triggers a read or write event

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        with open(parse_url(url), "wb") as in_file:
            while True:
                data = sock.recv(1024)
                in_file.write(data)
                
                # write to a file
                if len(data) == 0:
                    print("File received.")
                    print("Name of file: " + parse_url(url))
                    exit(0)

    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("Sending:", repr(data.outb))
            print("Waiting for response...")
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def parse_url(url):
    last_slash = url.rfind("/")
    if ("http" in url and last_slash == 6):
        return "index.html"
    elif ("https" in url and last_slash == 7):
        return "index.html"
    elif (last_slash + 1 == len(url)):
        return "index.html"
    elif (last_slash == -1):
        return "index.html"
    else:
        return url.rsplit("/", 1)[1]

def read_args(url, chainlist):
    try:
        fd = open(chainlist, 'r')
    except:
        print("No such file 'chaingang.txt'")
        exit()
    chainlist = fd.read().split('\n')
    fd.close()
    print("Request file from: " + url)
    print(f'Chainlist ({chainlist[0]}):')
    for i in range(int(chainlist[0])):
        ss = chainlist[i+1].split(' ')
        print(ss[0] + ', ' + ss[1])
    
    print("Picking a random SS from the chain list.")
    next_socket = random.choice(chainlist[1:])
    chainlist.remove(next_socket)
    chainlist[0] = int(chainlist[0]) - 1
    ip, port = next_socket.split()
    return url, chainlist, ip, int(port)

def create_payload(url, chainlist):
    test_tuple = (url,str(chainlist))
    payload = bytes(' '.join(test_tuple), 'utf-8')
    
    return payload

# main program
   
chainFile = "chaingang.txt"
if len(sys.argv) < 2:
    exit(1)
elif len(sys.argv) == 4 and sys.argv[2] == "-c":
    chainFile = sys.argv[3]
elif len(sys.argv) != 2:
    print("Improper arguments, usage: ./python awget.py [URL] [-c chainfile]")
    exit(1)
    
    
url, chainlist, ip, port = read_args(sys.argv[1], chainFile)
payload = create_payload(url, chainlist)

start_connection(ip, port, payload)

returned_data = []

# the event loop

try:
    while True:
        events = sel.select(timeout=None)
        if events:
            for key, mask in events:
                returned_data = service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("\nCaught keyboard interrupt. Exiting.")
finally:
    sel.close()
    
print(returned_data)
print(len(returned_data[0]))