"""
Integration tests for TCP protocol

For C# Unity developers:
- These test the full TCP communication flow
- Simulates a real RedScript client connecting
- Tests end-to-end protocol behavior
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock


class MockTCPClient:
    """
    Mock TCP client that simulates RedScript behavior

    For C# devs:
    - Simulates a Socket client connecting to the server
    - Sends commands and receives responses
    - Like a test harness for network protocol testing
    """

    def __init__(self):
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None
        self.connected = False


    async def connect(self, host: str, port: int):
        """Connect to the TCP server"""
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False


    async def send_command(self, command: str) -> str:
        """
        Send a command and wait for response

        For C# devs:
        - Like NetworkStream.Write() + NetworkStream.Read()
        - Sends command with newline, waits for response
        """
        if not self.connected:
            raise RuntimeError("Not connected")

        # Send command (ensure newline)
        if not command.endswith('\n'):
            command += '\n'

        self.writer.write(command.encode('utf-8'))
        await self.writer.drain()

        # Read response
        response_line = await self.reader.readline()
        response = response_line.decode('utf-8').strip()

        return response


    async def disconnect(self):
        """Close the connection"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False


@pytest.mark.asyncio
class TestTCPProtocol:
    """
    Integration tests for the full TCP protocol

    For C# devs:
    - These are integration tests (test full system)
    - Spin up the actual TCP server
    - Connect a mock client
    - Verify full message flow
    """

    async def test_full_session_flow(self):
        """
        Test a complete session from connect to disconnect

        For C# devs:
        - End-to-end test of the protocol
        - Simulates a real game session
        """
        from worlds.cyberpunk2077.client import CyberpunkContext

        # Create context and start server
        ctx = CyberpunkContext(None, None)
        ctx.send_msgs = AsyncMock()  # Mock Archipelago communication

        # Start the game server
        await ctx.start_game_server()

        # Give server time to start
        await asyncio.sleep(0.1)

        try:
            # Create mock client
            client = MockTCPClient()

            # Connect to server
            connected = await client.connect('localhost', ctx.game_server_port)
            assert connected, "Failed to connect to server"

            # Wait for connection to be established
            await asyncio.sleep(0.1)

            # Test 1: Connect to Archipelago
            response = await client.send_command("CONNECT_REQ:test.server:38281:TestPlayer")
            # Connection will fail (no real server), but command should be acknowledged
            assert response == "OK" or response.startswith("FAIL")

            # Mark as connected for testing
            ctx.archipelago_connected = True

            # Test 2: Sync items (empty)
            response = await client.send_command("SYNC_ITEMS")
            assert response == "ITEMS:"

            # Test 3: Add some items and sync again
            ctx.received_item_ids = [77207001, 77207002]
            response = await client.send_command("SYNC_ITEMS")
            assert response == "ITEMS:77207001,77207002"

            # Test 4: OK_READY
            response = await client.send_command("OK_READY")
            assert response == "OK"

            # Test 5: Check location
            response = await client.send_command("CHECK:77207001")
            assert response == "OK"

            # Test 6: Check if has item
            response = await client.send_command("CHECK_REQ:77207001")
            assert response == "TRUE"

            response = await client.send_command("CHECK_REQ:77207999")
            assert response == "FALSE"

            # Test 7: Status update
            response = await client.send_command("STATUS:Watson")
            assert response == "OK"

            # Test 8: Disconnect
            response = await client.send_command("DISCONNECT")
            assert response == "OK"

            await client.disconnect()

        finally:
            # Clean up server
            if ctx.game_server:
                ctx.game_server.close()
                await ctx.game_server.wait_closed()


    async def test_multiple_commands_rapid(self):
        """
        Test sending multiple commands rapidly

        For C# devs:
        - Stress test for the protocol
        - Ensures server handles rapid requests
        """
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = True
        ctx.send_msgs = AsyncMock()

        await ctx.start_game_server()
        await asyncio.sleep(0.1)

        try:
            client = MockTCPClient()
            await client.connect('localhost', ctx.game_server_port)
            await asyncio.sleep(0.1)

            # Send 10 commands rapidly
            for i in range(10):
                response = await client.send_command(f"STATUS:District{i}")
                assert response == "OK", f"Command {i} failed"

            await client.disconnect()

        finally:
            if ctx.game_server:
                ctx.game_server.close()
                await ctx.game_server.wait_closed()


    async def test_error_handling(self):
        """
        Test error responses

        For C# devs:
        - Verifies error messages are formatted correctly
        - Tests FAIL: responses
        """
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = False  # Not connected

        await ctx.start_game_server()
        await asyncio.sleep(0.1)

        try:
            client = MockTCPClient()
            await client.connect('localhost', ctx.game_server_port)
            await asyncio.sleep(0.1)

            # Try to sync when not connected
            response = await client.send_command("SYNC_ITEMS")
            assert response.startswith("FAIL:")
            assert "Not connected" in response

            # Try invalid command format
            response = await client.send_command("CHECK:invalid")
            assert response.startswith("FAIL:")

            # Unknown command
            response = await client.send_command("INVALID_COMMAND")
            assert response.startswith("FAIL:")
            assert "Unknown command" in response

            await client.disconnect()

        finally:
            if ctx.game_server:
                ctx.game_server.close()
                await ctx.game_server.wait_closed()


    async def test_item_push_from_server(self):
        """
        Test server pushing items to client

        For C# devs:
        - Tests unsolicited messages from server
        - Simulates receiving items from other players
        """
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = True
        ctx.item_names = {77207001: "Mantis Blades"}
        ctx.player_names = {1: "Player1"}

        await ctx.start_game_server()
        await asyncio.sleep(0.1)

        try:
            client = MockTCPClient()
            await client.connect('localhost', ctx.game_server_port)
            await asyncio.sleep(0.1)

            # Simulate item received from Archipelago
            ctx.items_received = [
                MagicMock(item=77207001, player=1)
            ]

            # Manually trigger item send
            ctx.received_item_ids = [77207001]
            await ctx.send_new_items_to_game()

            # Client should receive ITEM message
            # Note: In a real scenario, client would need to be listening
            # This is a simplified test

            await client.disconnect()

        finally:
            if ctx.game_server:
                ctx.game_server.close()
                await ctx.game_server.wait_closed()


    async def test_reconnection(self):
        """
        Test client reconnecting

        For C# devs:
        - Verifies server handles disconnection/reconnection
        - Tests connection lifecycle
        """
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = True

        await ctx.start_game_server()
        await asyncio.sleep(0.1)

        try:
            # First connection
            client1 = MockTCPClient()
            await client1.connect('localhost', ctx.game_server_port)
            await asyncio.sleep(0.1)

            response = await client1.send_command("OK_READY")
            assert response == "OK"

            await client1.disconnect()
            await asyncio.sleep(0.1)

            # Server should accept new connection
            client2 = MockTCPClient()
            await client2.connect('localhost', ctx.game_server_port)
            await asyncio.sleep(0.1)

            response = await client2.send_command("OK_READY")
            assert response == "OK"

            await client2.disconnect()

        finally:
            if ctx.game_server:
                ctx.game_server.close()
                await ctx.game_server.wait_closed()


