"""
Cyberpunk 2077 Archipelago Client

This file implements the TCP server that communicates with the Cyberpunk 2077 RedScript mod.
It acts as a bridge between the Archipelago server and the game.

Architecture:
- Connects to the Archipelago multiworld server via websocket
- Runs a TCP server on localhost:51234 for the game to connect to
- Handles bidirectional communication between game and server
- Uses Python's asyncio for concurrent network operations

PROTOCOL: Simple Text-Based Commands (No JSON needed!)
========================================================
All commands are newline-terminated strings (ending with \n)
Commands use : as a delimiter for parameters
RedScript only needs simple string parsing - no JSON library required!
"""

import asyncio
import logging
import typing
from typing import Dict, List, Any, Optional, Set

# CommonClient imports
from CommonClient import (
    CommonContext,
    server_loop,
    gui_enabled,
    ClientCommandProcessor,
    logger,
    get_base_parser
)
from NetUtils import ClientStatus, NetworkItem
from Utils import async_start
import Utils

# Import item and location lookup functions
# Bidirectional lookup helpers for translating between names and IDs
from worlds.cyberpunk2077.items import get_item_name_by_id, get_item_id_by_name, item_id_to_name, item_name_to_id
from worlds.cyberpunk2077.locations import get_location_id_by_name, get_location_name_by_id


# ===== VERSION INFORMATION =====
# Version constants for client/server compatibility checking
SERVER_VERSION = "0.0.1"  # Python server version
MIN_CLIENT_VERSION = "0.0.1"  # Minimum required RedScript client version


class CyberpunkClientCommandProcessor(ClientCommandProcessor):
    """
    Handles text commands typed by the user in the client UI

    Handles text commands typed by the user in the client UI.
    Methods starting with _cmd_ are automatically registered as commands.
    Users can type /command_name in the client to execute them.
    """

    ctx: "CyberpunkContext"

    def _cmd_cyberpunk(self) -> None:
        """
        Display Cyberpunk 2077 connection status
        Usage: /cyberpunk
        """
        if isinstance(self.ctx, CyberpunkContext):
            if self.ctx.game_connected:
                self.output("Cyberpunk 2077 game is CONNECTED.")
                self.output(f"Items received: {len(self.ctx.items_received)}")
                self.output(f"Locations checked: {len(self.ctx.checked_locations)}")
            else:
                self.output("Cyberpunk 2077 game is NOT CONNECTED.")
                self.output(f"Waiting on port {self.ctx.game_server_port}...")
        else:
            self.output("Not connected to a Cyberpunk 2077 session.")


