import socket
import threading
import time
from enum import Enum

continue_scanning = True
print_lock = threading.Lock()
scan_results = {
    'tcp_open': [],
    'udp_open': [],
    'udp_no_response': [],
    'udp_error_10054': []
}

class PortStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    NO_RESPONSE = "no_response"
    ERROR_10054 = "error_10054"

def scan_tcp_port(target, port):
    global continue_scanning
    
    while continue_scanning:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            
            result = s.connect_ex((target, port))
            
            if result == 0:
                with print_lock:
                    print(f'TCP Port {port} is open!')
                    scan_results['tcp_open'].append(port)
            s.close()
            
        except Exception as e:
            with print_lock:
                print(f'Error scanning TCP port {port}: {str(e)}')
        
        break

def scan_udp_port(target, port):
    global continue_scanning
    
    while continue_scanning:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            
            message = b"Test message"
            s.sendto(message, (target, port))
            
            try:
                data, addr = s.recvfrom(1024)
                with print_lock:
                    print(f'UDP Port {port} is open')
                    scan_results['udp_open'].append(port)
            
            except socket.timeout:
                with print_lock:
                    print(f'UDP Port {port}: No answer')
                    scan_results['udp_no_response'].append(port)
            
            except socket.error as e:
                if e.winerror == 10054:
                    with print_lock:
                        print(f'UDP Port {port}: ICMP Port Unreachable (10054)')
                        scan_results['udp_error_10054'].append(port)
                else:
                    with print_lock:
                        print(f'UDP Port {port}: different error: {str(e)}')
            
            s.close()
            
        except Exception as e:
            with print_lock:
                print(f'Error scanning UDP Port {port}: {str(e)}')
        
        break

def main():
    global continue_scanning
    
    target = "141.37.168.26"
    start_port = 1
    end_port = 50
    max_threads = 10
    
    print(f'Starting TCP/UDP Port-Scan for IP: {target} from Port {start_port} to {end_port}')
    
    try:
        threads = []
        
        for port in range(start_port, end_port + 1):
            while len(threads) >= max_threads:
                threads = [t for t in threads if t.is_alive()]
                time.sleep(0.1)
            
            tcp_thread = threading.Thread(target=scan_tcp_port, args=(target, port))
            tcp_thread.daemon = True
            tcp_thread.start()
            threads.append(tcp_thread)

            udp_thread = threading.Thread(target=scan_udp_port, args=(target, port))
            udp_thread.daemon = True
            udp_thread.start()
            threads.append(udp_thread)

        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\nInterrupting scan...")
        continue_scanning = False
        for thread in threads:
            thread.join()
    
    # Ergebnisse ausgeben
    print("\nScan finished!")
    print("\nTCP Results:")
    print("Open Ports:", sorted(scan_results['tcp_open']))
    
    print("\nUDP Results:")
    print("Open Ports:", sorted(scan_results['udp_open']))
    print("No Answer:", sorted(scan_results['udp_no_response']))
    print("ICMP Port Unreachable (10054):", sorted(scan_results['udp_error_10054']))

if __name__ == "__main__":
    main()