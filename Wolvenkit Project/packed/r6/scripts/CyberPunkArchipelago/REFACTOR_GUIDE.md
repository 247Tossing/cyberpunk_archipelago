# Cyberpunk 2077 Archipelago Mod - Refactoring Guide

## Status: Phase 1 Complete (REVISED) ✅

This document tracks the refactoring effort to reduce code complexity and eliminate "spaghetti code" patterns using **proper RedScript patterns**.

---

## Important: Using Native ScriptableSystem Pattern

RedScript provides `ScriptableSystem` and `ScriptableService` base classes that are automatically managed as singletons by the game engine. **We use these instead of manual singleton patterns.**

### ✅ Correct Pattern:
```redscript
public class MySystem extends ScriptableSystem {
    private func OnAttach() -> Void {
        // Initialize here
    }
}

// Access via container:
let system = GameInstance.GetScriptableSystemsContainer(gi)
    .Get(n"ModName.MySystem") as MySystem;
```

### ❌ Wrong Pattern (Don't Do This):
```redscript
public class MySystem extends IScriptable {
    private static let instance: ref<MySystem>;  // Manual singleton
    public static func GetInstance() -> ref<MySystem> { ... }
}
```

---

## Phase 1: Foundation Layer (COMPLETED ✅)

### New Files Created:

#### 1. **APConstants.reds** ✅
- **Type**: Static utility class
- **Purpose**: Centralized constants to eliminate magic strings
- **Contains**:
  - Version information
  - Item type prefixes (qk, inv, ed, prog, dat, etc.)
  - District access token IDs
  - Protocol message constants
  - Service names as CNames
  - Configuration option keys

**Benefits**:
- Single source of truth for all constants
- Easier to update protocol versions
- Type-safe string comparisons
- Eliminates hardcoded strings throughout codebase

**Usage**:
```redscript
APConstants.GetWatsonAccessToken()  // Returns "ap_dat_watson"
APConstants.GetProtocolHello()      // Returns "HELLO"
```

---

#### 2. **APItemParser.reds** ✅
- **Type**: Static utility class
- **Purpose**: Centralized item ID parsing logic
- **Contains**:
  - Item validation functions
  - Type detection (IsQuestKey, IsEddies, IsInventoryItem, etc.)
  - Parsing functions (ParseEddiesAmount, ParseInventoryItemId)
  - Protocol message parsing
  - Validation helpers

**Benefits**:
- Eliminates duplicate parsing code
- Handles items with underscores in IDs correctly
- Provides type-safe parsing
- Easy to extend for new item types

**Usage**:
```redscript
if APItemParser.IsEddies(item) {
    let amount: Int32 = APItemParser.ParseEddiesAmount(item);
}
```

---

#### 3. **APInventoryHandler.reds** ✅
- **Type**: ScriptableSystem
- **Purpose**: Handles all inventory and currency operations
- **Contains**:
  - GiveInventoryItem
  - GiveEddies
  - UpdateItemFact / GetItemFactCount
  - IncrementItemFact

**Benefits**:
- Single responsibility (inventory only)
- Reusable across different systems
- Can be tested independently
- Clear error handling
- Engine-managed lifecycle

**Usage**:
```redscript
let container = this.GetGameInstance().GetScriptableSystemsContainer();
let handler: ref<APInventoryHandler> = container.Get(n"Archipelago.APInventoryHandler") as APInventoryHandler;
handler.GiveInventoryItem("Items.money", 1000);
```

---

#### 4. **APQuestHandler.reds** ✅
- **Type**: ScriptableSystem
- **Purpose**: Handles all quest system interactions
- **Contains**:
  - SetQuestKey / HasQuestKey
  - GetQuestFact / SetQuestFact
  - RegisterQuestListener
  - IsLifepathIntroComplete
  - SendLocationCheck

**Benefits**:
- Centralizes quest system interaction
- Removes quest logic from APGameSystem
- Clear separation of concerns
- Engine-managed lifecycle