class CyberpunkContext(CommonContext):
    """
    Main context class that manages the connection state
    """

    # Class attributes
    game = "Cyberpunk 2077"  # Must match the game name in __init__.py
    command_processor = CyberpunkClientCommandProcessor

    # Items handling flags (bitwise)
    # 0b111 = 7 = receive all items
    items_handling = 0b111


    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        """
        Initialize the context
        """
        super().__init__(server_address, password)

        # TCP server for RedScript client
        self.game_server: Optional[asyncio.Server] = None
        self.game_client_writer: Optional[asyncio.StreamWriter] = None
        self.game_client_reader: Optional[asyncio.StreamReader] = None
        self.game_connected: bool = False

        # Port for the TCP server (RedScript connects to this)
        self.game_server_port: int = 51234

        # Archipelago connection state
        self.archipelago_connected: bool = False
        self.slot_data: Dict[str, Any] = {}

        # Item tracking
        # Track items received from the Archipelago server
        self.received_item_ids: List[int] = []

        # Track which items we've sent to the game
        # Prevents duplicate sends
        self.items_sent_to_game: Set[int] = set()


    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.

        Standard Archipelago flow - no custom blocking logic.
        The TCP server runs independently and accepts game connections at any time.
        """
        # Standard Archipelago authentication - no game wait
        if password_requested and not self.password:
            await super().server_auth(password_requested)

        await self.get_username()
        await self.send_connect()


    async def connection_closed(self) -> None:
        """
        Called when connection to Archipelago server is closed
        """
        self.archipelago_connected = False
        await super().connection_closed()
        print("Connection to Archipelago server closed.")


    def on_package(self, cmd: str, args: Dict[str, Any]) -> None:
        """
        Handle packets received from the Archipelago server

        """
        if cmd == "Connected":
            # Successfully connected to Archipelago server
            self.archipelago_connected = True
            #logger.info("✓ Connected to Archipelago server!")
            #logger.info(f"Slot: {self.auth}")
            # Get slot data (custom world generation data)
            self.slot_data = args.get("slot_data", {})
            #logger.info(f"Slot data: {self.slot_data}")

            # Inform user about game connection
            if self.game_connected:
                # Game already connected - sync immediately
                logger.info("Syncing items and configuration with game...")
                async_start(self.send_to_game("CONNECTED"))
            else:
                # Game not connected yet - this is normal, just inform user
                logger.info("")
                logger.info("═════════════════════════════════════════════════════════════")
                logger.info("  Please connect Cyberpunk 2077 to the client:")
                logger.info("    1. Launch Cyberpunk 2077")
                logger.info("    2. Open CET overlay")
                logger.info("    3. Navigate to 'Archipelago Client'")
                logger.info(f"    4. Connect to localhost:{self.game_server_port}")
                logger.info("═════════════════════════════════════════════════════════════")


        elif cmd == "ReceivedItems":
            # Server sent us items
            start_index = args["index"]
            items: List[NetworkItem] = args["items"]

            print(f"Received {len(items)} items from Archipelago")

            # Add items to our received list
            for item in items:
                if item.item not in self.received_item_ids:
                    self.received_item_ids.append(item.item)

            # Send new items to the game if connected
            if self.game_connected:
                async_start(self.send_new_items_to_game())

        elif cmd == "RoomInfo":
            # Initial room information
            pass


    async def send_new_items_to_game(self) -> None:
        """
        Send any items we haven't sent to the game yet
        """
        if not self.game_connected:
            return

        # Find items we haven't sent yet
        new_items = [
            item_id for item_id in self.received_item_ids
            if item_id not in self.items_sent_to_game
        ]

        # Send each new item
        for item_id in new_items:
            # Get item name using our lookup function
            item_name = get_item_name_by_id(item_id)
            if not item_name:
                # Fallback for unknown items
                item_name = self.item_names.get(item_id, f"Unknown Item {item_id}")
                logger.warning(f"Unknown item ID: {item_id}")

            # Find who sent it (if available)
            sender = "Unknown"
            for network_item in self.items_received:
                if network_item.item == item_id:
                    sender = self.player_names.get(network_item.player, f"Player {network_item.player}")
                    break

            # Send to game: ITEM_RECEIVED:<name>:<sender>
            # RedScript receives the item name and sender, must respond with OK/FAIL
            response = await self.send_to_game(f"ITEM_RECEIVED:{item_name}:{sender}")

            if response and response.startswith("ITEM_RECEIVED:OK"):
                # Game acknowledged, mark as sent
                self.items_sent_to_game.add(item_id)
                logger.info(f"✓ Sent item to game: {item_name} (from {sender})")
            elif response and response.startswith("ITEM_RECEIVED:FAIL"):
                logger.error(f"✗ Game failed to receive item: {item_name} - {response}")
            else:
                logger.warning(f"✗ Game gave unexpected response for item {item_name}: {response}")


    # ===== GAME CLIENT (RedScript TCP Client) COMMUNICATION =====

    async def start_game_server(self) -> None:
        """
        Start the TCP server that the RedScript client connects to
        """
        try:
            self.game_server = await asyncio.start_server(
                self.handle_game_client,
                'localhost',
                self.game_server_port
            )

            # Start serving (accepting connections)
            await self.game_server.start_serving()

            logger.info(f"═══════════════════════════════════════════════")
            logger.info(f"  Cyberpunk 2077 TCP Server Started")
            logger.info(f"  Listening on: localhost:{self.game_server_port}")
            logger.info(f"  Ready to accept connections...")
            logger.info(f"═══════════════════════════════════════════════")

        except Exception as e:
            logger.error(f"✗ Failed to start game server: {e}")


    async def handle_game_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        """
        Handle connection from the RedScript TCP client
        """
        addr = writer.get_extra_info('peername')
        logger.info("")
        logger.info("═════════════════════════════════════════════════════════════")
        logger.info(f"  ✓ Cyberpunk 2077 client connected!")
        logger.info("═════════════════════════════════════════════════════════════")

        self.game_client_reader = reader
        self.game_client_writer = writer
        self.game_connected = True

        # If already connected to Archipelago, sync now
        if self.archipelago_connected:
            logger.info("Syncing items and configuration with game...")
            async_start(self.send_to_game("CONNECTED"))

        try:
            while True:
                # Read a line (command) from the game
                # Read a line from the TCP stream
                line = await reader.readline()

                if not line:
                    # Connection closed
                    break

                # Decode and strip whitespace
                command = line.decode('utf-8').strip()

                if not command:
                    continue

                logger.debug(f"← Game: {command}")

                # Process the command and get response
                response = await self.process_game_command(command)

                # Send response
                if response:
                    await self.send_to_game_raw(response)

        except asyncio.CancelledError:
            logger.info("Game client handler cancelled")
        except Exception as e:
            logger.error(f"✗ Error handling game client: {e}")
        finally:
            # GAME DISCONNECTED - Cleanup and disconnect from Archipelago
            logger.info("✗ Game disconnected!")
            self.game_connected = False
            self.game_client_writer = None
            self.game_client_reader = None
            writer.close()
            await writer.wait_closed()

            # Disconnect from Archipelago if connected
            if self.archipelago_connected:
                logger.info("Disconnecting from Archipelago server due to game disconnect...")
                await self.disconnect()
                self.archipelago_connected = False
                logger.info("Game disconnected. You can reconnect by restarting the client.")


    async def process_game_command(self, command: str) -> Optional[str]:
        """
        Process a command received from the RedScript client

        Args:
            command: The command string from RedScript

        Returns:
            Response string to send back to RedScript (or None)
        """
        try:
            # Split command by : delimiter
            parts = command.split(':')
            cmd = parts[0].upper()

            # ===== HELLO =====
            if cmd == "HELLO":
                # HELLO:<client_version>
                # Returns: HELLO:<server_version>:<OK|FAIL>
                # Example: HELLO:1.0.0

                if len(parts) != 2:
                    return "FAIL:Invalid HELLO format. Expected: HELLO:<client_version>"

                client_version = parts[1]
                print(f"HELLO from RedScript client version {client_version}")

                # Version compatibility check
                # Simple version string comparison
                # In production, you might want semantic version parsing
                is_compatible = self._check_version_compatibility(client_version)

                if is_compatible:
                    print(f"✓ Client version {client_version} is compatible")
                    return f"HELLO:{SERVER_VERSION}:OK"
                else:
                    print(f"✗ Client version {client_version} is incompatible (requires >= {MIN_CLIENT_VERSION})")
                    return f"HELLO:{SERVER_VERSION}:FAIL"


            # ===== CONNECT_REQ =====
            elif cmd == "CONNECT_REQ":
                # Simple handshake - game is checking if client is ready
                # No parameters needed, just return OK
                #logger.info("✓ Game sent CONNECT_REQ handshake")
                return "CONNECT_REQ:OK"


            # ===== SYNC_ITEMS =====
            elif cmd == "SYNC_ITEMS":
                # SYNC_ITEMS
                # Returns: ITEMS:<name>,<name>,<name>... or ITEMS: (empty if none)
                # Returns item names that RedScript can directly use

                if not self.archipelago_connected:
                    return "SYNC_ITEMS:FAIL:Not connected to Archipelago server"

                # Build comma-separated list of item names
                if self.received_item_ids:
                    # Convert IDs to names using our lookup function
                    item_names = []
                    for item_id in self.received_item_ids:
                        item_name = get_item_name_by_id(item_id)
                        if item_name:
                            item_names.append(item_name)
                        else:
                            # Fallback for unknown items
                            logger.warning(f"Unknown item ID: {item_id}")
                            item_names.append(f"Unknown Item {item_id}")

                    item_list = ','.join(item_names)
                    return f"SYNC_ITEMS:ITEMS:{item_list}"
                else:
                    return "SYNC_ITEMS:ITEMS:"


            elif cmd == "SYNC_CONFIG":
                # SYNC_CONFIG
                # Returns: CONFIG:<key>:<value>,<key>:<value>... or CONFIG: (empty if none)
                # Returns configuration values that RedScript can directly use

                if not self.archipelago_connected:
                    return "SYNC_CONFIG:FAIL:Not connected to Archipelago server"

                # Build comma-separated list of config key:value pairs
                if self.slot_data:
                    # Convert slot_data to key:value pairs
                    config_pairs = []
                    for key, value in self.slot_data.items():
                        # Convert boolean values to lowercase strings (true/false)
                        if isinstance(value, bool):
                            value_str = "true" if value else "false"
                        else:
                            value_str = str(value)
                        config_pairs.append(f"{key}:{value_str}")

                    config_list = ','.join(config_pairs)
                    return f"SYNC_CONFIG:CONFIG:{config_list}"
                else:
                    return "SYNC_CONFIG:CONFIG:"

            # ===== OK_READY =====
            elif cmd == "OK_READY":
                # OK_READY
                # Game confirms it's synced and ready

                logger.info("✓ Game is ready!")
                return "OK_READY:OK"


            # ===== CHECK =====
            elif cmd == "CHECK":
                # CHECK:<location_name>
                # Example: CHECK:Watson - Complete Gig 1

                if len(parts) != 2:
                    return "CHECK:FAIL:Invalid CHECK format. Expected: CHECK:<location_name>"

                location_name = parts[1]

                # If not connected, we log and return OK (as requested)
                if not self.archipelago_connected:
                    logger.warning(f"Got CHECK for '{location_name}' but not connected to Archipelago")
                    return "CHECK:OK"

                # Lookup location ID by name
                location_id = get_location_id_by_name(location_name)

                if location_id:
                    # Send location check to Archipelago server
                    await self.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": [location_id]
                    }])
                    logger.info(f"✓ Location checked: {location_name} ({location_id})")
                else:
                    # User requested NOT to return fail if it doesn't exist
                    logger.warning(f"Unknown location name: {location_name}. Skipping check.")

                return "CHECK:OK"


            # ===== CHECK_REQ =====
            elif cmd == "CHECK_REQ":
                # CHECK_REQ:<item_id>
                # Returns: TRUE or FALSE
                # Example: CHECK_REQ:77207001

                if len(parts) != 2:
                    return "CHECK_REQ:FAIL:Invalid CHECK_REQ format. Expected: CHECK_REQ:<item_id>"

                try:
                    item_id = int(parts[1])
                except ValueError:
                    return f"CHECK_REQ:FAIL:Invalid item ID: {parts[1]}"

                # Check if we have this item
                has_item = item_id in self.received_item_ids
                result = "TRUE" if has_item else "FALSE"
                return f"CHECK_REQ:{result}"


            # ===== GET_SLOT_DATA =====
            elif cmd == "GET_SLOT_DATA":
                # GET_SLOT_DATA:<key>
                # Returns: VALUE:<data> or FAIL:Key not found
                # Example: GET_SLOT_DATA:starting_district

                if len(parts) != 2:
                    return "GET_SLOT_DATA:FAIL:Invalid GET_SLOT_DATA format. Expected: GET_SLOT_DATA:<key>"

                key = parts[1]

                if key in self.slot_data:
                    value = self.slot_data[key]
                    return f"GET_SLOT_DATA:VALUE:{value}"
                else:
                    return f"GET_SLOT_DATA:FAIL:Key not found: {key}"


            # ===== STATUS =====
            elif cmd == "STATUS":
                # STATUS:<district_name>
                # Example: STATUS:Watson

                if len(parts) != 2:
                    return "STATUS:FAIL:Invalid STATUS format. Expected: STATUS:<district_name>"

                district = parts[1]
                logger.info(f"Player location: {district}")
                return "STATUS:OK"


            # ===== VICTORY =====
            elif cmd == "VICTORY":
                # VICTORY
                # Player completed the game

                if not self.archipelago_connected:
                    return "VICTORY:FAIL:Not connected to Archipelago server"

                # Send completion to server
                await self.send_msgs([{
                    "cmd": "StatusUpdate",
                    "status": ClientStatus.CLIENT_GOAL
                }])

                logger.info("🏆 VICTORY! Player completed the game!")
                return "VICTORY:OK"


            # ===== DEATHLINK_SEND =====
            elif cmd == "DEATHLINK_SEND":
                # DEATHLINK_SEND
                # Player died in Cyberpunk, notify other players

                # TODO: Implement Death Link sending to Archipelago
                # For now, just acknowledge
                logger.info("💀 Player died in Cyberpunk (sending Death Link to others)")
                return "DEATHLINK_SEND:OK"


            # ===== DISCONNECT =====
            elif cmd == "DISCONNECT":
                # DISCONNECT
                # Clean disconnect

                logger.info("Game requested disconnect")
                return "DISCONNECT:OK"


            # ===== UNKNOWN COMMAND =====
            else:
                logger.warning(f"Unknown command: {cmd}")
                return f"FAIL:Unknown command: {cmd}"

        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            return f"FAIL:Internal error: {str(e)}"


    def _check_version_compatibility(self, client_version: str) -> bool:
        """
        Check if the client version is compatible with this server

        Args:
            client_version: Version string from RedScript client

        Returns:
            True if compatible, False otherwise
        """
        try:
            # Parse version strings
            # Parse version strings as lists of integers
            client_parts = [int(x) for x in client_version.split('.')]
            min_parts = [int(x) for x in MIN_CLIENT_VERSION.split('.')]

            # Pad to same length
            while len(client_parts) < len(min_parts):
                client_parts.append(0)
            while len(min_parts) < len(client_parts):
                min_parts.append(0)

            # Compare: major.minor.patch
            # Compare version tuples
            return client_parts >= min_parts

        except Exception as e:
            logger.error(f"Error parsing version '{client_version}': {e}")
            return False  # If we can't parse, assume incompatible


    async def send_to_game(self, message: str) -> Optional[str]:
        """
        Send a message to the game and wait for response

        Args:
            message: Command string to send

        Returns:
            Response from the game (or None if failed)
        """
        if not self.game_connected or not self.game_client_writer:
            logger.warning("Cannot send to game - not connected")
            return None

        try:
            await self.send_to_game_raw(message)

            # Wait for response (with timeout)
            response_line = await asyncio.wait_for(
                self.game_client_reader.readline(),
                timeout=5.0
            )

            response = response_line.decode('utf-8').strip()
            logger.debug(f"→ Game: {response}")
            return response

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for game response")
            return None
        except Exception as e:
            logger.error(f"Error sending to game: {e}")
            return None


    async def send_to_game_raw(self, message: str) -> None:
        """
        Send a raw message to the game (no response expected)

        Args:
            message: Message to send
        """
        if not self.game_connected or not self.game_client_writer:
            return

        try:
            # RedScript needs \r\n line ending (CRLF)
            if not message.endswith('\r\n'):
                # Remove any existing line ending and add \r\n
                message = message.rstrip('\r\n\n') + '\r\n'

            # Send the message
            self.game_client_writer.write(message.encode('utf-8'))
            await self.game_client_writer.drain()

            logger.debug(f"→ Game: {message.strip()}")

        except Exception as e:
            logger.error(f"Error sending to game: {e}")
            self.game_connected = False


# ===== MAIN ENTRY POINT =====

def launch(*args: str) -> None:
    """
    Launch function called by the Archipelago Launcher.

    Entry point when launched from the GUI.
    Initializes logging and starts the async event loop.
    """
    async def main():
        parser = get_base_parser(description="Cyberpunk 2077 Archipelago Client")
        args_parsed = parser.parse_args(args)

        ctx = CyberpunkContext(args_parsed.connect, args_parsed.password)

        # Start the game TCP server
        logger.info("Starting Cyberpunk 2077 game server on localhost:51234")
        await ctx.start_game_server()

        # Run GUI if available, otherwise run CLI
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        # Start the main client loop (connects to Archipelago server)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

        await ctx.exit_event.wait()
        await ctx.shutdown()

    Utils.init_logging("CyberpunkClient", exception_logger="Client")

    import colorama
    colorama.just_fix_windows_console()

    asyncio.run(main())
    colorama.deinit()


if __name__ == "__main__":
    """
    Entry point when running this file directly
    """
    launch()


# ═════════════════════════════════════════════════════════════════════════════
# PROTOCOL DOCUMENTATION FOR REDSCRIPT MOD
# ═════════════════════════════════════════════════════════════════════════════

"""
═══════════════════════════════════════════════════════════════════════════════
SIMPLE TEXT-BASED TCP PROTOCOL (NO JSON REQUIRED!)
═══════════════════════════════════════════════════════════════════════════════

