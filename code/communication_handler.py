import socket
import struct
import threading
import time
import json

class CommunicationHandler:
    """
    The CommunicationHandler class is responsible for communicating with other agents in the same cell as well as with the
    WMS. It is capable of communicating with the use of Sockets in a multicast as well as sending direct messages to other peers
    """

    MULTICAST_IP = '224.1.1.1'
    PORT = 5004
    INTERVAL = 5

    def __init__(self, dicover_peer_callback):
        """
        Initializes the socket and subscribes to a peer discovery event.
        """
        self.peers = set()
        self.lock = threading.Lock()
        self.running = False
        self.subscriptions = {}
        self.dicover_peer_callback = dicover_peer_callback

        self.subscribe("DISCOVER_PEER", self.handle_discover_peer)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip = self.get_local_ip()
        self.sock.bind(('', self.PORT))

        mreq = struct.pack("4sl", socket.inet_aton(self.MULTICAST_IP), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    
    def get_local_ip(self):
        """
        Returns the local ip of the agent.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('192.168.1.1', 80))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip
    
    
    def start(self):
        """
        Starts a threads listening to the socket
        """
        self.running = True
        threading.Thread(target=self.listen).start()
        threading.Thread(target=self.publish_presence).start()


    def listen(self):
        """
        listens to incomming connections and deserializes them into a message type and the message itself.
        """
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            message = data.decode('utf-8')
            type, message, ip = self.deserialize_message(message)
            self.handle_subscription(type, message, ip)

    
    def publish_presence(self):
        """
        Show other peers the presence of the agent
        """
        while self.running:
            self.send_multicast("DISCOVER_PEER", True)
            time.sleep(self.INTERVAL)

    
    def send_multicast(self, type, payload):
        """
        Sends messages as a multicast to other peers
        """
        message = self.serialize_message(type, payload, self.ip)
        
        try:
            self.sock.sendto(message.encode('utf-8'), (self.MULTICAST_IP, self.PORT))
        except Exception:
            print(f"An error uccured while sending multicast message")

    
    def send(self, address, type, payload):
        """
        Sends messages directly to other peers
        """
        message = self.serialize_message(type, payload, self.ip)
        try:
            self.sock.sendto(message.encode('utf-8'), (address, self.PORT))
        except Exception:
            print(f"Error sending message to {address}")

    
    def get_peers(self):
        """
        Returns all discovered peers
        """
        with self.lock:
            return list(self.peers)

    
    def subscribe(self, type, callback):
        """
        Adds new subscriptions to the subscription dictionary.
        """
        self.subscriptions[type] = callback

    
    def handle_subscription(self, type, message, ip):
        """
        Executes the suiting functions based on the message type
        """
        self.subscriptions[type](type, message, ip)
    
    
    def handle_discover_peer(self, type, message, ip):
        """
        Add new discovered agents to the peer_list
        """
        with self.lock:
            if ip != self.ip and ip not in self.peers:
                self.peers.add(ip)
                self.dicover_peer_callback(ip)
    

    def serialize_message(self, type, message, address):
       """
       Serializes messages into the json format for transmission
       """
       return json.dumps({
            "type": type,
            "message": message,
            "address": address
        })

    
    def deserialize_message(self, payload):
        """
        Deserializes messages from the json format into type, message and address
        """
        payload = json.loads(payload)
        return [payload["type"], payload["message"], payload["address"]]

