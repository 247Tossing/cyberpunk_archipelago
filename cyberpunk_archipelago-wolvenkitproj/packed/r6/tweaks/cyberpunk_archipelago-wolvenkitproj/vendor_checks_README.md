# Vendor check TweakXL YAML (split by category)

Vendor sanity uses several `vendor_checks_*.yaml` files in this folder. **TweakXL** loads every `.yaml` here; files are prefixed `vendor_checks_0_` … `vendor_checks_5_` so **`vendor_checks_0_common.yaml` loads first** (shared `Items.APCheck_Price_*` modifiers referenced by all vendor check items).

| File | Contents |
|------|----------|
| `vendor_checks_0_common.yaml` | Price stat modifiers for vendor check items |
| `vendor_checks_1_ripperdoc.yaml` | Ripperdoc `VendorCheck_*` items + ripperdoc vendor `itemStock` |
| `vendor_checks_2_gunsmith.yaml` | 2nd Amendment + gunsmith items + weapon vendor stock (`VendorCheck_2ndAmendment_*` on `Vendors.wat_lch_gunsmith_01` Wilson / H10, and `Vendors.wat_kab_gunsmith_01` Kabuki) |
| `vendor_checks_3_clothing.yaml` | Clothing vendor checks + stock |
| `vendor_checks_4_melee.yaml` | Melee vendor checks + stock |
| `vendor_checks_5_netrunner.yaml` | Netrunner vendor checks + stock |

## Vendor identity cheat sheet

Maps `Vendors.*` TweakDB ID → VendorKey (in `VendorCheck_<Key>_*`) → AP display name prefix. PL = Phantom Liberty DLC only.

### Ripperdocs

