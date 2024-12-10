
# Run8 Port Mirroring Application (Run8PM)

## Overview

The **Run8 Port Mirroring Application** is a Python-based utility designed to mirror UDP packets from the Simulator Run 8. This tool enables multiple sub-applications to work with the mirrored traffic simultaneously. With debugging options and message translation capabilities, it can be used for monitoring and troubleshooting.

## Features

- **UDP Port Mirroring**: Mirrors UDP packets from a source port to multiple target ports.
- **Bidirectional Communication**: Supports two-way communication between the source and mirrors.
- **Debug Levels**:
  - `NONE`: Disables debug messages.
  - `MIRROR`: Displays messages related to traffic from mirrors.
  - `SOURCE`: Displays messages related to traffic from the source.
  - `ALL`: Combines `MIRROR` and `SOURCE` debug messages.
  - `TRANSLATOR`: Decodes and displays UDP packet contents in a human-readable format.
- **Message Translation**: Converts raw UDP packet data into structured details, including headers, message types, values, and CRC.

## Requirements

- Python 3.8 or higher
- Standard Python libraries (`asyncio`, `socket`, `enum`)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository_url>
   ```

2. Navigate to the project directory:
   ```bash
   cd Run8PM
   ```

3. (Optional) Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

## Usage

### Running the Application

1. Open `Run8PM.py` and configure the following parameters:
   - **Source Address and Port**: Set the address and port of the UDP source.
   - **Mirror Ports**: Define a list of UDP ports for mirroring.
   - **Debug Level**: Set the desired debug and translation flags using the `DebugLevel` enum.

   Example configuration:
   ```python
   source_address = "127.0.0.1"
   source_port = 18888
   mirror_ports = [18890, 18895]
   debug_level = DebugLevel.MIRROR | DebugLevel.TRANSLATOR
   ```

2. Run the application:
   ```bash
   python Run8PM.py
   ```

### Debug Levels

- **MIRROR**: Monitors traffic from mirrors to the source.
- **SOURCE**: Monitors traffic from the source to mirrors.
- **ALL**: Combines `MIRROR` and `SOURCE` debug messages.
- **TRANSLATOR**: Decodes and displays detailed message content.

### Example Debug Output

Sample debug output with `DebugLevel.TRANSLATOR` enabled:
```
[DEBUG] Received 5 bytes from ('127.0.0.1', 18888) on source response port 18889
[TRANSLATED] Header: 224, Message Type: 1, Value: 1, CRC: 226
```

## Example Test Script: `TestRun8.py`

A test script, `TestRun8.py`, is included to simulate UDP messages being sent to the Run8 simulator. It demonstrates:
- Sending control messages such as:
  - Alerter button pressed/released
  - Horn button pressed/released
  - Dynamic brake lever adjustments

Run the test script:
```bash
python TestRun8.py
```

### Example Messages Sent by Test Script

- **Alerter Button Pressed**:
  ```
  Header: 224, Message Type: 1, Value: 1, CRC: <calculated CRC>
  ```

- **Horn Button Released**:
  ```
  Header: 224, Message Type: 8, Value: 0, CRC: <calculated CRC>
  ```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