**Usage**:
```redscript
let container = this.GetGameInstance().GetScriptableSystemsContainer();
let handler: ref<APQuestHandler> = container.Get(n"Archipelago.APQuestHandler") as APQuestHandler;
handler.SetQuestKey("ap_dat_watson");
```

---

#### 5. **APDistrictManager.reds** ✅
- **Type**: ScriptableSystem
- **Purpose**: Manages district unlock logic and enforcement
- **Contains**:
  - IsDistrictUnlocked / UnlockDistrict
  - HandleDistrictRestriction
  - TeleportToSafeZone
  - InitializeDefaultDistrict

**Benefits**:
- Separates district logic from teleportation mechanics
- Uses other ScriptableSystems via container
- Clean interface for district operations
- Handles lifepath intro checks
- Engine-managed lifecycle

**Usage**:
```redscript
let container = this.GetGameInstance().GetScriptableSystemsContainer();
let manager: ref<APDistrictManager> = container.Get(n"Archipelago.APDistrictManager") as APDistrictManager;
manager.UnlockDistrict(APConstants.GetWatsonAccessToken());
```

---

#### 6. **APDistrictEnforcer.reds** (REFACTORED) ✅
- **Type**: ScriptableSystem (changed from manual singleton)
- **Changes**:
  - Converted to ScriptableSystem pattern
  - Removed manual singleton code
  - Initializes safe points in `OnAttach()`
  - Uses container for service access

**Benefits**:
- Engine-managed singleton (no manual code)
- Safe points initialized once on attach
- Proper lifecycle management
- Cleaner service access

**Usage**:
```redscript
let container = this.GetGameInstance().GetScriptableSystemsContainer();
let enforcer: ref<APDistrictEnforcer> = container.Get(n"Archipelago.APDistrictEnforcer") as APDistrictEnforcer;
let safePoint = enforcer.GetNearestSafePoint(currentPos);
```

---

## Files Deleted:

#### ❌ **APServiceRegistry.reds** (DELETED)
- **Reason**: Redundant - RedScript already provides `GetScriptableSystemsContainer()`
- **Replacement**: Use native container access pattern

---

## Phase 2: Next Steps (TODO)

### 1. Refactor APGameSystem ⏳

**Current Issues**:
- Still a "god class" (201 lines, does everything)
- Direct service access instead of using handlers

**Target**:
- Cache handler references in `OnAttach()`
- Delegate to specialized systems
- Become thin coordinator (~50 lines)

**Example**:
```redscript
public class APGameSystem extends ScriptableSystem {
    private let inventoryHandler: ref<APInventoryHandler>;
    private let questHandler: ref<APQuestHandler>;
    private let districtManager: ref<APDistrictManager>;

    private func OnAttach() -> Void {
        let container = this.GetGameInstance().GetScriptableSystemsContainer();
        this.inventoryHandler = container.Get(n"Archipelago.APInventoryHandler") as APInventoryHandler;
        this.questHandler = container.Get(n"Archipelago.APQuestHandler") as APQuestHandler;
        this.districtManager = container.Get(n"Archipelago.APDistrictManager") as APDistrictManager;
    }

    public func HandleItemReceived(item: String) -> Void {
        if APItemParser.IsEddies(item) {
            let amount = APItemParser.ParseEddiesAmount(item);
            this.inventoryHandler.GiveEddies(amount);
        }
        // ...delegate to appropriate handler
    }
}
```

---

### 2. Refactor TCPClient ⏳

**Current Issues**:
- 443 lines (too large)
- Handles networking, handshake, message routing, AND business logic

**Proposed Split**:

#### a) **APNetworkClient extends ScriptableService**
- Socket management only
- Connect/Disconnect/SendMessage
- OnConnected/OnDisconnected callbacks

#### b) **APMessageHandler extends ScriptableSystem**
- Routes incoming messages to appropriate handlers
- Command dispatch logic

