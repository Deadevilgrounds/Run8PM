import asyncio
import socket
from enum import IntFlag

class DebugLevel(IntFlag):
    NONE = 0
    ALL = 3
    MIRROR = 1
    SOURCE = 2
    TRANSLATOR = 4

class UDPPortMirror:
    def __init__(self, source_address: str, source_port: int, mirror_ports: list[int], debug_level: DebugLevel = DebugLevel.NONE):
        """
        Initialize the UDPPortMirror.

        :param source_address: Address of the source UDP stream (e.g., '127.0.0.1').
        :param source_port: Port of the source stream (e.g., 18888).
        :param mirror_ports: List of ports to listen on and their respective response ports.
        :param debug_level: Debug level using DebugLevel flags.
        """
        self.source_address = source_address
        self.source_port = source_port
        self.mirror_ports = mirror_ports
        self.debug_level = debug_level

    async def start(self):
        """Start the UDP port mirror."""
        loop = asyncio.get_running_loop()

        # Hook into the source response port (18889)
        source_response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        source_response_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        source_response_socket.bind((self.source_address, self.source_port + 1))

        # Create and own mirror sockets
        mirror_sockets = []
        for port in self.mirror_ports:
            mirror_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            mirror_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            mirror_socket.bind((self.source_address, port))
            mirror_sockets.append(mirror_socket)

        handler = self.UDPHandler(self.source_port + 1, self.mirror_ports, self.debug_level)

        # Add sockets to the event loop
        loop.create_task(self.listen_on_source_response(source_response_socket, handler))
        for port, sock in zip(self.mirror_ports, mirror_sockets):
            loop.create_task(self.listen_on_mirror(sock, port, handler))

        print(f"Hooked into source response port {self.source_port + 1}")
        print(f"Listening on mirror ports: {', '.join(map(str, self.mirror_ports))}")

        try:
            print("Starting UDP port mirror loop")
            await asyncio.Future()  # Run forever
        finally:
            print("Stopping UDP port mirror loop")
            source_response_socket.close()
            for sock in mirror_sockets:
                sock.close()

    async def listen_on_source_response(self, source_response_socket, handler):
        """Listen for incoming messages on the source response port."""
        while True:
            data, addr = await asyncio.get_event_loop().run_in_executor(None, source_response_socket.recvfrom, 65535)
            if self.debug_level & DebugLevel.SOURCE:
                print(f"[DEBUG] Received {len(data)} bytes from {addr} on source response port {self.source_port + 1}")
                if DebugLevel.TRANSLATOR:
                    print(f"[TRANSLATED] {self.translate_message(data)}")
            for port in self.mirror_ports:
                handler.send_to(data, ('127.0.0.1', port + 1))  # Forward to mirror response ports

    async def listen_on_mirror(self, mirror_socket, mirror_port, handler):
        """Listen for incoming messages on a mirror port."""
        while True:
            data, addr = await asyncio.get_event_loop().run_in_executor(None, mirror_socket.recvfrom, 65535)
            if self.debug_level & DebugLevel.MIRROR:
                print(f"[DEBUG] Received {len(data)} bytes from {addr} on mirror port {mirror_port}")
                if DebugLevel.TRANSLATOR:
                    print(f"[TRANSLATED] {self.translate_message(data)}")
            handler.send_to(data, ('127.0.0.1', self.source_port))  # Forward to source port

    @staticmethod
    def translate_message(data):
        """Translate a message into a human-readable format."""
        try:
            header = data[0]
            message_type = (data[1] << 8) + data[2]
            value = data[3]
            crc = data[4]
            return (
                f"Header: {header}, Message Type: {message_type}, "
                f"Value: {value}, CRC: {crc}"
            )
        except IndexError:
            return "Invalid or incomplete message"

    class UDPHandler:
        def __init__(self, source_port: int, mirror_ports: list[int], debug_level: DebugLevel):
            """Initialize the UDP handler."""
            self.source_port = source_port
            self.mirror_ports = mirror_ports
            self.debug_level = debug_level

        def send_to(self, data, target):
            """Send data to the specified target."""
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data, target)
            sock.close()

if __name__ == "__main__":
    source_address = "127.0.0.1"
    source_port = 18888
    mirror_ports = [18890, 18895]  # Listening ports for mirrors

    # Set debug level to DebugLevel.MIRROR to monitor mirror to Run8 messages only
    # Set debug level to DebugLevel.SOURCE to monitor Run8 to mirror messages only
    # Set debug level to DebugLevel.ALL to enable all debug messages
    # Set debug level to DebugLevel.TRANSLATOR to translate the message bytes. Must be used with one of the above
    debug_level = DebugLevel.MIRROR | DebugLevel.TRANSLATOR

    mirror = UDPPortMirror(source_address, source_port, mirror_ports, debug_level=debug_level)

    asyncio.run(mirror.start())
