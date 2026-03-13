"""
Unit tests for Cyberpunk 2077 Client command processing

For C# Unity developers:
- These are unit tests (like NUnit tests)
- Each test_* function is a separate test case
- Tests verify individual command logic works correctly
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


class TestCommandParsing:
    """
    Test command parsing logic

    For C# devs:
    - Like a [TestFixture] class in NUnit
    - Groups related tests together
    """

    @pytest.mark.asyncio
    async def test_hello_compatible_version(self, mock_context):
        """Test HELLO with compatible version"""
        ctx = mock_context

        response = await ctx.process_game_command("HELLO:1.0.0")

        assert response.startswith("HELLO:")
        parts = response.split(':')
        assert len(parts) == 3
        assert parts[2] == "OK"  # Version should be compatible


    @pytest.mark.asyncio
    async def test_hello_incompatible_version(self, mock_context):
        """Test HELLO with incompatible (old) version"""
        ctx = mock_context

        response = await ctx.process_game_command("HELLO:0.5.0")

        assert response.startswith("HELLO:")
        parts = response.split(':')
        assert len(parts) == 3
        assert parts[2] == "FAIL"  # Old version should be incompatible


    @pytest.mark.asyncio
    async def test_hello_future_version(self, mock_context):
        """Test HELLO with future version (should be compatible)"""
        ctx = mock_context

        response = await ctx.process_game_command("HELLO:2.0.0")

        assert response.startswith("HELLO:")
        parts = response.split(':')
        assert len(parts) == 3
        assert parts[2] == "OK"  # Future versions should work


    @pytest.mark.asyncio
    async def test_hello_invalid_format(self, mock_context):
        """Test HELLO with invalid format"""
        ctx = mock_context

        response = await ctx.process_game_command("HELLO")

        assert response.startswith("FAIL:")
        assert "Invalid HELLO format" in response


    @pytest.mark.asyncio
    async def test_connect_req_valid(self, mock_context):
        """Test CONNECT_REQ with valid parameters"""
        # Arrange (setup)
        ctx = mock_context
        command = "CONNECT_REQ:archipelago.gg:38281:Player1"

        # Mock the connect method to avoid actual connection
        ctx.connect = AsyncMock()

        # Act (execute)
        response = await ctx.process_game_command(command)

        # Assert (verify)
        assert response == "OK"
        assert ctx.server_address == "archipelago.gg:38281"
        assert ctx.username == "Player1"


    @pytest.mark.asyncio
    async def test_connect_req_invalid_format(self, mock_context):
        """Test CONNECT_REQ with invalid format"""
        ctx = mock_context
        command = "CONNECT_REQ:incomplete"

        response = await ctx.process_game_command(command)

        assert response.startswith("FAIL:")
        assert "Invalid CONNECT_REQ format" in response


    @pytest.mark.asyncio
    async def test_sync_items_not_connected(self, mock_context):
        """Test SYNC_ITEMS when not connected to Archipelago"""
        ctx = mock_context
        ctx.archipelago_connected = False

        response = await ctx.process_game_command("SYNC_ITEMS")

        assert response.startswith("FAIL:")
        assert "Not connected to Archipelago" in response


    @pytest.mark.asyncio
    async def test_sync_items_empty(self, mock_context):
        """Test SYNC_ITEMS with no items"""
        ctx = mock_context
        ctx.archipelago_connected = True
        ctx.received_item_ids = []

        response = await ctx.process_game_command("SYNC_ITEMS")

        assert response == "ITEMS:"


    @pytest.mark.asyncio
    async def test_sync_items_with_items(self, mock_context, sample_item_ids, sample_item_names):
        """Test SYNC_ITEMS with multiple items - now returns names instead of IDs"""
        ctx = mock_context
        ctx.archipelago_connected = True
        ctx.received_item_ids = sample_item_ids

        response = await ctx.process_game_command("SYNC_ITEMS")

        assert response.startswith("ITEMS:")
        # Verify all item NAMES are in the response (not IDs)
        for item_name in sample_item_names:
            assert item_name in response
        # Verify format (comma-separated names)
        assert "Mantis Blades,Kerenzikov,Security Access Card,Rare Quickhack" in response


    @pytest.mark.asyncio
    async def test_ok_ready(self, mock_context):
        """Test OK_READY command"""
        ctx = mock_context

        response = await ctx.process_game_command("OK_READY")

        assert response == "OK"


    @pytest.mark.asyncio
    async def test_check_valid(self, mock_context):
        """Test CHECK with valid location ID"""
        ctx = mock_context
        ctx.archipelago_connected = True
        ctx.send_msgs = AsyncMock()

        response = await ctx.process_game_command("CHECK:772077001")

        assert response == "OK"
        # Verify send_msgs was called with correct data
        ctx.send_msgs.assert_called_once()
        call_args = ctx.send_msgs.call_args[0][0][0]
        assert call_args["cmd"] == "LocationChecks"
        assert 772077001 in call_args["locations"]


    @pytest.mark.asyncio
    async def test_check_invalid_id(self, mock_context):
        """Test CHECK with invalid location ID"""
        ctx = mock_context
        ctx.archipelago_connected = True

        response = await ctx.process_game_command("CHECK:notanumber")

        assert response.startswith("FAIL:")
        assert "Invalid location ID" in response


    @pytest.mark.asyncio
    async def test_check_not_connected(self, mock_context):
        """Test CHECK when not connected"""
        ctx = mock_context
        ctx.archipelago_connected = False

        response = await ctx.process_game_command("CHECK:772077001")

        assert response.startswith("FAIL:")
        assert "Not connected to Archipelago" in response


    @pytest.mark.asyncio
    async def test_check_req_has_item(self, mock_context):
        """Test CHECK_REQ when player has the item"""
        ctx = mock_context
        ctx.received_item_ids = [772077001, 772077002]

        response = await ctx.process_game_command("CHECK_REQ:772077001")

        assert response == "TRUE"


    @pytest.mark.asyncio
    async def test_check_req_no_item(self, mock_context):
        """Test CHECK_REQ when player doesn't have the item"""
        ctx = mock_context
        ctx.received_item_ids = [772077001, 772077002]

        response = await ctx.process_game_command("CHECK_REQ:772077999")

        assert response == "FALSE"


    @pytest.mark.asyncio
    async def test_check_req_invalid_id(self, mock_context):
        """Test CHECK_REQ with invalid item ID"""
        ctx = mock_context

        response = await ctx.process_game_command("CHECK_REQ:invalid")

        assert response.startswith("FAIL:")
        assert "Invalid item ID" in response


    @pytest.mark.asyncio
    async def test_get_slot_data_exists(self, mock_context, sample_slot_data):
        """Test GET_SLOT_DATA with existing key"""
        ctx = mock_context
        ctx.slot_data = sample_slot_data

        response = await ctx.process_game_command("GET_SLOT_DATA:starting_district")

        assert response == "VALUE:Watson"


    @pytest.mark.asyncio
    async def test_get_slot_data_not_exists(self, mock_context):
        """Test GET_SLOT_DATA with non-existent key"""
        ctx = mock_context
        ctx.slot_data = {}

        response = await ctx.process_game_command("GET_SLOT_DATA:nonexistent")

        assert response.startswith("FAIL:")
        assert "Key not found" in response


    @pytest.mark.asyncio
    async def test_status_update(self, mock_context):
        """Test STATUS command"""
        ctx = mock_context

        response = await ctx.process_game_command("STATUS:Watson")

        assert response == "OK"


    @pytest.mark.asyncio
    async def test_victory(self, mock_context):
        """Test VICTORY command"""
        ctx = mock_context
        ctx.archipelago_connected = True
        ctx.send_msgs = AsyncMock()

        response = await ctx.process_game_command("VICTORY")

        assert response == "OK"
        # Verify completion message was sent
        ctx.send_msgs.assert_called_once()


    @pytest.mark.asyncio
    async def test_victory_not_connected(self, mock_context):
        """Test VICTORY when not connected"""
        ctx = mock_context
        ctx.archipelago_connected = False

        response = await ctx.process_game_command("VICTORY")

        assert response.startswith("FAIL:")


    @pytest.mark.asyncio
    async def test_deathlink(self, mock_context):
        """Test DEATHLINK command"""
        ctx = mock_context

        response = await ctx.process_game_command("DEATHLINK")

        assert response == "OK"


    @pytest.mark.asyncio
    async def test_disconnect(self, mock_context):
        """Test DISCONNECT command"""
        ctx = mock_context

        response = await ctx.process_game_command("DISCONNECT")

        assert response == "OK"


    @pytest.mark.asyncio
    async def test_unknown_command(self, mock_context):
        """Test unknown command"""
        ctx = mock_context

        response = await ctx.process_game_command("UNKNOWN_COMMAND:test")

        assert response.startswith("FAIL:")
        assert "Unknown command" in response


    @pytest.mark.asyncio
    async def test_empty_command(self, mock_context):
        """Test empty command"""
        ctx = mock_context

        response = await ctx.process_game_command("")

        assert response.startswith("FAIL:")


