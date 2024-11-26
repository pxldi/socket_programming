import threading

from client import CalculationClient
from server import CalculationServer

if __name__ == '__main__':
    # Start server
    server = CalculationServer()
    server_thread = threading.Thread(target=server.start)
    server_thread.start()

    # Create client
    client = CalculationClient()

    # Test calculations
    test_cases = [
        (1, "SUM", [1, 2, 3, 4, 5]),
        (2, "PRO", [2, 3, 4]),
        (3, "MIN", [-5, 0, 5, 10]),
        (4, "MAX", [1, 100, 50, 25])
    ]

    # Test both TCP and UDP
    for task_id, op, numbers in test_cases:
        # TCP test
        tcp_id, tcp_result = client.send_tcp_request(task_id, op, numbers)
        print(f"TCP - Task {tcp_id}: {op}({numbers}) = {tcp_result}")

        # UDP test
        udp_id, udp_result = client.send_udp_request(task_id, op, numbers)
        print(f"UDP - Task {udp_id}: {op}({numbers}) = {udp_result}")