Connection Setup:
1. RedScript connects to localhost:51234
2. No handshake needed - just start sending commands!

Message Format:
- All messages are terminated with CRLF (\r\n) - Windows line ending
- Commands use : as delimiter
- Responses are simple strings
- RedScript should send: "COMMAND:PARAMS\r\n"
- Python server responds: "RESPONSE\r\n"

═══════════════════════════════════════════════════════════════════════════════
COMMANDS FROM REDSCRIPT TO PYTHON SERVER
═══════════════════════════════════════════════════════════════════════════════

1. HELLO:<client_version>
   Version handshake - verify client/server compatibility

   Example (compatible):
   → HELLO:1.0.0
   ← HELLO:1.0.0:OK

   Example (incompatible):
   → HELLO:0.5.0
   ← HELLO:1.0.0:FAIL

   RedScript should:
   - Send this as the first command after connecting
   - Parse response: HELLO:<server_version>:<status>
   - If status is FAIL, warn user to update from GitHub
   - If status is OK, proceed with normal commands


2. CONNECT_REQ:<url>:<port>:<slot_name>
   Connect to Archipelago server

   Example:
   → CONNECT_REQ:archipelago.gg:38281:Player1
   ← CONNECT_REQ:OK

   Error:
   ← CONNECT_REQ:FAIL:Connection failed: <reason>


