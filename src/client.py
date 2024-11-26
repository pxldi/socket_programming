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
            
            sock.send(struct.pack('!I', len(request)))
            sock.send(request)
            
            length = struct.unpack('!I', sock.recv(4))[0]
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
        
client = CalculationClient()

test_cases = [
    (1, "SUM", [1, 2, 3, 4, 5]),
    (2, "PRO", [2, 3, 4]),
    (3, "MIN", [-5, 0, 5, 10]),
    (4, "MAX", [1, 100, 50, 25])
]

for task_id, op, numbers in test_cases:
    tcp_id, tcp_result = client.send_tcp_request(task_id, op, numbers)
    print(f"TCP - Task {tcp_id}: {op}({numbers}) = {tcp_result}")

    udp_id, udp_result = client.send_udp_request(task_id, op, numbers)
    print(f"UDP - Task {udp_id}: {op}({numbers}) = {udp_result}")