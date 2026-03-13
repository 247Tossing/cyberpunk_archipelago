"""
Cyberpunk 2077 TCP Test Server

This is a standalone test server for testing the RedScript TCP client
without needing the full Archipelago infrastructure.

A mock Archipelago server for protocol testing.
- Runs on localhost:51234 (same port as real server)
- Returns hardcoded test data for all commands
- Perfect for testing the RedScript TCP client implementation

Usage (from Archipelago root directory):
    python worlds/cyberpunk2077/test_server.py

Then connect from RedScript to localhost:51234
"""

import asyncio
import logging
import sys
import os
from typing import Optional, Dict, List

# Add Archipelago root to sys.path so we can import BaseClasses and worlds
# This is needed because test_server.py is often run as a standalone script
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from worlds.cyberpunk2077.locations import LocationData
from worlds.cyberpunk2077 import item_table
from worlds.cyberpunk2077 import location_table

# Set up colored logging (optional, fallback to plain if colorama not available)
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        GREEN = YELLOW = RED = CYAN = MAGENTA = BLUE = ""
    class Style:
        RESET_ALL = BRIGHT = ""

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("CyberpunkTestServer")

# Server configuration
SERVER_VERSION = "0.1.1"
MIN_CLIENT_VERSION = "0.1.0"
PORT = 51234

# Test data loading logic
# Initialize with fallbacks
TEST_ITEMS = item_table.keys()
TEST_ITEM_IDS = item_table.values()
TEST_LOCATIONS = location_table  # name -> id
DATA_LOADED = False

try:
    # noinspection PyUnusedImports
    from worlds.cyberpunk2077.items import item_name_to_id
    # noinspection PyUnusedImports
    from worlds.cyberpunk2077.locations import location_name_to_id
except ImportError:
    # Fallback: Keep using hardcoded data when world files not found
    pass
else:
    # Only update test data if imports succeeded and contain valid data
    if item_name_to_id:
        TEST_ITEMS = list(item_name_to_id.keys())
        TEST_ITEM_IDS = list(item_name_to_id.values())
    if location_name_to_id:
        TEST_LOCATIONS = location_name_to_id
    DATA_LOADED = True

# Simulated state
class ServerState:
    """
    Simulated server state for testing

    
    - Like a GameState singleton
    - Tracks connection status and received commands
    """
    def __init__(self):
        self.client_connected = False
        self.client_version = None
        self.archipelago_connected = False
        self.commands_received = []
        self.game_client_writer = None  # Reference to connected client

state = ServerState()


def check_version_compatibility(client_version: str) -> bool:
    """
    Check if client version is compatible

    
    - Simple version string comparison
    - Parses semantic versioning (major.minor.patch)
    """
    try:
        client_parts = [int(x) for x in client_version.split('.')]
        min_parts = [int(x) for x in MIN_CLIENT_VERSION.split('.')]

        # Pad to same length
        while len(client_parts) < len(min_parts):
            client_parts.append(0)
        while len(min_parts) < len(client_parts):
            min_parts.append(0)

        return client_parts >= min_parts
    except Exception:
        return False


