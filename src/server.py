import socket
import struct
import threading

class CalculationServer:
    def __init__(self, host='localhost', tcp_port=12345, udp_port=12346):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        
    def calculate(self, operation, numbers):
        if operation == b'SUM':
            return sum(numbers)
        elif operation == b'PRO':
            result = 1
            for num in numbers:
                result *= num
            return result
        elif operation == b'MIN':
            return min(numbers)
        elif operation == b'MAX':
            return max(numbers)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    def process_request(self, data):
        # Unpack ID (unsigned int, 4 bytes)
        task_id = struct.unpack('!I', data[:4])[0]
        
        # Get operation (UTF-8 string, 3 bytes)
        operation = data[4:7]
        
        # Unpack N (unsigned char, 1 byte)
        n = struct.unpack('!B', data[7:8])[0]
        
        # Unpack numbers (signed int, 4 bytes each)
        numbers = []
        for i in range(n):
            start = 8 + i * 4
            num = struct.unpack('!i', data[start:start + 4])[0]
            numbers.append(num)
            
        # Calculate result
        result = self.calculate(operation, numbers)
        
        # Pack response
        return struct.pack('!Ii', task_id, result)

    def handle_tcp_client(self, client_socket):
        try:
            # Receive length of incoming data first (4 bytes for length)
            length_data = client_socket.recv(4)
            if not length_data:
                return
            
            length = struct.unpack('!I', length_data)[0]
            data = client_socket.recv(length)
            
            response = self.process_request(data)
            
            # Send response length followed by response
            client_socket.send(struct.pack('!I', len(response)))
            client_socket.send(response)
        finally:
            client_socket.close()

    def start_tcp_server(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((self.host, self.tcp_port))
        tcp_socket.listen(5)
        print(f"TCP Server listening on {self.host}:{self.tcp_port}")
        
        while True:
            client_socket, addr = tcp_socket.accept()
            print(f"TCP Connection from {addr}")
            client_thread = threading.Thread(
                target=self.handle_tcp_client,
                args=(client_socket,)
            )
            client_thread.start()

    def start_udp_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.host, self.udp_port))
        print(f"UDP Server listening on {self.host}:{self.udp_port}")
        
        while True:
            data, addr = udp_socket.recvfrom(1024)
            print(f"UDP Request from {addr}")
            response = self.process_request(data)
            udp_socket.sendto(response, addr)

    def start(self):
        # Start TCP and UDP servers in separate threads
        tcp_thread = threading.Thread(target=self.start_tcp_server)
        udp_thread = threading.Thread(target=self.start_udp_server)
        
        tcp_thread.start()
        udp_thread.start()