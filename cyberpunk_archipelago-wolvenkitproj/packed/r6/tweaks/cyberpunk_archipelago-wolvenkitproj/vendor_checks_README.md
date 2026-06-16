# Vendor check TweakXL YAML (split by category)

Vendor sanity uses several `vendor_checks_*.yaml` files in this folder. **TweakXL** loads every `.yaml` here; files are prefixed `vendor_checks_0_` … `vendor_checks_5_` so **`vendor_checks_0_common.yaml` loads first** (shared `Items.APCheck_Price_*` modifiers referenced by all vendor check items).

| File | Contents |
|------|----------|
| `vendor_checks_0_common.yaml` | Price stat modifiers for vendor check items |
| `vendor_checks_1_ripperdoc.yaml` | Ripperdoc `VendorCheck_*` items + ripperdoc vendor `itemStock` |
| `vendor_checks_2_gunsmith.yaml` | 2nd Amendment + gunsmith items + weapon vendor stock (`Vendors.wat_kab_gunsmith_01` for 2nd Amendment checks) |
| `vendor_checks_3_clothing.yaml` | Clothing vendor checks + stock |
| `vendor_checks_4_melee.yaml` | Melee vendor checks + stock |
| `vendor_checks_5_netrunner.yaml` | Netrunner vendor checks + stock |

**Netrunner vendor audit (wiki / in-game roster):**

| Vendor | `Vendors.*` tweak | In this mod |
|--------|-------------------|-------------|
| Nix (Little China) | `wat_lch_netrunner_01` | Yes (`VendorCheck_WatLchNetrunner_*`) |
| Yoko Tsuru (Kabuki) | `wat_kab_netrunner_01` | Yes (`VendorCheck_WatKabNetrunner_*`) |
| Netrunner (Vista del Rey) | `hey_rey_netrunner_01` | Yes |
| Chang-Hoon Nam + unnamed Japantown netrunner | `wbr_jpn_netrunner_01`, `wbr_jpn_netrunner_02` | Yes |
| Sammy Taylor (EBM Petrochem Stadium, PL) | `cz_con_netrunner_01` | Yes (`VendorCheck_CzConNetrunner_*`) |
| Netrunner (Coastview, Pacifica) | `pac_cvi_techstore_01` | Yes (`VendorCheck_PacCviNetrunner_*` on `Vendors.pac_cvi_techstore_01`). The cheat sheet’s `pac_cvi_techstore_0110` id does not match the in-game vendor the player uses (`Character.pac_cvi_techstore_01`). |

When adding a new vendor category, add a new numbered file or extend the matching file; keep `0_common` first alphabetically.