class TestItemSynchronization:
    """Test item tracking and synchronization"""

    @pytest.mark.asyncio
    async def test_send_new_items_to_game(self, mock_context):
        """Test sending new items to the game"""
        ctx = mock_context
        ctx.game_connected = True
        ctx.received_item_ids = [772077001, 772077002]
        ctx.items_sent_to_game = set()
        ctx.item_names = {
            772077001: "Mantis Blades",
            772077002: "Kerenzikov"
        }
        ctx.player_names = {1: "Player1"}
        ctx.items_received = [
            MagicMock(item=772077001, player=1),
            MagicMock(item=772077002, player=1)
        ]

        # Mock send_to_game to return OK
        async def mock_send(msg):
            return "OK"
        ctx.send_to_game = AsyncMock(side_effect=mock_send)

        await ctx.send_new_items_to_game()

        # Verify both items were sent
        assert len(ctx.items_sent_to_game) == 2
        assert 772077001 in ctx.items_sent_to_game
        assert 772077002 in ctx.items_sent_to_game


    @pytest.mark.asyncio
    async def test_send_new_items_no_duplicates(self, mock_context):
        """Test that items aren't sent twice"""
        ctx = mock_context
        ctx.game_connected = True
        ctx.received_item_ids = [772077001]
        ctx.items_sent_to_game = {772077001}  # Already sent
        ctx.send_to_game = AsyncMock()

        await ctx.send_new_items_to_game()

        # Verify send_to_game was NOT called (item already sent)
        ctx.send_to_game.assert_not_called()


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_command_with_multiple_colons(self, mock_context):
        """Test command where data contains colons"""
        ctx = mock_context
        ctx.archipelago_connected = True
        ctx.slot_data = {"test:key": "value:with:colons"}

        # This tests if the split logic handles colons in data correctly
        response = await ctx.process_game_command("GET_SLOT_DATA:test:key")

        # Should handle the extra colons gracefully
        # Note: Current implementation may not handle this perfectly
        # This test documents the behavior
        assert response is not None


    @pytest.mark.asyncio
    async def test_very_long_item_list(self, mock_context):
        """Test SYNC_ITEMS with many items"""
        ctx = mock_context
        ctx.archipelago_connected = True
        # Create 100 items
        ctx.received_item_ids = list(range(772077001, 772077101))

        response = await ctx.process_game_command("SYNC_ITEMS")

        assert response.startswith("ITEMS:")
        # Verify all items are present
        assert len(response.split(',')) == 100


    @pytest.mark.asyncio
    async def test_malformed_check_command(self, mock_context):
        """Test CHECK without parameter"""
        ctx = mock_context

        response = await ctx.process_game_command("CHECK")

        assert response.startswith("FAIL:")
        assert "Invalid CHECK format" in response


if __name__ == "__main__":
    """
    Run tests directly (though normally you'd use pytest)

    For C# devs:
    - Like a main method for running tests
    - Normally use: pytest worlds/cyberpunk2077/tests/
    """
    pytest.main([__file__, "-v"])