async def process_command(command: str) -> str:
    """
    Process a command from the RedScript client

    Command dispatcher that routes commands to appropriate handlers.
Returns mock responses for testing.

    Args:
        command: Command string from RedScript

    Returns:
        Response string to send back
    """
    # Log received command
    if HAS_COLOR:
        logger.info(f"{Fore.CYAN}← RX: {Style.BRIGHT}{command}{Style.RESET_ALL}")
    else:
        logger.info(f"← RX: {command}")

    state.commands_received.append(command)

    # Parse command
    parts = command.split(':')
    cmd = parts[0].upper() if parts else ""

    response = None

    try:
        # ===== HELLO =====
        if cmd == "HELLO":
            if len(parts) != 2:
                response = "FAIL:Invalid HELLO format. Expected: HELLO:<client_version>"
            else:
                client_version = parts[1]
                state.client_version = client_version

                is_compatible = check_version_compatibility(client_version)

                if is_compatible:
                    logger.info(f"✓ Client version {client_version} is compatible")
                    response = f"HELLO:{SERVER_VERSION}:OK"
                else:
                    logger.warning(f"✗ Client version {client_version} is incompatible")
                    response = f"HELLO:{SERVER_VERSION}:FAIL"

        # ===== CONNECT_REQ =====
        elif cmd == "CONNECT_REQ":
            # Simple handshake - game is checking if server is ready
            logger.info("✓ Game sent CONNECT_REQ handshake")
            response = "CONNECT_REQ:OK"

        # ===== SYNC_ITEMS =====
        elif cmd == "SYNC_ITEMS":
            if not state.archipelago_connected:
                response = "SYNC_ITEMS:FAIL:Not connected to Archipelago server"
            else:
                # Return test items by NAME (not IDs)
                item_list = ','.join(TEST_ITEMS)
                response = f"SYNC_ITEMS:ITEMS:{item_list}"
                logger.info(f"Returning {len(TEST_ITEMS)} test items")

        # ===== OK_READY =====
        elif cmd == "OK_READY":
            logger.info("✓ Client confirmed ready")
            response = "OK_READY:OK"

        # ===== CHECK =====
        elif cmd == "CHECK":
            if len(parts) != 2:
                response = "CHECK:FAIL:Invalid CHECK format. Expected: CHECK:<location_name>"
            else:
                location_name = parts[1]
                if DATA_LOADED:
                    if location_name in TEST_LOCATIONS:
                        location_id = TEST_LOCATIONS[location_name]
                        logger.info(f"✓ Location checked: {location_name} (ID: {location_id})")
                    else:
                        logger.warning(f"⚠ Unknown location checked: {location_name}")
                else:
                    logger.info(f"Location checked: {location_name}")
                response = "CHECK:OK"

        # ===== CHECK_REQ =====
        elif cmd == "CHECK_REQ":
            if len(parts) != 2:
                response = "CHECK_REQ:FAIL:Invalid CHECK_REQ format"
            else:
                item_id = int(parts[1])
                # Return TRUE if it's one of our test items
                has_item = item_id in TEST_ITEM_IDS
                result = "TRUE" if has_item else "FALSE"
                response = f"CHECK_REQ:{result}"
                logger.info(f"Item check {item_id}: {result}")

        # ===== GET_SLOT_DATA =====
        elif cmd == "GET_SLOT_DATA":
            if len(parts) != 2:
                response = "GET_SLOT_DATA:FAIL:Invalid GET_SLOT_DATA format"
            else:
                key = parts[1]
                # Return mock slot data
                mock_data = {
                    "starting_district": "Watson",
                    "gig_count": "50",
                    "difficulty": "Normal"
                }

                if key in mock_data:
                    response = f"GET_SLOT_DATA:VALUE:{mock_data[key]}"
                    logger.info(f"Slot data '{key}' = '{mock_data[key]}'")
                else:
                    response = f"GET_SLOT_DATA:FAIL:Key not found: {key}"

        # ===== STATUS =====
        elif cmd == "STATUS":
            if len(parts) >= 2:
                district = parts[1]
                logger.info(f"Player status update: {district}")
            response = "STATUS:OK"

        # ===== VICTORY =====
        elif cmd == "VICTORY":
            logger.info("🎉 Player completed the game!")
            response = "VICTORY:OK"

        # ===== DEATHLINK_SEND =====
        elif cmd == "DEATHLINK_SEND":
            logger.info("💀 Player died in Cyberpunk (sending DeathLink to others)")
            response = "DEATHLINK_SEND:OK"

        # ===== DISCONNECT =====
        elif cmd == "DISCONNECT":
            logger.info("Client requesting disconnect")
            response = "DISCONNECT:OK"

        # ===== UNKNOWN =====
        else:
            response = f"FAIL:Unknown command: {cmd}"
            logger.warning(f"Unknown command received: {cmd}")

    except Exception as e:
        response = f"FAIL:Error processing command: {str(e)}"
        logger.error(f"Error processing command: {e}")

    # Log response
    if response:
        if HAS_COLOR:
            color = Fore.GREEN if not response.startswith("FAIL") else Fore.RED
            logger.info(f"{color}→ TX: {Style.BRIGHT}{response}{Style.RESET_ALL}")
        else:
            logger.info(f"→ TX: {response}")

    return response


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """
    Handle a connected client

    
    - Called when RedScript connects
    - Runs in a loop processing commands
    - Like a NetworkStream message pump
    """
    addr = writer.get_extra_info('peername')

    if HAS_COLOR:
        logger.info(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}✓ RedScript client connected from {addr}{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    else:
        logger.info("="*60)
        logger.info(f"✓ RedScript client connected from {addr}")
        logger.info("="*60)

    state.client_connected = True
    state.game_client_writer = writer  # Store writer for sending commands

    try:
        while True:
            # Read a line (command) from the client
            line = await reader.readline()

            if not line:
                # Connection closed
                logger.info("Client closed connection (empty readline)")
                break

            # Decode and strip whitespace
            command = line.decode('utf-8').strip()

            if not command:
                logger.debug("Received empty command, skipping")
                continue

            # Process the command
            response = await process_command(command)

            # Send response - ALWAYS send something back
            if not response:
                response = "FAIL:No response generated"
                logger.error("Command processing returned None - this should never happen!")

            # RedScript needs \r\n line ending (CRLF)
            if not response.endswith('\r\n'):
                # Remove any existing line ending and add \r\n
                response = response.rstrip('\r\n') + '\r\n'

            try:
                writer.write(response.encode('utf-8'))
                await writer.drain()
                logger.debug(f"Response sent and flushed successfully")
            except Exception as write_error:
                logger.error(f"Failed to send response: {write_error}")
                break

    except asyncio.CancelledError:
        logger.info("Client handler cancelled")
    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        state.client_connected = False
        state.game_client_writer = None
        writer.close()
        await writer.wait_closed()

        if HAS_COLOR:
            logger.info(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}✗ RedScript client disconnected{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        else:
            logger.info("="*60)
            logger.info("✗ RedScript client disconnected")
            logger.info("="*60)


async def send_to_client(message: str) -> Optional[str]:
    """
    Send a message to the connected client and wait for response

    Sends a server-initiated command to RedScript.
Waits for and returns the response.
    """
    if not state.client_connected or not state.game_client_writer:
        print("✗ No client connected!")
        return None

    try:
        # Add CRLF if not present
        if not message.endswith('\r\n'):
            message = message.rstrip('\r\n\n') + '\r\n'

        # Send message
        state.game_client_writer.write(message.encode('utf-8'))
        await state.game_client_writer.drain()

        if HAS_COLOR:
            print(f"{Fore.MAGENTA}→ Sent to client: {Style.BRIGHT}{message.strip()}{Style.RESET_ALL}")
        else:
            print(f"→ Sent to client: {message.strip()}")

        # Read response (with timeout)
        # Note: This is a simplified version - in production you'd need a proper response queue
        await asyncio.sleep(0.1)  # Give client time to respond

        return "Waiting for response..."

    except Exception as e:
        print(f"✗ Error sending to client: {e}")
        return None


async def console_input_handler():
    """
    Handle console input for sending commands to RedScript client

    
    - Runs in background
    - Reads from stdin
    - Sends commands to connected client
    """
    print("\n" + "="*70)
    print("Interactive Console Commands:")
    print("="*70)
    print("  send <command>         - Send command to RedScript client")
    print("  item <name> <sender>   - Send ITEM_RECEIVED:<name>:<sender>")
    print("  death                  - Send DEATHLINK_RECEIVED (kill player)")
    print("  status                 - Show connection status")
    print("  help                   - Show this help")
    print("  quit                   - Stop server")
    print("="*70 + "\n")

    loop = asyncio.get_event_loop()

    while True:
        try:
            # Read input from stdin asynchronously
            line = await loop.run_in_executor(None, input, "> ")

            if not line.strip():
                continue

            parts = line.strip().split(maxsplit=1)
            command = parts[0].lower()

            if command == "quit":
                print("Stopping server...")
                sys.exit(0)

            elif command == "help":
                print("\nCommands:")
                print("  send <command>         - Send command to RedScript")
                print("  item <name> <sender>   - Send ITEM_RECEIVED:<name>:<sender>")
                print("  death                  - Send DEATHLINK_RECEIVED (kill player)")
                print("  status                 - Show connection status")
                print("  help                   - Show this help")
                print("  quit                   - Stop server\n")

            elif command == "status":
                print(f"\nConnection Status:")
                print(f"  Client Connected: {state.client_connected}")
                print(f"  Archipelago Connected: {state.archipelago_connected}")
                print(f"  Client Version: {state.client_version or 'N/A'}")
                print(f"  Commands Received: {len(state.commands_received)}\n")

            elif command == "send":
                if len(parts) < 2:
                    print("Usage: send <command>")
                    continue

                cmd = parts[1]
                await send_to_client(cmd)

            elif command == "item":
                if len(parts) < 2:
                    print("Usage: item <name> <sender>")
                    print("Example: item Mantis Blades Player2")
                    continue

                # Parse item name and sender
                item_parts = parts[1].split(maxsplit=1)
                if len(item_parts) < 2:
                    print("Usage: item <name> <sender>")
                    continue

                # Split on last space to get sender
                args = parts[1].rsplit(maxsplit=1)
                if len(args) == 2:
                    item_name, sender = args
                    cmd = f"ITEM_RECEIVED:{item_name}:{sender}"
                    await send_to_client(cmd)
                else:
                    print("Usage: item <name> <sender>")

            elif command == "death":
                cmd = "DEATHLINK_RECEIVED"
                await send_to_client(cmd)

            else:
                print(f"Unknown command: {command}. Type 'help' for commands.")

        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nStopping server...")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """
    Main entry point

    
    - Starts the TCP server
    - Waits for connections
    - Runs until Ctrl+C
    """
    # Start server
    server = await asyncio.start_server(
        handle_client,
        'localhost',
        PORT
    )

    # Print startup banner
    if HAS_COLOR:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}  Cyberpunk 2077 TCP Test Server{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  Status:     {Style.BRIGHT}READY{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  Listening:  {Style.BRIGHT}localhost:{PORT}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  Version:    {Style.BRIGHT}{SERVER_VERSION}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}  Waiting for RedScript client connection...{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}  Press Ctrl+C to stop the server{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*70}{Style.RESET_ALL}\n")
    else:
        print("\n" + "="*70)
        print("  Cyberpunk 2077 TCP Test Server")
        print("="*70)
        print(f"  Status:     READY")
        print(f"  Listening:  localhost:{PORT}")
        print(f"  Version:    {SERVER_VERSION}")
        print("="*70)
        print("  Waiting for RedScript client connection...")
        print("  Press Ctrl+C to stop the server")
        print("="*70 + "\n")

    logger.info("Test server started successfully")
    if DATA_LOADED:
        logger.info(f"✓ Real data loaded: {len(TEST_ITEMS)} items, {len(TEST_LOCATIONS)} locations")
    else:
        logger.info(f"⚠ Using fallback test data: {len(TEST_ITEMS)} items")

    # Start console input handler in background
    console_task = asyncio.create_task(console_input_handler())

    # Run until interrupted
    async with server:
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            logger.info("Server shutting down...")
            console_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if HAS_COLOR:
            print(f"\n{Fore.YELLOW}Server stopped by user (Ctrl+C){Style.RESET_ALL}")
        else:
            print("\nServer stopped by user (Ctrl+C)")
        sys.exit(0)
