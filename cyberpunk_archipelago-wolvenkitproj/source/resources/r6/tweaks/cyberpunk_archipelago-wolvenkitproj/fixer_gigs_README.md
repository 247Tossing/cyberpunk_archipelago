# Fixer gig tiers and story blocking (Fixers-Only goal)

Notes on how the Fixers-Only completion goal is enforced in game, and why there is
no `fixer_gigs_*.yaml` in this folder.

## What gates a gig in vanilla

Gig availability is decided by two things, and neither of them is a TweakDB record:

- **Street cred.** Each fixer releases their gigs in four tiers, and each tier has
  a street cred threshold that varies by district. See the tier table on the
  [wiki](https://cyberpunk.fandom.com/wiki/Cyberpunk_2077_Gigs); the per-gig
  requirements come from the district tables in the
  [gigs guide](https://www.gamerguides.com/cyberpunk-2077/guide/gigs/introduction/overview).
- **Content tokens.** The pacing system that drips new gigs and side jobs in over
  time rather than all at once. This is why a gig can stay hidden for a while even
  once its street cred requirement is met.

Both are evaluated inside quest phase graphs (`.questphase`), which read quest
facts. TweakXL only edits TweakDB, so **TweakXL cannot patch gig availability**.
Changing it directly would mean shipping modified `.questphase` resources through
ArchiveXL, which needs WolvenKit and the game files.

## How the mod unlocks tiers instead

Street cred is the one lever that is both authoritative and reachable from script,
so the mod raises street cred rather than patching quest phases:

1. `GIG_FIXER_TIERS` and `FIXER_TIER_STREET_CRED` in
   [locations.py](../../../../../../worlds/cyberpunk2077/locations.py) hold each
   gig's fixer, tier, and that tier's street cred threshold. This is the single
   source of truth.
2. Generation gates every gig above tier 1 behind a `<Fixer> Gig Tier <n>` item.
3. When that item arrives, `APFixerTierManager` records the fixer's highest
   unlocked tier in `ap_fixer_tier_<fixer>` and the highest street cred any
   unlocked tier calls for in `ap_required_street_cred`.
4. The CET bridge reads `ap_required_street_cred` and raises the player to that
   level via `Game.SetLevel("StreetCred", ...)`.

Street cred is global, so a high tier for one fixer can also open lower tiers for
another. That is deliberate: it makes the game **more** permissive than the
generation logic, never less, so a gig can never be logically expected while being
unavailable in game. The reverse would soft-lock a run.

`APConstants.GetFixerTierStreetCred` mirrors the Python thresholds and must stay in
step with them.

## Why street cred lives in CET rather than RedScript

Setting a proficiency level is a CET API. Putting the call in Lua means a wrong or
changed signature shows up as a line in `scripting.log`, instead of a RedScript
compile error that would stop the whole mod from loading.

## Story blocking

Story content cannot be withdrawn once it starts: an activated journal entry and
its map pin are registered permanently, and the quest graph is not script-driven.
What the client does instead:

- `APStoryQuestEnforcer` drops story checks rather than sending locations the slot
  does not have, and alerts the player by phone the first time it happens.
- `ap_fixers_only_mode` is set to 1 for the run, and
  `ap_story_blocked_<questId>` is set for each story check that was refused, so a
  future quest phase patch has facts to condition on.

Story quests therefore award nothing and count for nothing in a Fixers-Only run,
but a player who goes looking can still play them. Hard-blocking them needs
patched `.questphase` resources, which is a WolvenKit change rather than a TweakXL
one.

## Still to verify in game

The pieces above cannot be exercised without the game running. Worth checking on a
real save:

- Street cred rises when a tier item arrives, and the fixer's gigs appear
  (allowing for content token pacing).
- `ap_required_street_cred` survives a save load and reapplies.
- Nothing regresses for the other three completion goals, which never set
  `ap_fixers_only_mode`.