3. SYNC_ITEMS
   Get all items the player should have (for initial sync)
   **NOW RETURNS ITEM NAMES INSTEAD OF IDs!**

   Example (with items):
   → SYNC_ITEMS
   ← SYNC_ITEMS:ITEMS:(comma seperated item list)

   Example (no items):
   → SYNC_ITEMS
   ← SYNC_ITEMS:ITEMS:

   Error:
   ← SYNC_ITEMS:FAIL:Not connected to Archipelago server

   RedScript should:
   - Parse response by splitting on ':'
   - First part is command echo (SYNC_ITEMS)
   - Second part is status (ITEMS or FAIL)
   - Third part (if ITEMS) is comma-separated item names
   - Grant each item to the player in the game


4. SYNC_CONFIG
   Get world configuration options (Death Link, Skill Points, etc.)
   **Called after SYNC_ITEMS during initial sync**

   Example (with config):
   → SYNC_CONFIG
   ← SYNC_CONFIG:CONFIG:death_link:true,world_version:1,skill_points_as_items:false

   Example (no config):
   → SYNC_CONFIG
   ← SYNC_CONFIG:CONFIG:

   Error:
   ← SYNC_CONFIG:FAIL:Not connected to Archipelago server

   RedScript should:
   - Parse response by splitting on ':'
   - First part is command echo (SYNC_CONFIG)
   - Second part is status (CONFIG or FAIL)
   - Third part (if CONFIG) is comma-separated key:value pairs
   - Apply each configuration option
   - Store configuration in APGameState for runtime use
   - Example keys: death_link (true/false), skill_points_as_items (true/false), world_version (int)