| `Vendors.*` tweak | VendorKey | AP display name (sans slot) |
|-------------------|-----------|-----------------------------|
| `wat_lch_ripperdoc_01` | `Victor` | Victor's Shop |
| `cct_dtn_ripdoc_01` | `CctDtnRipdoc` | Downtown Ripperdoc (Darius Clarke) |
| `hey_spr_ripperdoc_01` | `HeySprRipperdoc` | Wellsprings Ripperdoc (Santiago Molina) |
| `pac_wwd_ripperdoc_01` | `PacWwdRipperdoc` | West Wind Estate Ripperdoc (Rony LaFleur) |
| `cz_con_ripdoc_01` | `CzConRipdoc` | Dogtown Ripperdoc (Eron Acedo) — PL |
| `cz_monument_ripperdoc_anderson` | `CzMonumentAnderson` | Dogtown Ripperdoc (Anthony Anderson) — PL |
| `cz_monument_ripperdoc_farida` | `CzMonumentFarida` | Dogtown Ripperdoc (Farida Nazeri) — PL |
| `std_arr_ripperdoc_01` | `StdArrRipperdoc` | Arroyo Ripperdoc (Rafael Pérez) |
| `std_rcr_ripperdoc_01` | `StdRcrRipperdoc` | Rancho Coronado Ripperdoc (Octavio) |
| `wat_kab_ripperdoc_01` | `WatKabRipperdoc01` | Kabuki Ripperdoc (Bucks' Clinic) |
| `wat_kab_ripperdoc_02` | `WatKabRipperdoc02` | Kabuki Ripperdoc (Dr. Chrome) |
| `wat_kab_ripperdoc_03` | `WatKabRipperdoc03` | Kabuki Ripperdoc (Instant Implants) |
| `wat_nid_ripperdoc_01` | `CassiusRyder` | Cassius Ryder's Clinic |
| `wbr_hil_ripdoc_01` | `WbrHilRipdoc` | Charter Hill Ripperdoc (Nina Kraviz) |
| `wbr_jpn_ripperdoc_01` | `WbrJpnRipperdoc01` | Japantown Ripperdoc (Clinic 01) |
| `wbr_jpn_ripperdoc_02` | `WbrJpnRipperdoc02` | Japantown Ripperdoc (Clinic 02) |
| `bls_ina_se1_ripperdoc_01` | `BlsInaSe1Ripperdoc01` | Jackson Plains Ripperdoc (Stall 1) — pre-camp-move |
| `bls_ina_se1_ripperdoc_02` | `BlsInaSe1Ripperdoc02` | Jackson Plains Ripperdoc (Stall 2) — post-camp-move |

Note: `wbr_jpn_ripperdoc_01` (Fingers M.D.) is documented as having a scripted lockout; both Japantown entries are kept generic until the exact TweakDB ↔ NPC mapping is confirmed in-game.

### Weapon Vendors

| `Vendors.*` tweak | VendorKey | AP display name (sans slot) |
|-------------------|-----------|-----------------------------|
| `wat_lch_gunsmith_01` + `wat_kab_gunsmith_01` | `2ndAmendment` | 2nd Amendment Shop |
| `cct_dtn_guns_01` | `CctDtnGunsmith` | Downtown Weapon Vendor |
| `hey_gle_gunsmith_01` | `HeyGleGunsmith` | The Glen Weapon Vendor |
| `hey_rey_gunsmith_01` | `HeyReyGunsmith` | Vista del Rey Weapon Vendor |
| `hey_spr_gunsmith_01` | `HeySprGunsmith` | Wellsprings Weapon Vendor |
| `pac_wwd_gunsmith_01` | `PacWwdGunsmith` | West Wind Estate Weapon Vendor |
| `std_arr_gunsmith_01` | `StdArrGunsmith` | Arroyo Weapon Vendor |
| `std_rcr_gunsmith_01` | `StdRcrGunsmith` | Rancho Coronado Weapon Vendor (Gun-O-Rama) |
| `wat_nid_gunsmith_01` | `WatNidGunsmith` | Northside Weapon Vendor (Iron & Lead) |
| `wbr_jpn_gunsmith_01` | `WbrJpnGunsmith` | Japantown Weapon Vendor (Rifles & Pistols) |
| `bls_ina_se1_gunsmith_01a` | `BlsInaSe1Gunsmith01a` | Jackson Plains Weapon Vendor (Marty Jenklow) |
| `bls_ina_se1_gunsmith_02` | `BlsInaSe1Gunsmith02` | Jackson Plains Weapon Vendor (Stall 2) |
| `bls_ina_se5_gunsmith_01` | `BlsInaSe5Gunsmith` | Rocky Ridge Weapon Vendor |
| `cz_con_gunsmith_01` | `CzConGunsmith` | Dogtown Weapon Vendor — PL |

### Clothing Vendors

| `Vendors.*` tweak | VendorKey | AP display name (sans slot) |
|-------------------|-----------|-----------------------------|
| `cct_cpz_cloth_02` | `CctCpzClothing` | Corpo Plaza Clothing Vendor (Appel de Paris) |
| `cct_dtn_cloth_01` | `CctDtnClothing` | Downtown Clothing Vendor (Jinguji) |
| `hey_spr_clothingshop_01` | `HeySprClothing` | Wellsprings Clothing Vendor (Stylishly) |
| `pac_cvi_clothingshop_01` | `PacCviClothing` | Coastview Clothing Vendor |
| `pac_wwd_clothingshop_01` | `PacWwdClothing` | West Wind Estate Clothing Vendor |
| `std_rcr_clothingshop_01` | `StdRcrClothing` | Rancho Coronado Clothing Vendor (Stylishly) |
| `wat_kab_clothingshop_01` | `WatKabClothing` | Kabuki Clothing Vendor |
| `wat_lch_clothingshop_01` | `WatLchClothing` | Little China Clothing Vendor (Stylishly) |
| `wat_nid_clothingshop_01` | `WatNidClothing` | Northside Clothing Vendor (Ded Zed) |
| `wbr_hil_clothingshop_01` | `WbrHilClothing` | Charter Hill Clothing Vendor (Avante) |
| `wbr_jpn_clothingshop_01` | `WbrJpnClothing01` | Japantown Clothing Vendor (Saeko's) |
| `wbr_jpn_clothingshop_02` | `WbrJpnClothing02` | Japantown Clothing Vendor (Karim Noel) |
| `bls_ina_se1_clothingshop_01` | `BlsInaSe1Clothing` | Jackson Plains Clothing Vendor |
| `cz_con_clothingshop_001` | `CzConClothing` | Dogtown Clothing Vendor — PL |

### Melee Vendors

| `Vendors.*` tweak | VendorKey | AP display name (sans slot) |
|-------------------|-----------|-----------------------------|
| `pac_cvi_melee_01` | `PacCviMelee` | Coastview Melee Vendor (Animals) |
| `pac_wwd_melee_01` | `PacWwdMelee` | West Wind Estate Melee Vendor |
| `std_arr_melee_01` | `StdArrMelee` | Arroyo Melee Vendor |
| `wat_lch_melee_01` | `WatLchMelee01` | Little China Melee Vendor (Coach Fred) |
| `wat_lch_melee_02` | `WatLchMelee02` | Little China Melee Vendor (2) |
| `wbr_jpn_melee_01` | `WbrJpnMelee` | Japantown Melee Vendor (Spector Cheng) |
| `bls_ina_se5_melee_01` | `BlsInaSe5Melee` | Rocky Ridge Melee Vendor |

### Netrunners

| `Vendors.*` tweak | VendorKey | AP display name (sans slot) |
|-------------------|-----------|-----------------------------|
| `hey_rey_netrunner_01` | `HeyReyNetrunner` | Vista del Rey Netrunner |
| `pac_cvi_techstore_01` | `PacCviNetrunner` | Coastview Netrunner (tech store) |
| `wat_lch_netrunner_01` | `WatLchNetrunner` | Little China Netrunner (Nix) |
| `wat_kab_netrunner_01` | `WatKabNetrunner` | Kabuki Netrunner (Yoko Tsuru) |
| `wbr_jpn_netrunner_01` | `WbrJpnNetrunner01` | Japantown Netrunner (Chang-Hoon Nam) |
| `wbr_jpn_netrunner_02` | `WbrJpnNetrunner02` | Japantown Netrunner (2) |
| `cz_con_netrunner_01` | `CzConNetrunner` | Dogtown Netrunner (Sammy Taylor) — PL |

Note: `pac_cvi_techstore_01` does not follow the standard district naming pattern (the cheat sheet lists `pac_cvi_techstore_0110` which does not match the in-game character `Character.pac_cvi_techstore_01`).

When adding a new vendor category, add a new numbered file or extend the matching file; keep `0_common` first alphabetically.
