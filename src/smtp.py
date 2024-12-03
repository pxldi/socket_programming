"""
Sends an email using the SMTP protocol.
"""

import socket
import base64
import ssl
import time
import argparse


def print_info(text: str, end="\n") -> None:
    """
    Prints the given text in blue.
    Args:
        text (str): The text to be printed.
    Returns:
        None
    """
    print(f"\033[94m{text}\033[0m", end=end)

def build_connection() -> socket.socket:
    """
    Builds a connection to the SMTP server.
    Returns:
        socket.socket: The socket object used for communication.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print_info("Connecting to asmtp.htwg-konstanz.de...")
    s.connect(("asmtp.htwg-konstanz.de", 587))
    print_info("Connected to asmtp.htwg-konstanz.de.")
    
    # Empfange initiale Begrüßung
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending EHLO...")
    s.send(b"EHLO asmtp.htwg-konstanz.de\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Starting TLS...")
    s.send(b"STARTTLS\r\n")
    response = s.recv(1024).decode("utf-8")
    print(response)
    
    if not response.startswith("220"):
        raise Exception("Server doesn't support STARTTLS")
    
    print_info("Socket ready for TLS upgrade.")
    return s

def send_email(
    s: socket.socket,
    username: str,
    password: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """
    Sends an email using the given socket.
    Args:
        s (socket.socket): The socket object used for communication.
        username (str): The username used to authenticate with the SMTP server.
        password (str): The password used to authenticate with the SMTP server.
        sender (str): The email address of the sender.
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The body of the email.
    Returns:
        None
    """
    # Nach TLS-Upgrade erneut EHLO senden
    print_info("Sending EHLO after TLS...")
    s.send(b"EHLO asmtp.htwg-konstanz.de\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Starting authentication...")
    s.send(b"AUTH LOGIN\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending username...")
    s.send(base64.b64encode(username.encode("utf-8")) + b"\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending password...")
    s.send(base64.b64encode(password.encode("utf-8")) + b"\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending mail from...")
    s.send(f"MAIL FROM:<{sender}>\r\n".encode("utf-8"))
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending rcpt to...")
    s.send(f"RCPT TO:<{recipient}>\r\n".encode("utf-8"))
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Sending data...")
    s.send(b"DATA\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    # Email-Header und Body
    message = f"""From: {sender}
To: {recipient}
Subject: {subject}
Date: {time.strftime("%a, %d %b %Y %H:%M:%S %z")}

{body}
.""".replace('\n', '\r\n')

    s.send(message.encode("utf-8") + b"\r\n")
    print(s.recv(1024).decode("utf-8"))
    
    print_info("Quitting...")
    s.send(b"QUIT\r\n")
    print(s.recv(1024).decode("utf-8"))

def parse_arguments():
    """
    Parse command line arguments
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Send email via SMTP with authentication')
    parser.add_argument('-u', '--username', required=True, help='SMTP username')
    parser.add_argument('-p', '--password', required=True, help='SMTP password')
    parser.add_argument('-s', '--src', required=True, help='source email')
    parser.add_argument('-d', '--dst', required=True, help='dest email')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    sock = build_connection()
    print_info("Wrapping socket...")
    context = ssl.create_default_context()
    try:
        ssl_socket = context.wrap_socket(
            sock,
            server_hostname="asmtp.htwg-konstanz.de",
            do_handshake_on_connect=True,
        )
        print_info("Socket wrapped.")
        send_email(
            ssl_socket,
            args.username, # username
            args.password, # password
            args.src, # src email
            args.dst, # dst email
            "Test",
            "This is a test email.",
        )
    except ssl.SSLError as e:
        print_info("\nSSL Error:\t", end="")
        print(f"{e}")
        print(f"Error number:\t{e.errno}")
        print(f"Error library:\t{e.library}")
        print(f"Error reason:\t{e.reason}")
    finally:
        sock.close()