5. OK_READY
   Confirm sync is complete, game is ready to play

   Example:
   → OK_READY
   ← OK_READY:OK


6. CHECK:<location_name>
   Report that a location/check was completed

   Example:
   → CHECK:Watson - Complete Gig 1
   ← CHECK:OK

   Note: Always returns OK, even if not connected or location unknown.
   Warnings will be logged on the Python server.


6. CHECK_REQ:<item_id>
   Ask if player has a specific item (for access rules)

   Example (has item):
   → CHECK_REQ:77207001
   ← CHECK_REQ:TRUE

   Example (doesn't have):
   → CHECK_REQ:77207999
   ← CHECK_REQ:FALSE


7. GET_SLOT_DATA:<key>
   Get custom world data by key

   Example:
   → GET_SLOT_DATA:starting_district
   ← GET_SLOT_DATA:VALUE:Watson

   Error:
   ← GET_SLOT_DATA:FAIL:Key not found: starting_district


8. STATUS:<district_name>
   Update current player location (optional, for logging)

   Example:
   → STATUS:Watson
   ← STATUS:OK


9. VICTORY
   Report game completion

   Example:
   → VICTORY
   ← VICTORY:OK


10. DEATHLINK_SEND
    Report player death (send to other players via Death Link)

    Example:
    → DEATHLINK_SEND
    ← DEATHLINK_SEND:OK

    RedScript should:
    - Send this when the player dies in Cyberpunk
    - Server will notify other players


11. DISCONNECT
    Clean disconnect

    Example:
    → DISCONNECT
    ← DISCONNECT:OK


═══════════════════════════════════════════════════════════════════════════════
COMMANDS FROM PYTHON SERVER TO REDSCRIPT (PUSHED)
═══════════════════════════════════════════════════════════════════════════════

These are sent automatically by the server when events occur.
RedScript MUST respond to these commands.

1. ITEM_RECEIVED:<item_name>:<sender_name>
   New item received from multiworld
   **Sends item name and sender - NO IDs!**

   Example:
   ← ITEM_RECEIVED:Mantis Blades:Player2
   → ITEM_RECEIVED:OK

   Error (if RedScript can't add item):
   → ITEM_RECEIVED:FAIL:Inventory full

   RedScript should:
   - Parse the item name and sender (split on ':')
   - Add the item to player inventory (by name)
   - Show notification: "Received Mantis Blades from Player2"
   - Respond with ITEM_RECEIVED:OK on success
   - Respond with ITEM_RECEIVED:FAIL:<reason> on failure
   - No need to handle item IDs!


2. CONNECTED
   Successfully connected to Archipelago server

   Example:
   ← CONNECTED
   → OK


3. DEATHLINK_RECEIVED
   Another player died (Death Link)
   Server is telling Cyberpunk to kill the player

   Example:
   ← DEATHLINK_RECEIVED
   → DEATHLINK_RECEIVED:OK

   RedScript should:
   - Kill the player in Cyberpunk
   - Show notification: "You died from Death Link"
   - Respond with DEATHLINK_RECEIVED:OK


═══════════════════════════════════════════════════════════════════════════════
TYPICAL SESSION FLOW
═══════════════════════════════════════════════════════════════════════════════

1. Game Startup:
   RedScript → TCP Connect to localhost:51234
   RedScript → HELLO:1.0.0
   Python    ← HELLO:1.0.0:OK
   RedScript → (If FAIL, warn user to update)
   RedScript → CONNECT_REQ:archipelago.gg:38281:Player1
   Python    ← CONNECT_REQ:OK

2. Initial Sync:
   RedScript → SYNC_ITEMS
   Python    ← SYNC_ITEMS:ITEMS:Mantis Blades,Kerenzikov,Security Access Card
   RedScript → (Adds items to inventory by name)
   RedScript → SYNC_CONFIG
   Python    ← SYNC_CONFIG:CONFIG:death_link:true,world_version:1
   RedScript → (Applies configuration to APGameState)
   RedScript → OK_READY
   Python    ← OK_READY:OK

3. During Gameplay:
   RedScript → CHECK:Watson - Complete Gig 1
   Python    ← CHECK:OK

   Python    → ITEM_RECEIVED:Rare Quickhack:Player2
   RedScript ← ITEM_RECEIVED:OK

   RedScript → CHECK_REQ:772077004
   Python    ← CHECK_REQ:TRUE

4. Game Completion:
   RedScript → VICTORY
   Python    ← VICTORY:OK

5. Shutdown:
   RedScript → DISCONNECT
   Python    ← DISCONNECT:OK
   RedScript → TCP Disconnect


═══════════════════════════════════════════════════════════════════════════════
REDSCRIPT IMPLEMENTATION NOTES
═══════════════════════════════════════════════════════════════════════════════

RedScript TCP Client Pseudocode:

1. Connect to server:
   let socket = TcpSocket.Connect("localhost", 51234);

2. Send command:
   let command = "CHECK:Watson - Complete Gig 1\n";
   socket.Send(command);

3. Receive response:
   let response = socket.ReadLine(); // Reads until \n
   if (response == "OK") {
       // Success
   } else if (StartsWith(response, "FAIL:")) {
       // Error - extract message after "FAIL:"
       let error = SubString(response, 5);
       Log("Error: " + error);
   }

4. Listen for server pushes (in background thread):
   while (socket.IsConnected()) {
       let message = socket.ReadLine();
       if (StartsWith(message, "ITEM_RECEIVED:")) {
           // Parse: ITEM_RECEIVED:<name>:<sender>
           let parts = Split(message, ":");
           let itemName = parts[1];
           let sender = parts[2];

           // Give item to player
           GiveItem(itemName);
           ShowNotification("Received " + itemName + " from " + sender);

           // Respond
           socket.Send("ITEM_RECEIVED:OK\n");
        }
   }

No JSON parsing needed - just string splitting!


═══════════════════════════════════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════════

All errors follow the format: FAIL:<error_message>

RedScript should:
1. Check if response starts with "FAIL:"
2. Extract error message (everything after "FAIL:")
3. Log the error
4. Optionally show to player

Example:
   Response: "FAIL:Not connected to Archipelago server"
   → Log: "Archipelago Error: Not connected to Archipelago server"
   → Show player: "Not connected to Archipelago. Check logs."
"""
