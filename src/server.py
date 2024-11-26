import socket
import struct
import threading
import time

class CalculationServer:
    def __init__(self, host='localhost', tcp_port=12345, udp_port=12346):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.stop_flag = False
        socket.setdefaulttimeout(30)
        
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
        task_id = struct.unpack('!I', data[:4])[0]
        
        operation = data[4:7]
        
        n = struct.unpack('!B', data[7:8])[0]
        
        numbers = []
        for i in range(n):
            start = 8 + i * 4
            num = struct.unpack('!i', data[start:start + 4])[0]
            numbers.append(num)
            
        result = self.calculate(operation, numbers)
        
        return struct.pack('!Ii', task_id, result)

    def handle_tcp_client(self, client_socket):
        try:
            while not self.stop_flag:
                try: 
                    length_data = client_socket.recv(4)
                    if not length_data:
                        return
                    
                    length = struct.unpack('!I', length_data)[0]
                    data = client_socket.recv(length)
                    
                    response = self.process_request(data)

                    client_socket.send(struct.pack('!I', len(response)))
                    client_socket.send(response)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error handling client: {e}")
                    break
        finally:
            client_socket.close()

    def start_tcp_server(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind((self.host, self.tcp_port))
        tcp_socket.listen(5)
        print(f"TCP Server listening on {self.host}:{self.tcp_port}")
        
        while not self.stop_flag:
            try:
                client_socket, addr = self.tcp_socket.accept()
                print(f"TCP Connection from {addr}")
                client_thread = threading.Thread(
                    target=self.handle_tcp_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error accepting connection: {e}")
                if self.stop_flag:
                    break

    def start_udp_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.host, self.udp_port))
        print(f"UDP Server listening on {self.host}:{self.udp_port}")
        
        while not self.stop_flag:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                print(f"UDP Request from {addr}")
                response = self.process_request(data)
                self.udp_socket.sendto(response, addr)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"UDP Error: {e}")
                if self.stop_flag:
                    break

    def stop(self):
        print("Stopping server...")
        self.stop_flag = True
        if self.tcp_socket:
            self.tcp_socket.close()
        if self.udp_socket:
            self.udp_socket.close()

    def start(self):
        self.stop_flag = False
        tcp_thread = threading.Thread(target=self.start_tcp_server)
        udp_thread = threading.Thread(target=self.start_udp_server)
        
        tcp_thread.daemon = True
        udp_thread.daemon = True
        
        tcp_thread.start()
        udp_thread.start()
        
        return tcp_thread, udp_thread

if __name__ == "__main__":
    server = CalculationServer()
    try:
        server.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()