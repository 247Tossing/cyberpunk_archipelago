"""
Cyberpunk 2077 Archipelago Client

This file implements the TCP server that communicates with the Cyberpunk 2077 RedScript mod.
It acts as a bridge between the Archipelago server and the game.
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
from worlds.cyberpunk2077.items import get_item_name_by_id, get_item_id_by_name, item_id_to_name, item_name_to_id, item_id_to_game_id
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
                self.output(f"Items received: {len(self.ctx.received_items)}")
                self.output(f"Items sent: {self.ctx.items_sent_count}")
                self.output(f"Locations checked: {len(self.ctx.checked_locations)}")
            else:
                self.output("Cyberpunk 2077 game is NOT CONNECTED.")
                self.output(f"Waiting on port {self.ctx.game_server_port}...")
        else:
            self.output("Not connected to a Cyberpunk 2077 session.")

    def _cmd_queue(self) -> None:
        """
        Display item queue status
        Usage: /queue
        """
        if isinstance(self.ctx, CyberpunkContext):
            queue_size = self.ctx.item_send_queue.qsize()
            total_received = len(self.ctx.received_items)
            total_sent = self.ctx.items_sent_count
            worker_running = (self.ctx.queue_worker_task and
                            not self.ctx.queue_worker_task.done())

            self.output("=" * 60)
            self.output("Item Queue Status")
            self.output("=" * 60)
            self.output(f"Queue size:         {queue_size} item(s) waiting")
            self.output(f"Items received:     {total_received}")
            self.output(f"Items sent:         {total_sent}")
            self.output(f"Items pending:      {total_received - total_sent}")
            self.output(f"Worker running:     {'Yes' if worker_running else 'No'}")
            self.output(f"Send delay:         {self.ctx.item_send_delay}s between items")
            self.output(f"Game connected:     {'Yes' if self.ctx.game_connected else 'No'}")
            self.output("=" * 60)

            if queue_size > 0:
                estimated_time = queue_size * self.ctx.item_send_delay
                self.output(f"Estimated time to clear queue: ~{estimated_time:.1f}s")
        else:
            self.output("Not connected to a Cyberpunk 2077 session.")

    def _cmd_itemdelay(self, delay: str = "") -> None:
        """
        Set or display the delay between item sends
        Usage: /itemdelay [seconds]
        Example: /itemdelay 1.0
        """
        if not isinstance(self.ctx, CyberpunkContext):
            self.output("Not connected to a Cyberpunk 2077 session.")
            return

        if not delay:
            # Display current delay
            self.output(f"Current item send delay: {self.ctx.item_send_delay}s")
            self.output("Use /itemdelay <seconds> to change (e.g., /itemdelay 1.0)")
            return

        try:
            new_delay = float(delay)
            if new_delay < 0.1:
                self.output("Error: Delay must be at least 0.1 seconds")
                return
            if new_delay > 10.0:
                self.output("Error: Delay cannot exceed 10 seconds")
                return

            old_delay = self.ctx.item_send_delay
            self.ctx.item_send_delay = new_delay
            self.output(f"Item send delay changed: {old_delay}s → {new_delay}s")
            self.output("New delay will apply to next item sent.")

        except ValueError:
            self.output(f"Error: Invalid delay value '{delay}'. Must be a number (e.g., 0.5)")


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

        # Location mapping: internal game IDs → display names
        # Used to translate location names from the game to Archipelago display names
        self.location_internal_id_to_display_name: Dict[str, str] = {}

        # Item tracking
        # Track ALL items received from the Archipelago server (including duplicates)
        # Each NetworkItem is unique even if they have the same item ID
        # Example: 3x "500 Eddies" = 3 separate NetworkItem objects
        self.received_items: List[NetworkItem] = []

        # Track how many items we've successfully sent to the game
        # Uses index-based counting instead of Set to allow duplicates
        self.items_sent_count: int = 0

        # Item sending queue and worker
        # Queue system to send items sequentially with rate limiting
        # Prevents overwhelming the RedSocket client with rapid-fire item commands
        self.item_send_queue: asyncio.Queue[NetworkItem] = asyncio.Queue()
        self.queue_worker_task: Optional[asyncio.Task] = None
        self.item_send_delay: float = 0.25  # Seconds between items (configurable)

        # Sync lock to prevent queue worker from interfering with handshake
        # Set to True during handshake, False when ready for item sending
        self.is_syncing: bool = False


    async def server_auth(self, password_requested: bool = False) -> None:
        """
        Authenticate with the Archipelago server.
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


    def on_deathlink(self, data: Dict[str, Any]) -> None:
        """
        Called when a DeathLink bounce arrives from the Archipelago server.
        Forwards the kill command to the Cyberpunk game.
        """
        super().on_deathlink(data)
        if self.game_connected:
            source = data.get("source", "Unknown")
            #logger.info(f"💀 DeathLink received from {source} — killing V in Cyberpunk 2077.")
            async_start(self.send_to_game_raw("DEATHLINK_RECEIVED\r\n"))


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

            # Load location mapping for translating internal game IDs to display names
            self.location_internal_id_to_display_name = self.slot_data.get("location_internal_id_to_display_name", {})

            # Register DeathLink tag with the Archipelago server based on slot data
            death_link_enabled = bool(self.slot_data.get("death_link", False))
            async_start(self.update_death_link(death_link_enabled))

            # Inform user about game connection
            if self.game_connected:
                # Game already connected - sync immediately
                #logger.info("Syncing items and configuration with game...")
                async_start(self.send_to_game("CONNECTED"))
            else:
                # Game not connected yet - this is normal, just inform user
                logger.info("")
                logger.info("=============================================================")
                logger.info("  Please connect Cyberpunk 2077 to the client:")
                logger.info("    1. Launch Cyberpunk 2077")
                logger.info("    2. Open CET overlay")
                logger.info("    3. Navigate to 'Archipelago Client'")
                logger.info(f"    4. Connect to localhost:{self.game_server_port}")
                logger.info("=============================================================")


        elif cmd == "ReceivedItems":
            # Server sent us items
            # Archipelago sends items incrementally with an index
            # index = starting position in the full item list
            # items = new items starting from that index
            start_index = args["index"]
            items: List[NetworkItem] = args["items"]

            # Check if these are new items or a resend (can happen on reconnect)
            if start_index < len(self.received_items):
                # We already have these items, skip
                #logger.debug(f"Skipping {len(items)} items (already received, start_index={start_index})")
                return

            # Add all new items to our list
            # Each NetworkItem is unique, even if they have the same item ID
            self.received_items.extend(items)
            #logger.info(f"Received {len(items)} item(s) from Archipelago (total: {len(self.received_items)})")

            # Send new items to the game if connected
            if self.game_connected:
                async_start(self.send_new_items_to_game())

        elif cmd == "RoomInfo":
            # Initial room information
            pass


    async def send_new_items_to_game(self) -> None:
        """
        Add new items to the send queue.

        Finds items that haven't been sent yet (by comparing sent count vs total received)
        and adds them to the queue. The queue worker will process them sequentially.

        This uses index-based tracking to allow duplicate items (e.g., 3x "500 Eddies"
        will all be queued and sent, not deduplicated).
        """
        if not self.game_connected:
            return

        # Find items we haven't sent yet (by index)
        total_received = len(self.received_items)

        if self.items_sent_count >= total_received:
            # All items already sent or queued
            return

        # Get items from items_sent_count to end of list
        # These are NetworkItem objects, not just IDs
        new_items = self.received_items[self.items_sent_count:]

        if not new_items:
            return

        # Add each NetworkItem to the queue
        for network_item in new_items:
            await self.item_send_queue.put(network_item)

        #logger.info(f"Queued {len(new_items)} item(s) for sending (queue size: {self.item_send_queue.qsize()})")


    async def item_queue_worker(self) -> None:
        """
        Background worker that processes the item send queue sequentially with rate limiting.

        This worker runs continuously while the game is connected, popping items from the
        queue one at a time and sending them to the game with a configurable delay between
        each item. This prevents overwhelming the RedSocket client with rapid-fire commands.

        The worker will:
        - Pop items from the queue (with timeout to check connection status)
        - Send ITEM_RECEIVED command to game
        - Wait for OK/FAIL response
        - Mark item as sent on success
        - Apply configurable delay before processing next item
        - Handle cancellation gracefully when game disconnects
        """
        #logger.info(f"Item queue worker started (delay: {self.item_send_delay}s between items)")

        try:
            while self.game_connected:
                # Wait while handshake is in progress
                # This prevents race condition with socket reader
                if self.is_syncing:
                    await asyncio.sleep(0.1)
                    continue

                try:
                    # Pop NetworkItem from queue (not just ID)
                    # Timeout allows us to check connection status periodically
                    network_item: NetworkItem = await asyncio.wait_for(
                        self.item_send_queue.get(),
                        timeout=1.0
                    )

                except asyncio.TimeoutError:
                    # No items in queue, check connection and loop again
                    continue

                # Get item ID from NetworkItem
                item_id = network_item.item

                # Get internal game ID for RedScript
                item_game_id = item_id_to_game_id.get(item_id)
                if not item_game_id:
                    # Fallback for unknown items
                    logger.warning(f"Unknown item ID in queue: {item_id}")
                    item_game_id = f"unknown_item_{item_id}"

                # Get display name for logging
                item_display_name = get_item_name_by_id(item_id) or item_game_id

                # Get sender from NetworkItem
                sender = self.player_names.get(network_item.player, f"Player {network_item.player}")

                # Send to game: ITEM_RECEIVED:<internal_game_id>:<sender>:<display_name>
                # RedScript receives the item and will send back ITEM_RECEIVED:OK as a separate command
                # Using fire-and-forget to avoid concurrency issues with handle_game_client reading
                await self.send_to_game_raw(f"ITEM_RECEIVED:{item_game_id}:{sender}:{item_display_name}")

                # Increment sent count immediately (game will process it)
                self.items_sent_count += 1
                #logger.info(f"→ Sent item to game: {item_display_name} (from {sender}) [{self.items_sent_count}/{len(self.received_items)}]")

                # Mark queue task as done
                self.item_send_queue.task_done()

                # Apply rate limiting delay before processing next item
                # Game processes items asynchronously in the engine
                # Delay ensures previous item completes before next is sent
                if self.game_connected and not self.item_send_queue.empty():
                    await asyncio.sleep(self.item_send_delay)

        except asyncio.CancelledError:
            # Worker cancelled (game disconnected)
            #logger.info("Item queue worker cancelled (game disconnected)")
            # Note: Items remaining in queue will be preserved for reconnect
            raise  # Re-raise to properly handle cancellation

        except Exception as e:
            logger.error(f"Error in item queue worker: {e}")
            # Worker will restart when game reconnects

        #finally:
            #logger.info("Item queue worker stopped")


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

            logger.info(f"=============================================================")
            logger.info(f"  Cyberpunk 2077 AP Server Started")
            logger.info(f"  Listening on: localhost:{self.game_server_port}")
            logger.info(f"  Ready to accept connections...")
            logger.info(f"=============================================================")

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
        logger.info("===========================")
        logger.info(f"    Game Connected")
        logger.info("===========================")

        self.game_client_reader = reader
        self.game_client_writer = writer
        self.game_connected = True

        # Set syncing flag to block queue worker during handshake
        # This prevents race condition where queue worker and handshake both try to read from socket
        if self.archipelago_connected:
            self.is_syncing = True
            #logger.info("Starting handshake - queue worker will wait...")

        # Start the item queue worker
        # This background task processes items sequentially with rate limiting
        # It will wait while is_syncing = True
        self.queue_worker_task = asyncio.create_task(
            self.item_queue_worker(),
            name="item_queue_worker"
        )

        # If already connected to Archipelago, game will initiate handshake
        # Don't call send_new_items_to_game() here - SYNC_ITEMS will handle catch-up
        # if self.archipelago_connected:
        #     # Handshake happens via game commands: HELLO → CONNECT_REQ → SYNC_ITEMS → SYNC_CONFIG
        #     pass

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
            # GAME DISCONNECTED - Cleanup game connection but stay connected to Archipelago
            logger.info("")
            logger.info("============================")
            logger.info("     Game disconnected")
            logger.info("============================")
            logger.info("")

            # Stop the queue worker before setting game_connected to False
            # This ensures a clean shutdown of the worker task
            if self.queue_worker_task and not self.queue_worker_task.done():
                self.queue_worker_task.cancel()
                try:
                    await self.queue_worker_task
                except asyncio.CancelledError:
                    pass  # Expected when cancelling the task
                except Exception as e:
                    logger.error(f"Error stopping queue worker: {e}")

            # Log queue status if there are remaining items
            queue_size = self.item_send_queue.qsize()
            if queue_size > 0:
                logger.info(f"  Note: {queue_size} item(s) remain in queue (will resume on reconnect)")

            self.game_connected = False
            self.game_client_writer = None
            self.game_client_reader = None
            writer.close()
            await writer.wait_closed()

            # Keep Archipelago connection alive for auto-reconnect when game restarts
            if self.archipelago_connected:
                logger.info("")
                logger.info("  Archipelago connection maintained.")
                logger.info("  Waiting for game to reconnect...")
                logger.info("  (No need to re-enter slot name)")
                logger.info("")
            else:
                logger.info("")
                logger.info("  Not connected to Archipelago.")
                logger.info("  Use /connect to connect when ready.")
                logger.info("")


    async def process_game_command(self, command: str) -> Optional[str]:
        """
        Process a command received from the RedScript client

        Args:
            command: The command string from RedScript

        Returns:
            Response string to send back to RedScript (or None)
        """
        try:
            #logger.info(f"processing command: '{command}'")
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
                #print(f"HELLO from RedScript client version {client_version}")

                # Version compatibility check
                # Simple version string comparison
                # In production, you might want semantic version parsing
                is_compatible = self._check_version_compatibility(client_version)

                if is_compatible:
                    print(f"Client version {client_version}")
                    return f"HELLO:{SERVER_VERSION}:OK"
                else:
                    logger.info(f"Client version {client_version} is incompatible (requires >= {MIN_CLIENT_VERSION})")
                    return f"HELLO:{SERVER_VERSION}:FAIL"


            # ===== CONNECT_REQ =====
            elif cmd == "CONNECT_REQ":
                # Simple handshake - game is checking if client is ready
                #logger.info("Game sent CONNECT_REQ handshake")
                return "CONNECT_REQ:OK"


            # ===== SYNC_ITEMS =====
            elif cmd == "SYNC_ITEMS":
                # SYNC_ITEMS:CURRENT_COUNT:<count>
                # Returns: ITEMS:<name>,<name>,<name>... or ITEMS: (empty if none)
                # Only returns NEW items (delta sync)
                if not self.archipelago_connected:
                    return "SYNC_ITEMS:FAIL:Not connected to Archipelago server"

                # Parse current count from game (if provided)
                current_count = 0
                if len(parts) >= 3 and parts[1] == "CURRENT_COUNT":
                    try:
                        current_count = int(parts[2])
                    except ValueError:
                        #logger.warning(f"Invalid CURRENT_COUNT in SYNC_ITEMS: {parts[2]}")
                        current_count = 0

                # Get total items received from Archipelago
                total_items = len(self.received_items)

                # Calculate delta: only send items from current_count onwards
                if current_count < total_items:
                    # Get new items (NetworkItem objects)
                    new_items = self.received_items[current_count:]

                    # Convert NetworkItem objects to game IDs
                    item_game_ids = []
                    for network_item in new_items:
                        item_id = network_item.item
                        item_name = item_id_to_game_id.get(item_id)

                        if item_name:
                            item_game_ids.append(item_name)
                        else:
                            # Fallback for unknown items
                            logger.warning(f"Unknown item ID: {item_id}")
                            item_game_ids.append(f"Unknown Item {item_id}")

                    item_list = ','.join(item_game_ids)
                    #logger.info(f"SYNC_ITEMS: Sending {len(new_items)} new items (game has {current_count}, server has {total_items})")
                    return f"SYNC_ITEMS:ITEMS:{item_list}"
                else:
                    # Game is up to date or ahead
                    #logger.info(f"SYNC_ITEMS: No new items (game has {current_count}, server has {total_items})")
                    return "SYNC_ITEMS:ITEMS:"


            elif cmd == "SYNC_CONFIG":
                # SYNC_CONFIG
                # Returns: CONFIG:<key>:<value>,<key>:<value>... or CONFIG: (empty if none)
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

                    # Handshake complete - allow queue worker to send items now
                    self.is_syncing = False
                    #logger.info("Handshake complete - queue worker can now send items")

                    return f"SYNC_CONFIG:CONFIG:{config_list}"
                else:
                    # Handshake complete even if no config
                    self.is_syncing = False
                    #logger.info("Handshake complete - queue worker can now send items")

                    return "SYNC_CONFIG:CONFIG:"

            # ===== SYNC_CHECKS =====
            elif cmd == "SYNC_CHECKS":
                # SYNC_CHECKS
                # Game requests ALL possible locations (called when save file loads)
                # Returns: LOCATIONS:<loc1>,<loc2>,<loc3>... with ALL locations from location_table
                # Game will verify each against FactsDB and respond with CHECK for ones it has completed
                if not self.archipelago_connected:
                    return "SYNC_CHECKS:FAIL:Not connected to Archipelago server"

                # Send ALL possible locations from the location table
                # location_internal_id_to_display_name contains all internal IDs from location_table
                if not self.location_internal_id_to_display_name:
                    # Mapping not loaded yet (shouldn't happen if Connected packet received)
                    logger.warning("SYNC_CHECKS: location mapping not available")
                    return "SYNC_CHECKS:LOCATIONS:"

                # Get all internal location IDs (keys of the mapping dict)
                all_location_ids = list(self.location_internal_id_to_display_name.keys())
                all_location_ids.extend(["q000_street_kid", "q000_corpo", "q000_nomad", "q201_heir", "q202_nomads", "q203_legend", "q204_reborn", "q307_tomorrow"])

                if all_location_ids:
                    location_list = ','.join(all_location_ids)
                    #logger.info(f"SYNC_CHECKS: Sending {len(all_location_ids)} total location(s) to game for verification")
                    return f"SYNC_CHECKS:LOCATIONS:{location_list}"
                else:
                    return "SYNC_CHECKS:LOCATIONS:"

            # ===== SYNC_COMPLETE =====
            elif cmd == "SYNC_COMPLETE":
                # SYNC_COMPLETE:CURRENT_COUNT:<count>
                # Game finished processing SYNC_ITEMS, update our sent count
                # This prevents the queue worker from re-sending items that were already synced

                if len(parts) >= 3 and parts[1] == "CURRENT_COUNT":
                    try:
                        game_count = int(parts[2])
                        # Update our sent count to match what the game has
                        # This ensures queue worker only sends NEW items from this point
                        self.items_sent_count = game_count
                        #logger.info(f"SYNC_COMPLETE: Game confirmed {game_count} items received, server counter synchronized")
                        return "SYNC_COMPLETE:OK"
                    except ValueError:
                        logger.warning(f"Invalid CURRENT_COUNT in SYNC_COMPLETE: {parts[2]}")
                        return "SYNC_COMPLETE:FAIL:Invalid count"
                else:
                    return "SYNC_COMPLETE:FAIL:Invalid format"


            # ===== OK_READY =====
            elif cmd == "OK_READY":
                #logger.info(" Game is ready!")
                return "OK_READY:OK"


            # ===== CHECK =====
            elif cmd == "CHECK":
                # CHECK:<location_name>

                if len(parts) != 2:
                    return "CHECK:FAIL:Invalid CHECK format. Expected: CHECK:<location_name>"

                location_name = parts[1]

                # If not connected, we log and return OK (as requested)
                if not self.archipelago_connected:
                    logger.warning(f"Got CHECK for '{location_name}' but not connected to Archipelago")
                    return "CHECK:OK"

                # Translate internal game ID to display name if needed
                # Game sends internal IDs like "q000_street_kid"
                # We need to convert to display names like "Prologue - The Streetkid"
                display_name = self.location_internal_id_to_display_name.get(location_name, location_name)

                # Lookup location ID by display name
                location_id = get_location_id_by_name(display_name)

                if location_id:
                    # Send location check to Archipelago server
                    # LocationChecks command requires integer location IDs, not names
                    await self.send_msgs([{
                        "cmd": "LocationChecks",
                        "locations": [location_id],
                    }])
                else:
                    # Location lookup failed - log detailed error for debugging
                    logger.error(f"Failed to check location: '{location_name}' (mapped to '{display_name}') - location ID not found")
                    logger.error(f"  This location may not be defined in location_table or the mapping is incorrect")

                return "CHECK:OK"


            # ===== ITEM_RECEIVED:OK =====
            elif cmd == "ITEM_RECEIVED" and len(parts) == 2 and parts[1] == "OK":
                # Game successfully processed an item
                # This is sent by RedScript after receiving ITEM_RECEIVED command
                # No response needed - this is purely informational
                logger.debug("✓ Game confirmed item received")
                return ""  # No response needed


            # ===== ITEM_RECEIVED:FAIL =====
            elif cmd == "ITEM_RECEIVED" and len(parts) >= 2 and parts[1] == "FAIL":
                # Game failed to process an item
                # Format: ITEM_RECEIVED:FAIL:<reason>
                reason = ":".join(parts[2:]) if len(parts) > 2 else "Unknown error"
                logger.error(f"✗ Game failed to process item: {reason}")
                return ""  # No response needed


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
            # Currently Unused
            elif cmd == "STATUS":
                # STATUS:<district_name>
                # Example: STATUS:Watson

                if len(parts) != 2:
                    return "STATUS:FAIL:Invalid STATUS format. Expected: STATUS:<district_name>"

                district = parts[1]
                #logger.info(f"Player location: {district}")
                return "STATUS:OK"


            # ===== DEATHLINK_SEND =====
            elif cmd == "DEATHLINK_SEND":
                # DEATHLINK_SEND
                # Player died in Cyberpunk, notify other players
                if "DeathLink" in self.tags:
                    player_name = self.player_names.get(self.slot, "V")
                    #logger.info(f"💀 DeathLink: {player_name} was killed in Cyberpunk 2077. Notifying other players...")
                    await self.send_death(f"{player_name} was killed in Cyberpunk 2077.")
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
                timeout=15.0
            )

            response = response_line.decode('utf-8').strip()
            #debug(f"→ Game: {response}")
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

            #logger.debug(f"→ Game: {message.strip()}")

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


#==============================================================================
# PROTOCOL DOCUMENTATION FOR REDSCRIPT MOD
#==============================================================================

"""
==============================================================================
SIMPLE TEXT-BASED TCP PROTOCOL
==============================================================================

Connection Setup:
RedScript connects to localhost:(port)

Message Format:
- All messages are terminated with CRLF (\r\n) - Windows line ending
- Commands use : as delimiter
- Responses are simple strings
- RedScript should send: "COMMAND:PARAMS\r\n"
- Python server responds: "RESPONSE\r\n"

==============================================================================
COMMANDS FROM REDSCRIPT TO PYTHON SERVER
==============================================================================


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


#==============================================================================
COMMANDS FROM PYTHON SERVER TO REDSCRIPT
#==============================================================================

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


#==============================================================================
TYPICAL SESSION FLOW
#==============================================================================

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

   RedScript → CHECK_REQ:<Key name>
   Python    ← CHECK_REQ:TRUE

4. Game Completion:
   RedScript → VICTORY
   Python    ← VICTORY:OK

5. Shutdown:
   RedScript → DISCONNECT
   Python    ← DISCONNECT:OK
   RedScript → TCP Disconnect

#==============================================================================
ERROR HANDLING
#==============================================================================

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
