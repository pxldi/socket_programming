# Rechnernetze WS24/25 Laboraufgabe: Socketprogrammierung

## 3 Rechen-Server und Client
Implementiert in `server.py` und `client.py`.

### 3.1 Lokale Kommunikation mit WireShark
|Time     |Source Port|Destination Port|Info      |Script|Befehl   |blockierender Befehl|
|:--------|:------|:-------|:---------|:-----|:--------|:-------------------|
|4.141010 |63671  |12345   |[SYN]     |Client|`connect`|`accept`            |
|4.141019 |12345  |63671   |[SYN, ACK]|Server|`accept` |`connect`           |
|4.141056 |63671  |12345   |[ACK]     |Client|         |                    |
|4.141078 |63671  |12345   |[PSH, ACK]|Client|`send`   |`recv`              |
|4.141085 |12345  |63671   |[ACK]     |Server|         |                    |
|4.141092 |63671  |12345   |[PSH, ACK]|Client|`send`   |`recv`              |
|4.141095 |12345  |63671   |[ACK]     |Server|         |                    |
|4.141488 |12345  |63671   |[PSH, ACK]|Server|`send`   |`recv`              |
|4.141501 |63671  |12345   |[ACK]     |Client|         |                    |
|4.141510 |12345  |63671   |[PSH, ACK]|Server|`send`   |`recv`              |
|4.141517 |63671  |12345   |[ACK]     |Client|         |                    |
|4.141528 |12345  |63671   |[FIN, ACK]|Server|`close`  |                    |
|4.141533 |63671  |12345   |[ACK]     |Client|         |                    |
|4.141544 |63671  |12345   |[FIN, ACK]|Client|`close`  |                    |
|4.141568 |12345  |63671   |[ACK]     |Server|         |                    |

### 3.2 Netzwerk-Kommunikation

#### 3.2.1 Wie können Sie im Client Python-Skript die IP-Adresse und Port-Nummer des verwendeten 
lokalen Sockets bestimmen („bestimmen“ im Sinne von herausfinden)?

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 12345))
local_ip, local_port = sock.getsockname()
```

#### 3.2.2. Wann (in welcher Code-Zeile) und woher erhält ein Client seine IP-Adresse und Port-Nummer?

Bei `socket.connect()` wird automatisch ein zufälliger freier Port vom Betriebssystem zugewiesen.

#### 3.2.3. Wie können Sie im Client-Skript die IP-Adresse und Port-Nummer des Sockets setzen?

Explizites Setzen von IP und Port im Client:

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('192.168.1.99', 30000))
sock.connect(('127.0.0.1', 12345))
```

#### 3.2.4. Warum müssen Sie Timeouts verwenden und wie funktioniert try ... except? Mit welchem Befehl können Sie einen gemeinsamen Timeout für alle Sockets setzen?

Timeouts sind wichtig weil:
- sie verhindern, dass das Programm endlos hängt
- sie ermöglichen die Behandlung von Netzwerkproblemen

Globalen Timeout für alle Sockets setzen:
```python
socket.setdefaulttimeout(30)  # 30 Sekunden
```

#### 3.2.5. Finden Sie experimentell heraus, ob Sie einen Server betreiben können, der ECHO-Anfragen auf dem gleichen Port für UDP und TCP beantwortet?

Ja, es ist möglich TCP und UDP auf dem gleichen Port zu verwenden, da es separate Protokolle sind. 
Wichtig ist die Verwendung von `SO_REUSEADDR`.

### 3.3 Multithreaded Server

Funktion listen() implementiert in `start_tcp_server()` in `server.py`, `receive()` implementiert in `handle_tcp_client()`.

## 4 Port Scan

### 4.2 TCP und UDP Port Scanner

Implementiert in `scan.py`.

#### 4.3.1 Offene Ports

Offene TCP Ports für 141.37.168.26: [7, 9, 13, 17, 19]

Offene UDP Ports für 141.37.168.26: [7, 13, 17]

#### 4.3.2 Paketsequenzen

Client sendet SYN
Server antwortet mit SYN-ACK
Client sendet ACK
Verbindung etabliert

TCP geschlossen (z.B. Port 8):

Client sendet SYN
Server antwortet mit RST-ACK
Verbindungsaufbau abgebrochen

UDP offen (Port 7):

Client sendet UDP-Datagramm
Server antwortet mit UDP-Datagramm

UDP geschlossen (die meisten anderen Ports):

Client sendet UDP-Datagramm
Keine Antwort (Timeout)

#### 4.3.3 ECHO-Dienst

=== TCP ECHO Test ===
Verbindungsaufbau zu 141.37.168.26:7 (TCP)...
Verbindung hergestellt!
Sende Nachricht: Hello ECHO Server!
Empfangene Antwort: Hello ECHO Server!

=== UDP ECHO Test ===
Sende Nachricht an 141.37.168.26:7 (UDP): Hello ECHO Server!
Empfangene Antwort von ('141.37.168.26', 7): Hello ECHO Server!

## 5 Mail

### 5.2 SMTP

Implementiert in `smtp.py`.

Resultierende Email:

![alt text](image.png)