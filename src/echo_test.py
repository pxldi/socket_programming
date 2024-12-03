import socket
import time

def test_tcp_echo(host, message):
    print("\n=== TCP ECHO Test ===")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        print(f"Verbindungsaufbau zu {host}:7 (TCP)...")
        s.connect((host, 7))
        print("Verbindung hergestellt!")
        print(f"Sende Nachricht: {message}")
        s.send(message.encode())
        response = s.recv(1024).decode()
        print(f"Empfangene Antwort: {response}")
        s.close()
        return True
        
    except Exception as e:
        print(f"TCP ECHO Test fehlgeschlagen: {str(e)}")
        return False

def test_udp_echo(host, message):
    print("\n=== UDP ECHO Test ===")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        print(f"Sende Nachricht an {host}:7 (UDP): {message}")
        s.sendto(message.encode(), (host, 7))
        data, addr = s.recvfrom(1024)
        response = data.decode()
        print(f"Empfangene Antwort von {addr}: {response}")
        s.close()
        return True
        
    except Exception as e:
        print(f"UDP ECHO Test fehlgeschlagen: {str(e)}")
        return False

def main():
    host = "141.37.168.26"
    test_message = "Hello ECHO Server!"
    tcp_result = test_tcp_echo(host, test_message)
    time.sleep(1)
    udp_result = test_udp_echo(host, test_message)
    print("\n=== Testergebnisse ===")
    print(f"TCP ECHO Test: {'Erfolgreich' if tcp_result else 'Fehlgeschlagen'}")
    print(f"UDP ECHO Test: {'Erfolgreich' if udp_result else 'Fehlgeschlagen'}")

if __name__ == "__main__":
    main()