"""
Pytest configuration and fixtures for Cyberpunk 2077 tests

For C# Unity developers:
- Fixtures are like setup methods that run before tests
- Similar to [SetUp] in NUnit or Awake() in Unity tests
- They provide reusable test data and mocks
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import MagicMock


@pytest.fixture
def mock_multiworld():
    """
    Create a mock MultiWorld instance

    For C# devs:
    - Like creating a mock/stub object
    - Provides fake implementation for testing
    """
    mock = MagicMock()
    mock.player_name = {1: "TestPlayer"}
    mock.get_location = MagicMock(return_value=MagicMock())
    mock.get_entrance = MagicMock(return_value=MagicMock())
    return mock


@pytest.fixture
def mock_context():
    """
    Create a mock CyberpunkContext for testing

    For C# devs:
    - Provides a fake game context without network connections
    - Like a test double or mock object
    """
    from worlds.cyberpunk2077.client import CyberpunkContext
    from unittest.mock import MagicMock

    # Create a minimal mock context without the full initialization
    ctx = MagicMock(spec=CyberpunkContext)
    ctx.server = None
    ctx.archipelago_connected = False
    ctx.game_connected = False
    ctx.received_item_ids = []
    ctx.items_sent_to_game = set()
    ctx.slot_data = {}
    ctx.item_names = {}
    ctx.player_names = {}
    ctx.items_received = []
    ctx.server_address = None
    ctx.username = None

    # Use the actual methods from the real class
    from worlds.cyberpunk2077.client import CyberpunkContext as RealContext
    ctx.process_game_command = RealContext.process_game_command.__get__(ctx, RealContext)
    ctx._check_version_compatibility = RealContext._check_version_compatibility.__get__(ctx, RealContext)
    ctx.send_new_items_to_game = RealContext.send_new_items_to_game.__get__(ctx, RealContext)

    return ctx


@pytest.fixture
def sample_slot_data() -> Dict[str, Any]:
    """
    Sample slot data for testing

    For C# devs:
    - Test data fixture
    - Like a const dictionary with test values
    """
    return {
        "world_version": 1,
        "starting_district": "Watson",
        "gig_count": 50
    }


@pytest.fixture
def sample_item_ids():
    """
    Sample item IDs for testing

    For C# devs:
    - Test data with sample item IDs
    - Note: IDs use underscore format (77_2077_001 = 772077001)
    """
    return [77_2077_001, 77_2077_002, 77_2077_003, 77_2077_004]


@pytest.fixture
def sample_item_names():
    """
    Sample item names for testing (corresponds to sample_item_ids)

    For C# devs:
    - Test data with sample item names
    """
    return ["Mantis Blades", "Kerenzikov", "Security Access Card", "Rare Quickhack"]


@pytest.fixture
def sample_item_mapping():
    """
    Sample item ID to name mapping for testing

    For C# devs:
    - Provides bidirectional lookup test data
    """
    return {
        77_2077_001: "Mantis Blades",
        77_2077_002: "Kerenzikov",
        77_2077_003: "Security Access Card",
        77_2077_004: "Rare Quickhack"
    }


@pytest.fixture
def event_loop():
    """
    Provide an event loop for async tests

    For C# devs:
    - Allows testing async/await code
    - Like setting up a test coroutine runner
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_tcp_streams():
    """
    Create mock TCP reader/writer streams

    For C# devs:
    - Simulates NetworkStream without actual network connection
    - Allows testing TCP protocol without sockets
    """
    # Create in-memory streams for testing
    reader = asyncio.StreamReader()
    writer_transport = MagicMock()
    writer_protocol = MagicMock()
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())

    return reader, writer