class TestProtocolCompliance:
    """
    Test protocol specification compliance

    For C# devs:
    - Verifies protocol matches documentation
    - Tests message format rules
    """

    @pytest.mark.asyncio
    async def test_all_commands_have_responses(self):
        """Verify every command gets a response"""
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = True
        ctx.send_msgs = AsyncMock()

        commands = [
            "SYNC_ITEMS",
            "OK_READY",
            "CHECK:77207001",
            "CHECK_REQ:77207001",
            "STATUS:Watson",
            "DISCONNECT"
        ]

        for command in commands:
            response = await ctx.process_game_command(command)
            assert response is not None, f"Command '{command}' returned None"
            assert len(response) > 0, f"Command '{command}' returned empty string"


    @pytest.mark.asyncio
    async def test_error_format(self):
        """Verify error messages follow FAIL: format"""
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = False

        # Commands that should fail
        error_commands = [
            "SYNC_ITEMS",  # Not connected
            "CHECK:77207001",  # Not connected
            "CHECK:invalid",  # Invalid ID
            "UNKNOWN_CMD"  # Unknown command
        ]

        for command in error_commands:
            response = await ctx.process_game_command(command)
            assert response.startswith("FAIL:"), f"Command '{command}' didn't return FAIL: format"


    @pytest.mark.asyncio
    async def test_items_format(self):
        """Verify ITEMS response is comma-separated"""
        from worlds.cyberpunk2077.client import CyberpunkContext

        ctx = CyberpunkContext(None, None)
        ctx.archipelago_connected = True
        ctx.received_item_ids = [77207001, 77207002, 77207003]

        response = await ctx.process_game_command("SYNC_ITEMS")

        assert response.startswith("ITEMS:")
        items_part = response[6:]  # Remove "ITEMS:"

        if items_part:  # If not empty
            # Verify format: numbers separated by commas
            items = items_part.split(',')
            for item in items:
                assert item.isdigit(), f"Item ID '{item}' is not a number"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
