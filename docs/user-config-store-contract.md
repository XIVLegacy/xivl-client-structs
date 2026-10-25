# User config store contracts

[`manifests/user_config_store.json`](../manifests/user_config_store.json)
records the stores behind the `_getUserConfig`, `_setUserConfig`,
`_saveUserConfig` and `_resetUserConfig` natives of the
[desktop contracts](desktop-native-call-contract.md#user-config). It lists
the group count of each store, every registered group and key with its name,
value type, range words and default, the per-character file that overrides
those defaults and the text format and override order of that file. The
contracts describe the client's constructor defaults and file handling, not
what a retail character file held.

## Binary and method

Input: retail `ffxivgame.exe`, version `2012.09.19.0001`, PE32 x86, image
base `0x00400000`, `15996808` bytes, SHA-256
`9341f2b4567440b310a4d494f5cc5599ca334ba51c8042247317ff466492f2e9`, as pinned
by [`manifests/retail_inputs.json`](../manifests/retail_inputs.json).
Addresses are absolute VAs. The observations came from instruction listings
decoded from the PE bytes through its section table. A script took the pushed
arguments of every call to the two record registrars, tracked register
operands through `mov`, `xor`, `or` and `lea`, and read each name and default
literal from the string constructor call that builds it.

## Stores

Three stores share one record model. The class names come from the RTTI of
the vftable that each constructor writes.

| Store | RTTI class | Constructor | Placement | Groups | Registrations |
| --- | --- | --- | --- | ---: | ---: |
| Game | `Application::Misc::GameConfig` | `0x004C4750` | context `+0x17430` | 7 | 145 |
| UI | `Application::Misc::UserConfig` | `0x004BB3D0` | context `+0x174C8` | 6 | 192 |
| System | `Application::Misc::SystemConfig` | `0x004B8640` | `Main +0x3A0` | 10 | 139 |

`0x004D73C0` returns the game store, so every `_getUserConfig` call
addresses it. The RTTI class named `UserConfig` is the UI store. The game and
UI constructors reach the shared `Sqex::Misc::Config` constructor
`0x00444150` through the `ResourceConfig` constructor `0x004B66F0`. The system
constructor calls `0x00444150` directly. The sole caller `0x0040179D` of the
system constructor passes `this + 0x3A0`, which agrees with the `SystemConfig`
placement in [`manifests/structs.json`](../manifests/structs.json).

The 145 game registrations cover 139 distinct group and key pairs. The other
six are the alternate defaults of group 4 keys 0 to 5.

## Record model

The group count sits at store `+0x04` and the record array at `+0x08`. The
constructor `0x00444150` allocates `groupCount * 32` records of `0xBC` bytes
and `0x00443C30` constructs each with type tag 0. The dirty byte at `+0x0C`
is set by both registrars and by the set accessors.

| Offset | Field |
| ---: | --- |
| `+0x00` | Type tag. 0 is unregistered, 1 is int and 2 is string. |
| `+0x04` | Name, a `0x54`-byte inline string. |
| `+0x58` | Range word one, type 1 only. |
| `+0x5C` | Range word two, type 1 only. |
| `+0x60` | Int value. |
| `+0x64` | Int default. |
| `+0x68` | String value, a `0x54`-byte inline string. |

The registrars write the record at `(group * 32 + (key & 0x1F)) * 0xBC`.

| Registrar | Kind | Arguments | Writes |
| --- | --- | --- | --- |
| `0x00443CF0` | int | name, group, key, min, max, default | type 1, name, `+0x58` min, `+0x5C` max, `+0x60` and `+0x64` default |
| `0x00443D50` | string | name, group, key, default | type 2, name, `+0x68` default |

The range words are an inclusive signed minimum and maximum. The test
`0x00444110` returns true for a type 1 record when `+0x58 <= value <= +0x5C`
by signed compare. The int setter `0x00443DD0`, the Lua setter target
`0x0075C980` and the file parser `0x004448E0` never apply the range. Besides
the two text writers `0x00443ED0` and `0x00444730`, the test is the only code
that reads both words, and the image has no `rel32` call or absolute
reference to it. The ranges are therefore metadata that the client does not
enforce on the traced paths.

Lua reaches the game store through `_getUserConfig` target `0x0075CAB0`,
`_setUserConfig` target `0x0075C980` (int) or `0x0075CA70` (string),
`_resetUserConfig` target `0x0075C9C0` and `_saveUserConfig` target
`0x0075CBA0`, which jumps to the game store writer `0x004C72F0`. All five
resolve the store through `0x004D73C0`. The two set targets call
`0x004B6780` with `(0, group, key)` after the write, and the reset target
does so after a type 1 or type 2 reset and skips it for a type 0 record.
`0x004B6780` forwards to the listener held at store `+0x20` when one is
set.

## Game store

`_getUserConfig(group, key)` passes each argument minus 1, so the Lua group
and key of this page are the native ids plus 1. A record that was never
registered keeps type 0 and the native returns nil. Groups register keys
0 to `keyCount - 1`, so group 1 registers all 32 keys and every other group
leaves its upper keys unregistered. The lookup `0x00443EA0` does not compare
the group with the group count, so a Lua group above 7 addresses memory past
the record array and its result is undefined. Returning nil for such a group
is a consumer choice, not client behavior.

The tables give the native key, the Lua key, the name, the type, the range
words and the default of each registered record. The number in parentheses
is the default that group 4 takes in the low spec case below.

### Group 0, Lua group 1

19 keys: chat window, macro, lock and targeting options.

The defaults of the 19 keys, in key order, are
`0, 0, 1, 1, 1, 3, 7, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1`.

| Key | Lua key | Name | Min | Max | Default |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 1 | `nohide_action` | 0 | 1 | 0 |
| 1 | 2 | `nohide_macro` | 0 | 1 | 0 |
| 2 | 3 | `macro_lines` | 1 | 3 | 1 |
| 3 | 4 | `auto_lock` | 0 | 1 | 1 |
| 4 | 5 | `npc_lock` | 0 | 1 | 1 |
| 5 | 6 | `logwin_trans1` | 0 | 10 | 3 |
| 6 | 7 | `logwin_trans2` | 0 | 10 | 7 |
| 7 | 8 | `target_cursor` | 0 | 1 | 0 |
| 8 | 9 | `item_sort` | 0 | 4 | 0 |
| 9 | 10 | `input_mode` | 0 | 1 | 0 |
| 10 | 11 | `hide_head` | 0 | 1 | 1 |
| 11 | 12 | `hide_log_sec` | 0 | 255 | 0 |
| 12 | 13 | `target_type` | 0 | 2 | 0 |
| 13 | 14 | `target_lockon` | 0 | 1 | 0 |
| 14 | 15 | `action_cancel` | 0 | 1 | 0 |
| 15 | 16 | `hide_log_sec2` | 0 | 255 | 0 |
| 16 | 17 | `logwin_opti1` | 0 | 10 | 0 |
| 17 | 18 | `logwin_opti2` | 0 | 10 | 0 |
| 18 | 19 | `log_weapon_skill` | 0 | 1 | 1 |

### Group 1, Lua group 2

32 keys: chat log channel colors.

`widget/logcolorsettingwidget` and `widget/logwidget` pass this group
with a key computed from a log channel. The values are 24-bit color words and
this page does not trace their byte order.

| Key | Lua key | Name | Min | Max | Default |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 1 | `log_color01` | 0x000000 | 0xFFFFFF | 0xFFFFFF |
| 1 | 2 | `log_color02` | 0x000000 | 0xFFFFFF | 0xFFA666 |
| 2 | 3 | `log_color03` | 0x000000 | 0xFFFFFF | 0xFF8CC6 |
| 3 | 4 | `log_color04` | 0x000000 | 0xFFFFFF | 0x66E6FF |
| 4 | 5 | `log_color05` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 5 | 6 | `log_color06` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 6 | 7 | `log_color07` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 7 | 8 | `log_color08` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 8 | 9 | `log_color09` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 9 | 10 | `log_color10` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 10 | 11 | `log_color11` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 11 | 12 | `log_color12` | 0x000000 | 0xFFFFFF | 0xD4FF7F |
| 12 | 13 | `logcolor13` | 0x000000 | 0xFFFFFF | 0x745BA6 |
| 13 | 14 | `logcolor14` | 0x000000 | 0xFFFFFF | 0xA65B80 |
| 14 | 15 | `logcolor15` | 0x000000 | 0xFFFFFF | 0xF3F3F3 |
| 15 | 16 | `logcolor16` | 0x000000 | 0xFFFFFF | 0x878787 |
| 16 | 17 | `logcolor17` | 0x000000 | 0xFFFFFF | 0xA6904B |
| 17 | 18 | `logcolor18` | 0x000000 | 0xFFFFFF | 0xA65353 |
| 18 | 19 | `logcolor19` | 0x000000 | 0xFFFFFF | 0xA6904B |
| 19 | 20 | `logcolor20` | 0x000000 | 0xFFFFFF | 0xA65353 |
| 20 | 21 | `logcolor21` | 0x000000 | 0xFFFFFF | 0xA6904B |
| 21 | 22 | `logcolor22` | 0x000000 | 0xFFFFFF | 0xA6904B |
| 22 | 23 | `logcolor23` | 0x000000 | 0xFFFFFF | 0x4295A6 |
| 23 | 24 | `logcolor24` | 0x000000 | 0xFFFFFF | 0x4295A6 |
| 24 | 25 | `logcolor25` | 0x000000 | 0xFFFFFF | 0x4295A6 |
| 25 | 26 | `logcolor26` | 0x000000 | 0xFFFFFF | 0x4295A6 |
| 26 | 27 | `logcolor27` | 0x000000 | 0xFFFFFF | 0x878787 |
| 27 | 28 | `logcolor28` | 0x000000 | 0xFFFFFF | 0x878787 |
| 28 | 29 | `logcolor29` | 0x000000 | 0xFFFFFF | 0x878787 |
| 29 | 30 | `logcolor30` | 0x000000 | 0xFFFFFF | 0x878787 |
| 30 | 31 | `logcolor31` | 0x000000 | 0xFFFFFF | 0x878787 |
| 31 | 32 | `logcolor32` | 0x000000 | 0xFFFFFF | 0x878787 |

### Group 2, Lua group 3

31 keys: camera, name plate, key config, search sort and log font options.

| Key | Lua key | Name | Type | Min | Max | Default |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 0 | 1 | `cam_fp_vertical` | int | 0 | 1 | 1 |
| 1 | 2 | `cam_fp_horizontal` | int | 0 | 1 | 1 |
| 2 | 3 | `cam_tp_vertical` | int | 0 | 1 | 1 |
| 3 | 4 | `cam_tp_horizontal` | int | 0 | 1 | 1 |
| 4 | 5 | `cam_tp_fov` | int | 12 | 28 | 18 |
| 5 | 6 | `damage_plate` | int | 0 | 1 | 1 |
| 6 | 7 | `name_plate` | int | 0 | 1 | 1 |
| 7 | 8 | `vulgar` | int | 0 | 1 | 1 |
| 8 | 9 | `keyconfig` | string | - | - | empty |
| 9 | 10 | `acquaintance` | string | - | - | empty |
| 10 | 11 | `mouse_focus` | int | 0 | 1 | 0 |
| 11 | 12 | `cam_tp_offset` | int | 0 | 12 | 4 |
| 12 | 13 | `item_search_sort` | string | - | - | empty |
| 13 | 14 | `pc_search_sort` | string | - | - | empty |
| 14 | 15 | `name_plate_hp_type` | int | 0 | 1 | 1 |
| 15 | 16 | `enemy_rank` | int | 0 | 1 | 1 |
| 16 | 17 | `active_icon` | int | 0 | 1 | 1 |
| 17 | 18 | `target_cursor_type` | int | 0 | 2 | 0 |
| 18 | 19 | `cam_def_height` | string | - | - | empty |
| 19 | 20 | `cam_def_distance` | string | - | - | empty |
| 20 | 21 | `popup_help` | int | 0 | 1 | 1 |
| 21 | 22 | `direct_target` | int | 0 | 1 | 0 |
| 22 | 23 | `hate_info` | int | 0 | 1 | 1 |
| 23 | 24 | `cam_tp_turn` | int | 50 | 200 | 100 |
| 24 | 25 | `ui_lock` | int | 0 | 1 | 0 |
| 25 | 26 | `log_se` | int | 0 | 1 | 0 |
| 26 | 27 | `log_font_size1` | int | 0 | 2 | 1 |
| 27 | 28 | `log_font_size2` | int | 0 | 2 | 1 |
| 28 | 29 | `toggle_macro` | int | 0 | 1 | 0 |
| 29 | 30 | `hate_target_mode` | int | 0 | 1 | 0 |
| 30 | 31 | `use_sub_target` | int | 0 | 1 | 1 |

### Group 3, Lua group 4

7 keys: audio volumes.

| Key | Lua key | Name | Min | Max | Default |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 1 | `music_volume` | 0 | 100 | 100 |
| 1 | 2 | `sys_volume` | 0 | 100 | 100 |
| 2 | 3 | `se_volume` | 0 | 100 | 100 |
| 3 | 4 | `dolby_iiz` | 0 | 1 | 0 |
| 4 | 5 | `voice_volume` | 0 | 100 | 100 |
| 5 | 6 | `env_sound_volume` | 0 | 100 | 100 |
| 6 | 7 | `listener_position_scale` | 0 | 80 | 0 |

### Group 4, Lua group 5

9 keys: rendering options.

Keys 0 to 5 are registered by one of two sequences. The constructor calls
`0x00443E40` with `(9, 12, 0)` on the object it received as its fourth
argument. A zero result runs the first sequence and a non-zero result jumps
to `0x004C658F`, which registers the second sequence. The object is taken to
be the system store, because the only store that registers group 9 key 12 is
the system store, where that record is `low_spec_mode` with default 0. The
second sequence defaults keys 0 to 4 to 0 and key 5 to 1. Keys 6 to 8 are
common to both. The `Default` column shows the first sequence with the
second in parentheses where they differ.

| Key | Lua key | Name | Min | Max | Default |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 1 | `chara_shadow` | 0 | 1 | 1 (0) |
| 1 | 2 | `chara_foot_effect` | 0 | 1 | 1 (0) |
| 2 | 3 | `chara_bone_physics` | 0 | 1 | 1 (0) |
| 3 | 4 | `map_far_bg` | 0 | 1 | 1 (0) |
| 4 | 5 | `map_back_side_bg` | 0 | 1 | 1 (0) |
| 5 | 6 | `map_wtr_effect` | 0 | 1 | 1 (1) |
| 6 | 7 | `map_seamless_scale` | 0 | 3 | 0 |
| 7 | 8 | `chara_balancer_max` | 0 | 256 | 40 |
| 8 | 9 | `draw_frame_rate` | 10 | 60 | 60 |

### Group 5, Lua group 6

24 keys: chat log filters, titles and enable flags.

Keys 0 to 7 are the filter strings, keys 8 to 15 the title strings and keys 16 to 23
the enable flags of eight log tabs. Four `DesktopWidget` methods of
`widget/desktopwidget_connector` pass Lua group 6 with a key computed from a
log index.

| Key | Lua key | Name | Type | Min | Max | Default |
| ---: | ---: | --- | --- | ---: | ---: | ---: |
| 0 | 1 | `log_filter1` | string | - | - | empty |
| 1 | 2 | `log_filter2` | string | - | - | empty |
| 2 | 3 | `log_filter3` | string | - | - | empty |
| 3 | 4 | `log_filter4` | string | - | - | empty |
| 4 | 5 | `log_filter5` | string | - | - | empty |
| 5 | 6 | `log_filter6` | string | - | - | empty |
| 6 | 7 | `log_filter7` | string | - | - | empty |
| 7 | 8 | `log_filter8` | string | - | - | empty |
| 8 | 9 | `log_title1` | string | - | - | empty |
| 9 | 10 | `log_title2` | string | - | - | empty |
| 10 | 11 | `log_title3` | string | - | - | empty |
| 11 | 12 | `log_title4` | string | - | - | empty |
| 12 | 13 | `log_title5` | string | - | - | empty |
| 13 | 14 | `log_title6` | string | - | - | empty |
| 14 | 15 | `log_title7` | string | - | - | empty |
| 15 | 16 | `log_title8` | string | - | - | empty |
| 16 | 17 | `log_enable1` | int | 0 | 1 | 1 |
| 17 | 18 | `log_enable2` | int | 0 | 1 | 1 |
| 18 | 19 | `log_enable3` | int | 0 | 1 | 0 |
| 19 | 20 | `log_enable4` | int | 0 | 1 | 0 |
| 20 | 21 | `log_enable5` | int | 0 | 1 | 0 |
| 21 | 22 | `log_enable6` | int | 0 | 1 | 0 |
| 22 | 23 | `log_enable7` | int | 0 | 1 | 0 |
| 23 | 24 | `log_enable8` | int | 0 | 1 | 0 |

### Group 6, Lua group 7

17 keys: name plate visibility, map alpha and camera lock limit.

| Key | Lua key | Name | Min | Max | Default |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 1 | `cam_tplock_limit` | 0 | 100 | 0 |
| 1 | 2 | `action_help` | 0 | 1 | 1 |
| 2 | 3 | `ui_map_alpha` | 0 | 100 | 80 |
| 3 | 4 | `name_plate_offset` | -30 | 30 | 0 |
| 4 | 5 | `name_plate_player_name` | 0 | 1 | 1 |
| 5 | 6 | `name_plate_player_hp` | 0 | 1 | 1 |
| 6 | 7 | `name_plate_party_name` | 0 | 1 | 1 |
| 7 | 8 | `name_plate_party_hp` | 0 | 1 | 1 |
| 8 | 9 | `name_plate_other_name` | 0 | 1 | 1 |
| 9 | 10 | `name_plate_other_hp` | 0 | 1 | 1 |
| 10 | 11 | `name_plate_npc_name` | 0 | 1 | 1 |
| 11 | 12 | `name_plate_enemy_name` | 0 | 1 | 1 |
| 12 | 13 | `name_plate_enemy_hp` | 0 | 1 | 1 |
| 13 | 14 | `name_plate_target_mouse_over` | 0 | 1 | 0 |
| 14 | 15 | `target_character_edge` | 0 | 1 | 0 |
| 15 | 16 | `name_plate_npc_hp` | 0 | 1 | 1 |
| 16 | 17 | `ui_map_alpha_new` | 0 | 100 | 80 |

## UI store

The constructor `0x004BB3D0` calls `0x004B6C60`, which loops groups 0 to 5
and slots 1 to 8 and registers four int records per slot through
`0x00443CF0`. The name is `ui_%d_%d_` (literal `0x00F9085C`) formatted with
the group plus 1 and the slot, followed by one of the literals `x`, `y`, `w`
and `h`. Key `4 * (slot - 1) + n` takes the part `x`, `y`, `w` or `h` for `n`
0 to 3. Every record has range -10000 to 10000 and default -1, which makes
192 records. The natives of the desktop contracts do not address this store.

## System store

The constructor `0x004B8640` registers 139 records in 10 groups. The values
are constructor defaults, not those of an installation, and the manifest
lists every row. Range words and defaults are 32-bit words printed as signed
values. `debuginfo_mode` therefore has max `0xFFFFFFFF` (-1) and
`view_clear_color` has default `0xAAAAAAAA` (-1431655766), above its max
`0x00FFFFFF`.

| Group | Registered count | Registered keys | Contents by name |
| ---: | ---: | --- | --- |
| 0 | 32 | 0 to 31 | boot and debug switches, `excel_max_cache`, `load_region` |
| 1 | 3 | 0 to 2 | `debug_sd_config`, `debug_cut_channel`, `bootup_is_disp_extraicon` |
| 2 | 31 | 0 to 30 | `root_path`, `env_rapture_local`, `path_file`, `boot_path`, queue sizes, debug camera and load switches |
| 3 | 1 | 0 | `extra_platform` |
| 4 | 16 | 0 to 15 | `net_` queue sizes, lobby and front host, port and retry options |
| 5 | 2 | 0 to 1 | `view_queue_size`, `view_clear_color` |
| 6 | 7 | 0 to 6 | `patch_` options |
| 7 | 32 | 0 to 31 | `enable_create_` layout and background switches, clip ranges, `multisample_surface` |
| 8 | 3 | 0, 1, 8 | `platform_install_image`, `platform_install_path`, `psn_signin_required` |
| 9 | 12 | 0 to 7 and 9 to 12 | `ambient_occlusion`, `system_font_` options, `low_layout_quality`, `scene_frame_rate`, `menu_bar`, `low_spec_mode` |

## Per-character files

The game store reads and writes a file named `game` and the UI store a file
named `ui`, one pair per character id. `0x004D9980` takes the character id,
returns when it equals the current id at context `+0x1783C`, and otherwise
runs one of two branches.

- A real id calls `0x004B71F0` on the game store with the id, the literal
  `game` (`0x00F90DBC`) and flag 0, and `0x004B67E0` on the UI store with
  the literal `ui` (`0x00F90DC4`). `0x004B71F0` also keeps the id at `+0x28`
  and the name at `+0x30` for the save path. Both skip the call when the
  store already holds a file handle at `+0x1C`, and both call slot `0x0C` of
  the object at store `+0x18` with the id, the name, the store's callback
  object at `+0x10` and the flag.
- The sentinel `0xC0000000` means no character. The branch writes the UI
  store to the previous id's `ui` file, re-registers the UI records through
  `0x004B6C60`, writes the game store through `0x004C72F0`, parses the
  default snapshot with `0x004B7250`, zeroes context `+0x17838` (the result of
  `0x004D9910` that the real-id branch stores there) and runs `0x004D6A50`,
  which sets group 3 keys 0, 1, 2, 5 and 4 to 100. The common tail of
  `0x004D9980` then moves the current id at context `+0x1783C` to `+0x17840`
  and stores the new id, here the sentinel, at `+0x1783C`. Ten of the
  eleven callers of `0x004D9980` push the sentinel. The other, at
  `0x004DCC41`, pushes a handler argument.

The object at store `+0x18` is taken to be a `ResourceModule`, whose vftable
`0x01108C3C` holds `0x00C99480` at offset `0x0C` and `0x00C98E40` at offset
`0x14`. Both take the seven arguments that the callers push and call the
path builder `0x0044AC40`, and no other vftable holds them. The builder
concatenates a root string, the text of `\user\%08X\` (literal
`0x00F672E8`) formatted with the character id and the file name. It adds no
extension. The root is the process string `0x0132CC48` for flag 0 and
`0x0132CCA0` otherwise, and both are filled at run time.

When the read completes, the callback `0x004B8540` takes the buffer pointer
and byte count from the file object, calls the parser `0x004448E0` and sets
the loaded byte at `+0x15`.

### Text format

An int record is one line, `name,<TAB>min,<TAB>max,<TAB>value`, and a string
record is `name,<TAB>value`, each ending in a line feed. Writer `0x00444730`
walks the records in group and key order, emits one line per type 1 or type 2
record and skips type 0. It replaces comma with `0x02`, line feed with `0x03`
and carriage return with `0x04` in a string value. A second writer
`0x00443ED0` opens a path with mode `wt`, writes two Shift-JIS header lines
that begin with `#` and clears the dirty byte. It has no direct caller.

The parser `0x004448E0` splits the text at line feed and each line at comma,
tab and line feed.

- A line whose first byte is `#` is skipped.
- The record is found by exact name with a linear scan (`0x00444090`). A line
  that names no registered record is ignored.
- One field sets the string value to empty.
- Two fields set the string value to the second field after reversing the
  `0x02`, `0x03` and `0x04` replacement.
- Four fields set the int value to the decimal parse of the fourth field. The
  min and max fields are not read.
- Any other field count is ignored, and the line type is not compared with
  the record type.
- Lines are applied from the last to the first, so the first line of a name
  remains.

### Override order

1. The constructor registers every record with value equal to default.
2. The constructor ends by serializing those values into a default snapshot
   held at `+0x84` of the game store through `0x00444730`. `0x004B7250`
   parses the snapshot back to restore the registered values.
3. A switch to a real character id opens that character's file and, when it
   completes, overlays the values it names.
4. A switch to the sentinel saves both stores, restores the snapshot and
   resets the group 3 volumes as described above.

## Open

- The run-time contents of the root strings `0x0132CC48` and `0x0132CCA0`
  were not traced, so the directory of the per-character files is not
  recorded.
- The origin of the character id that `0x004DCC41` passes was not traced.
- The identity of the fourth constructor argument as the system store rests
  on its group 9 key 12 record.
- The load path of the system store and whether `config.sys` is its file
  were not traced.
- The constructor at `0x00860A70` registers a character record in a
  `Config` store with `version` and `appearancetype_` keys. It is not a
  user config store and its rows are not recorded.
- The consumers of each key name were not traced, and whether a widget script
  clamps a value to its range was not traced.

## Reproduction

Authenticate the program with
[`VerifyProgramFileBytes.java`](../ghidra/VerifyProgramFileBytes.java) using
the procedure in [`ghidra/README.md`](../ghidra/README.md#verifyprogramfilebytesjava).
With explicit project and JDK bindings and a new absolute output path, use:

```powershell
tools/ghidra/run-headless.ps1 -Script DumpVAs.java -ReadOnly `
    -ScriptPath @('ghidra') -Out $Output `
    -ScriptEnv @{ XIVL_TARGET_VAS = $Addresses }
```

| Observation | Function VAs for `$Addresses` |
| --- | --- |
| Constructors | `0x004C4750,0x004BB3D0,0x004B8640,0x004B66F0,0x00444150,0x004B6C60` |
| Registrars and accessors | `0x00443CF0,0x00443D50,0x00443E40,0x00443DD0,0x00444110,0x0075C980,0x0075C9C0` |
| Text format | `0x00444730,0x00443ED0,0x004448E0,0x00444090,0x004C71A0,0x004C72F0` |
| Files | `0x004D9980,0x004B71F0,0x004B67E0,0x004B8540,0x004B7250,0x0044AC40,0x00C99480,0x00C98E40,0x004D6A50` |

The decoded registration rows are read from the call sites listed in the
`site` field of each manifest row. No decompiled body is a tracked evidence
dependency.
