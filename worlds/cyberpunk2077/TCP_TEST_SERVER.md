# TCP Test Server for RedScript Development

## Overview

`test_server.py` is a standalone mock TCP server for testing your RedScript TCP client without needing the full Archipelago infrastructure.

## Features

- **Standalone**: No Archipelago connection required
- **Mock Responses**: Returns hardcoded test data for all commands
- **Full Logging**: Shows all RX (received) and TX (transmitted) messages
- **Same Protocol**: Uses identical protocol as the real server
- **Test Data**: Pre-loaded with sample items, locations, and slot data

## Usage

### Starting the Server

From the Archipelago root directory:

```bash
python worlds/cyberpunk2077/test_server.py
```

The server will start on **localhost:51234** and display:

```
======================================================================
  Cyberpunk 2077 TCP Test Server
======================================================================
  Status:     READY
  Listening:  localhost:51234
  Version:    1.0.0
======================================================================
  Waiting for RedScript client connection...
  Press Ctrl+C to stop the server
======================================================================
```

### Stopping the Server

Press **Ctrl+C** to stop the server gracefully.

## Testing from RedScript

Connect your RedScript TCP client to:
- **Host**: `localhost`
- **Port**: `51234`

### Important: Line Endings

RedScript requires **CRLF** (`\r\n`) line endings for all messages:
- All commands from RedScript should end with `\r\n`
- All responses from server end with `\r\n`
- This is the Windows line ending format

## Test Data

### Items (returned by SYNC_ITEMS)
The server returns these 4 test items by **name**:
1. `Mantis Blades`
2. `Kerenzikov`
3. `Security Access Card`
4. `Rare Quickhack`

### Item IDs (for CHECK_REQ testing)
- `772077001` - Mantis Blades (returns TRUE)
- `772077002` - Kerenzikov (returns TRUE)
- `772077003` - Security Access Card (returns TRUE)
- `772077004` - Rare Quickhack (returns TRUE)
- Any other ID returns FALSE

### Slot Data (for GET_SLOT_DATA testing)
- `starting_district` → `Watson`
- `gig_count` → `50`
- `difficulty` → `Normal`

## Supported Commands

All commands from the protocol are supported:

1. **HELLO:<version>** - Version handshake
2. **CONNECT_REQ:<url>:<port>:<slot>** - Simulates Archipelago connection
3. **SYNC_ITEMS** - Returns test items (by name!)
4. **OK_READY** - Confirms ready
5. **CHECK:<location_id>** - Always returns OK
6. **CHECK_REQ:<item_id>** - Returns TRUE/FALSE based on test IDs
7. **GET_SLOT_DATA:<key>** - Returns mock slot data
8. **STATUS:<district>** - Always returns OK
9. **VICTORY** - Always returns OK
10. **DEATHLINK** - Always returns OK
11. **DISCONNECT** - Always returns OK

## Server Responses

The server automatically sends these messages:
- **CONNECTED** - Sent 0.5 seconds after CONNECT_REQ succeeds

## Example Session

```
RedScript: HELLO:1.0.0
Server:    HELLO:1.0.0:OK

RedScript: CONNECT_REQ:test.server:38281:TestPlayer
Server:    OK
(0.5s delay)
Server:    CONNECTED

RedScript: SYNC_ITEMS
Server:    ITEMS:Mantis Blades,Kerenzikov,Security Access Card,Rare Quickhack

RedScript: OK_READY
Server:    OK

RedScript: CHECK_REQ:772077001
Server:    TRUE

RedScript: DISCONNECT
Server:    OK
```

## Logging

All messages are logged with timestamps:

```
04:15:23 - INFO - ← RX: SYNC_ITEMS
04:15:23 - INFO - Returning 4 test items
04:15:23 - INFO - → TX: ITEMS:Mantis Blades,Kerenzikov,Security Access Card,Rare Quickhack
```

## Notes

- The server uses the **name-based protocol** (items sent as names, not IDs)
- CONNECT_REQ will always succeed (no real Archipelago connection)
- All CHECK commands return OK (no validation)
- Perfect for testing your RedScript protocol implementation
- Use the real `CyberpunkClient.py` when ready to connect to Archipelago

## Troubleshooting

### "Address already in use" error

Port 51234 is already in use. Kill the existing process:

**Windows:**
```bash
netstat -ano | findstr :51234
taskkill //F //PID <PID>
```

**Linux/Mac:**
```bash
lsof -i :51234
kill <PID>
```

### No connection from RedScript

1. Verify server is running (`Waiting for RedScript client connection...` should be visible)
2. Check RedScript is connecting to `localhost:51234`
3. Check firewall isn't blocking port 51234

## Color Output (Optional)

The server supports colored output if `colorama` is installed:

```bash
pip install colorama
```

Without colorama, the server still works but uses plain text output.