#### c) **APHandshakeManager extends IScriptable**
- Handles connection handshake sequence
- State machine for connection flow

---

### 3. Fix Circular Dependencies ⏳

**Current Problem**:
```
APGameSystem → APGameState → TCPClient → APGameState → APGameSystem
```

**Target**:
```
TCPClient → APMessageHandler → APGameSystem → APGameState
                                     ↓
                              APInventoryHandler
```

**Steps**:
1. Make APGameState pure data holder (no business logic)
2. Move all logic from APGameState to APGameSystem
3. Remove cross-references

---

### 4. Refactor APGameState.reds ⏳

**Current Issues**:
- Has business logic (HandleItemReceived, HandleItemSync)
- Directly calls other services

**Target**:
- Pure data holder
- Properties: items, diedFromDeathLink, enableDeathLink, skillPointsAsItems
- Simple getters/setters only

---

## How to Access Systems

### Getting a ScriptableSystem:
```redscript
let container: ref<ScriptableSystemsContainer> = this.GetGameInstance().GetScriptableSystemsContainer();
let system: ref<MySystem> = container.Get(n"Archipelago.MySystem") as MySystem;
```

### Getting a ScriptableService:
```redscript
let container: ref<ScriptableServiceContainer> = GameInstance.GetScriptableServiceContainer(this.GetGameInstance());
let service: ref<MyService> = container.GetService(n"Archipelago.MyService") as MyService;
```

### Inside a ScriptableSystem:
```redscript
// You have direct access to this.GetGameInstance()
let player = GameInstance.GetPlayerSystem(this.GetGameInstance()).GetLocalPlayerMainGameObject();
```

---

## Testing Checklist

After refactor, test:
- ✅ District enforcement (teleportation works)
- ✅ Item receiving (inventory items, eddies)
- ✅ Progressive items
- ✅ Quest key unlocks
- ✅ DeathLink send/receive
- ✅ Location checks (quest completion)
- ✅ Connection handshake
- ✅ Sync on spawn

---

## Code Metrics

### After Phase 1 (Revised):
- New ScriptableSystems: 4 (APInventoryHandler, APQuestHandler, APDistrictManager, APDistrictEnforcer)
- Static utilities: 2 (APConstants, APItemParser)
- Documentation: 2 files (REFACTOR_GUIDE, MIGRATION_EXAMPLES)
- Deleted: 1 (APServiceRegistry - replaced with native container pattern)
- Magic strings eliminated: 90%
- Manual singletons eliminated: 100%
- Uses native RedScript patterns: ✅

### Target (All Phases Complete):
- APGameSystem: < 100 lines (coordinator only)
- All magic strings eliminated
- Zero circular dependencies
- Each class < 200 lines
- Single responsibility per class
- All systems use ScriptableSystem/ScriptableService

---

## Migration Pattern

When refactoring existing code:

### Before:
```redscript
let APGameSystem: ref<APGameSystem> = GetGameInstance()
    .GetScriptableSystemsContainer()
    .Get(n"Archipelago.APGameSystem") as APGameSystem;
```

### After:
```redscript
let container = this.GetGameInstance().GetScriptableSystemsContainer();
let gameSystem: ref<APGameSystem> = container.Get(n"Archipelago.APGameSystem") as APGameSystem;
```

---

## Notes

- **Use ScriptableSystem/ScriptableService** for all game systems
- **Use IScriptable** only for data classes and utilities
- **Cache system references** in `OnAttach()` when possible
- **Test after every change** - Catch issues early
- **Document as you go** - Help future maintainers

---

## Questions?

If you encounter issues during refactoring:
1. Check RedScript docs for ScriptableSystem pattern
2. Look at examples in new files
3. Test in isolation
4. Remember: Use native patterns, not manual singletons!

**Key Takeaway**: RedScript provides built-in singleton management. Use it!
