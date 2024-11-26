import struct
import socket

class CalculationClient:
    def __init__(self, host='localhost', tcp_port=12345, udp_port=12346):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port

    def create_request(self, task_id, operation, numbers):
        # Pack task ID (unsigned int, 4 bytes)
        request = struct.pack('!I', task_id)
        
        # Add operation (UTF-8 encoded string)
        request += operation.encode('utf-8')
        
        # Pack number of values (unsigned char, 1 byte)
        request += struct.pack('!B', len(numbers))
        
        # Pack all numbers (signed int, 4 bytes each)
        for num in numbers:
            request += struct.pack('!i', num)
            
        return request

    def send_tcp_request(self, task_id, operation, numbers):
        request = self.create_request(task_id, operation, numbers)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.tcp_port))
            
            # Send length of request first
            sock.send(struct.pack('!I', len(request)))
            # Send actual request
            sock.send(request)
            
            # Receive response length
            length = struct.unpack('!I', sock.recv(4))[0]
            # Receive response
            response = sock.recv(length)
            
            task_id, result = struct.unpack('!Ii', response)
            return task_id, result

    def send_udp_request(self, task_id, operation, numbers):
        request = self.create_request(task_id, operation, numbers)
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(request, (self.host, self.udp_port))
            response, _ = sock.recvfrom(1024)
            
            task_id, result = struct.unpack('!Ii', response)
            return task_id, result