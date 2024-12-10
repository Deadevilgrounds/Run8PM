import socket
import time


def calculate_crc(message):
    """Calculate the CRC byte for the message."""
    crc = message[0]
    for byte in message[1:-1]:
        crc ^= byte
    return crc


def create_message(header, message_type, data):
    """
    Create a 5-byte message with the correct CRC.

    :param header: Header byte (96 or 224 for audio flag).
    :param message_type: Ushort message type (2 bytes).
    :param data: Data byte for the control.
    :return: A 5-byte message as a byte array.
    """
    message = bytearray(5)
    message[0] = header
    message[1] = (message_type >> 8) & 0xFF  # High byte of message type
    message[2] = message_type & 0xFF  # Low byte of message type
    message[3] = data  # Data byte
    message[4] = calculate_crc(message)  # CRC byte
    return message


def send_message(message, port=18888):
    """
    Send the message to the specified port.

    :param message: Message to send (byte array).
    :param port: Target UDP port (default 18888).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.sendto(message, ('127.0.0.1', port))
        print(f"Sent: {list(message)} to port {port}")


# Example Usage
if __name__ == "__main__":
    # Configuration
    header = 224  # 96 for no audio, 224 for audio
    port = 18888

    # Test 1: Alerter button pressed
    message_type = 1  # Alerter
    data = 1  # Button pressed
    message = create_message(header, message_type, data)
    send_message(message, port)

    time.sleep(1)

    message_type = 1  # Alerter
    data = 0  # Button pressed
    message = create_message(header, message_type, data)
    send_message(message, port)

    # Test 2: Horn button pressed
    message_type = 8  # Horn
    data = 1  # Button pressed
    message = create_message(header, message_type, data)
    send_message(message, port)

    time.sleep(1)

    message_type = 8  # Horn
    data = 0  # Button pressed
    message = create_message(header, message_type, data)
    send_message(message, port)

    # Test 3: Dynamic brake lever to 50%
    message_type = 4  # Dynamic Brake Lever
    data = 0  # 50% (value between 0-255)
    message = create_message(header, message_type, data)
    send_message(message, port)
