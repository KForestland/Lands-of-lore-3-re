# CKEEP script excerpt

The first 18 directly referenced object script entries. Offsets are absolute in the original WSX. [Summary](CKEEP.md), [schema](README.md).

- index 0, `0xD036F4` — *When* object request at 0xD08DBA. *Does* set an object property through its subcommand (operand 21) (code 0x447680). *Touches* object pool 3 53.
- index 2, `0xD03700` — *When* object value 9 at 0xD08DC6. *Does* set an object property through its subcommand (operand 21) (code 0x447680). *Touches* object pool 3 1.
- index 3, `0xD03706` — *When* object value 20 at 0xD08DCC. *Does* select a settings operation (code 0x4E6A80) → select a settings operation (code 0x4E6A80) → select a settings operation (code 0x4E6A80). *Touches* runtime context.
- index 7, `0xD0371E` — *When* object value 20 at 0xD08DD2. *Does* select a settings operation (code 0x4E6A80) → select a settings operation (code 0x4E6A80) → select a settings operation (code 0x4E6A80). *Touches* runtime context.
- index 11, `0xD03736` — *When* object value 9 and guard 28 passes at 0xD08DDA. *Does* run a duration or region operation (code 0x4E66D0) → run a duration or region operation (code 0x4E66D0). *Touches* runtime context.
- index 14, `0xD0374C` — *When* object value 9 and guard 29 passes at 0xD08DE4. *Does* run a duration or region operation (code 0x4E66D0) → run a duration or region operation (code 0x4E66D0). *Touches* runtime context.
- index 17, `0xD03762` — *When* object value 9 and guard 31 passes at 0xD08DEE. *Does* run a duration or region operation (code 0x4E66D0) → run a duration or region operation (code 0x4E66D0). *Touches* runtime context.
- index 20, `0xD03778` — *When* object request at 0xD08DFA. *Does* submit a player action (code 0x447FB0) → set an object property through its subcommand (operand 2) (code 0x447680). *Touches* runtime context, object pool 3 9.
- index 23, `0xD0378A` — *When* object request at 0xD08E06. *Does* submit a player action (code 0x447FB0) → set an object property through its subcommand (operand 2) (code 0x447680). *Touches* runtime context, object pool 3 10.
- index 26, `0xD0379C` — *When* object request at 0xD08E12. *Does* submit a player action (code 0x447FB0) → set an object property through its subcommand (operand 2) (code 0x447680). *Touches* runtime context, object pool 3 11.
- index 29, `0xD037AE` — *When* object value 9 at 0xD08E1E. *Does* set an object property through its subcommand (operand 21) (code 0x447680). *Touches* object pool 3 12.
- index 31, `0xD037BA` — *When* object value 20 and guard 5299 passes at 0xD08E24. *Does* set an object property through its subcommand (operand 3) (code 0x447680). *Touches* creature 0.
- index 33, `0xD037C6` — *When* object value 9 and guard 31 passes at 0xD08E30. *Does* set an object property through its subcommand (operand 3) (code 0x447680) → pass the command to virtual slot +0xC0 (code 0x447F31) → pass the command to virtual slot +0xC0 (code 0x447F31) → pass the command to virtual slot +0xC0 (code 0x447F31). *Touches* creature 3.
- index 38, `0xD037EA` — *When* object value 9 and guard 34 passes at 0xD08E3C. *Does* set a level byte (2) (code 0x4E5BD0). *Touches* level byte 15.
- index 40, `0xD037F6` — *When* object value 9 and guard 37 passes at 0xD08E46. *Does* set a level byte (2) (code 0x4E5BD0). *Touches* level byte 16.
- index 42, `0xD03802` — *When* object value 20 and guard 36 passes at 0xD08E52. *Does* set a level byte (1) (code 0x4E5BD0) → resolve a target and submit an object setup request (code 0x4482F8). *Touches* level byte 16, runtime context.
- index 45, `0xD0383B` — *When* object value 20 and guard 38 passes at 0xD08E5C. *Does* set a level byte (5) (code 0x4E5BD0) → resolve a target and submit an object setup request (code 0x4482F8). *Touches* level byte 16, runtime context.
- index 48, `0xD03874` — *When* object value 20 and guard 33 passes at 0xD08E68. *Does* set a level byte (1) (code 0x4E5BD0) → resolve a target and submit an object setup request (code 0x4482F8). *Touches* level byte 15, runtime context.
