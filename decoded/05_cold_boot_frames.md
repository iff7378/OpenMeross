# Cold-boot capture: decoded TuyaMCU frames
Source: captures/05_cold_boot_uart0_pins15_16.sr (module pins 15/16, URX0/UTX0, 9600 8N1)
D0 = URX0 (MCU -> module). D1 = UTX0 (module -> MCU).
Frame grammar: 55 AA | version | command | len_hi len_lo | payload[len] | checksum(sum of all preceding bytes mod 256)
Payload grammar (per-DP report, cmd 0x06/0x07): dp_id | dp_type | dp_len_hi dp_len_lo | dp_data[dp_len]

## D0 (URX0, MCU -> module): 639 bytes
[  1] ver=00 cmd=06 dp_id=0x01 dp_type=04(enum) = 0 (0x00)  raw_payload=[01 04 00 01 00] chk=10
[  2] ver=00 cmd=06 dp_id=0x02 dp_type=02(value) = 760 (0x000002F8)  raw_payload=[02 02 00 04 00 00 02 F8] chk=0F
[  3] ver=00 cmd=06 dp_id=0x03 dp_type=02(value) = 640 (0x00000280)  raw_payload=[03 02 00 04 00 00 02 80] chk=98
[  4] ver=00 cmd=06 dp_id=0x04 dp_type=04(enum) = 0 (0x00)  raw_payload=[04 04 00 01 00] chk=13
[  5] ver=00 cmd=06 dp_id=0x05 dp_type=04(enum) = 0 (0x00)  raw_payload=[05 04 00 01 00] chk=14
[  6] ver=00 cmd=06 dp_id=0x06 dp_type=02(value) = 700 (0x000002BC)  raw_payload=[06 02 00 04 00 00 02 BC] chk=D7
[  7] ver=00 cmd=06 dp_id=0x07 dp_type=02(value) = 690 (0x000002B2)  raw_payload=[07 02 00 04 00 00 02 B2] chk=CE
[  8] ver=00 cmd=06 dp_id=0x10 dp_type=02(value) = 0 (0x00000000)  raw_payload=[10 02 00 04 00 00 00 00] chk=23
[  9] ver=00 cmd=06 dp_id=0x11 dp_type=02(value) = 0 (0x00000000)  raw_payload=[11 02 00 04 00 00 00 00] chk=24
[ 10] ver=00 cmd=06 dp_id=0x13 dp_type=01(bool) = 0 (0x00)  raw_payload=[13 01 00 01 00] chk=1F
[ 11] ver=00 cmd=06 dp_id=0x15 dp_type=02(value) = 8 (0x00000008)  raw_payload=[15 02 00 04 00 00 00 08] chk=30
[ 12] ver=00 cmd=06 dp_id=0x16 dp_type=02(value) = 1 (0x00000001)  raw_payload=[16 02 00 04 00 00 00 01] chk=2A
[ 13] ver=00 cmd=06 dp_id=0x19 dp_type=04(enum) = 1 (0x01)  raw_payload=[19 04 00 01 01] chk=29
[ 14] ver=00 cmd=06 dp_id=0x1A dp_type=04(enum) = 0 (0x00)  raw_payload=[1A 04 00 01 00] chk=29
[ 15] ver=00 cmd=06 dp_id=0x1B dp_type=02(value) = 0 (0x00000000)  raw_payload=[1B 02 00 04 00 00 00 00] chk=2E
[ 16] ver=00 cmd=06 dp_id=0x1C dp_type=04(enum) = 0 (0x00)  raw_payload=[1C 04 00 01 00] chk=2B
[ 17] ver=00 cmd=06 dp_id=0x28 dp_type=02(value) = 20 (0x00000014)  raw_payload=[28 02 00 04 00 00 00 14] chk=4F
[ 18] ver=00 cmd=06 dp_id=0x29 dp_type=02(value) = 10 (0x0000000A)  raw_payload=[29 02 00 04 00 00 00 0A] chk=46
[ 19] ver=00 cmd=06 dp_id=0x2A dp_type=02(value) = 30 (0x0000001E)  raw_payload=[2A 02 00 04 00 00 00 1E] chk=5B
[ 20] ver=00 cmd=06 dp_id=0x2B dp_type=02(value) = 50 (0x00000032)  raw_payload=[2B 02 00 04 00 00 00 32] chk=70
[ 21] ver=00 cmd=06 dp_id=0x2C dp_type=02(value) = 2 (0x00000002)  raw_payload=[2C 02 00 04 00 00 00 02] chk=41
[ 22] ver=00 cmd=06 dp_id=0x2D dp_type=01(bool) = 0 (0x00)  raw_payload=[2D 01 00 01 00] chk=39
[ 23] ver=00 cmd=06 dp_id=0x2E dp_type=04(enum) = 0 (0x00)  raw_payload=[2E 04 00 01 00] chk=3D
[ 24] ver=00 cmd=06 dp_id=0x32 dp_type=02(value) = 5 (0x00000005)  raw_payload=[32 02 00 04 00 00 00 05] chk=4A
[ 25] ver=00 cmd=06 dp_id=0x33 dp_type=02(value) = 5 (0x00000005)  raw_payload=[33 02 00 04 00 00 00 05] chk=4B
[ 26] ver=00 cmd=06 dp_id=0x34 dp_type=02(value) = 350 (0x0000015E)  raw_payload=[34 02 00 04 00 00 01 5E] chk=A6
[ 27] ver=00 cmd=06 dp_id=0x35 dp_type=02(value) = 10 (0x0000000A)  raw_payload=[35 02 00 04 00 00 00 0A] chk=52
[ 28] ver=00 cmd=06 dp_id=0x36 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[36 02 00 04 00 00 00 1E] chk=67
[ 29] ver=00 cmd=06 dp_id=0x37 dp_type=01(bool) = 0 (0x00)  raw_payload=[37 01 00 01 00] chk=43
[ 30] ver=00 cmd=06 dp_id=0x38 dp_type=04(enum) = 0 (0x00)  raw_payload=[38 04 00 01 00] chk=47
[ 31] ver=00 cmd=06 dp_id=0x3C dp_type=02(value) = 400 (0x00000190)  raw_payload=[3C 02 00 04 00 00 01 90] chk=E0
[ 32] ver=00 cmd=06 dp_id=0x3D dp_type=02(value) = 40 (0x00000028)  raw_payload=[3D 02 00 04 00 00 00 28] chk=78
[ 33] ver=00 cmd=06 dp_id=0x3E dp_type=02(value) = 50 (0x00000032)  raw_payload=[3E 02 00 04 00 00 00 32] chk=83
[ 34] ver=00 cmd=06 dp_id=0x3F dp_type=02(value) = 60 (0x0000003C)  raw_payload=[3F 02 00 04 00 00 00 3C] chk=8E
[ 35] ver=00 cmd=06 dp_id=0x40 dp_type=01(bool) = 0 (0x00)  raw_payload=[40 01 00 01 00] chk=4C
[ 36] ver=00 cmd=06 dp_id=0x41 dp_type=01(bool) = 0 (0x00)  raw_payload=[41 01 00 01 00] chk=4D
[ 37] ver=00 cmd=06 dp_id=0x42 dp_type=02(value) = 2 (0x00000002)  raw_payload=[42 02 00 04 00 00 00 02] chk=57
[ 38] ver=00 cmd=06 dp_id=0x46 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[46 02 00 04 00 00 00 1E] chk=77
[ 39] ver=00 cmd=06 dp_id=0x47 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[47 02 00 04 00 00 00 1E] chk=78
[ 40] ver=00 cmd=06 dp_id=0x49 dp_type=02(value) = 0 (0x00000000)  raw_payload=[49 02 00 04 00 00 00 00] chk=5C
[ 41] ver=00 cmd=06 dp_id=0x50 dp_type=01(bool) = 0 (0x00)  raw_payload=[50 01 00 01 00] chk=5C
[ 42] ver=00 cmd=06 dp_id=0x51 dp_type=01(bool) = 0 (0x00)  raw_payload=[51 01 00 01 00] chk=5D
[ 43] ver=00 cmd=06 dp_id=0x52 dp_type=01(bool) = 0 (0x00)  raw_payload=[52 01 00 01 00] chk=5E
[ 44] ver=00 cmd=06 dp_id=0x53 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[53 02 00 04 00 00 00 1E] chk=84
[ 45] ver=00 cmd=06 dp_id=0x54 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[54 02 00 04 00 00 00 1E] chk=85
[ 46] ver=00 cmd=06 dp_id=0x55 dp_type=01(bool) = 0 (0x00)  raw_payload=[55 01 00 01 00] chk=61

## D1 (UTX0, module -> MCU): 586 bytes
  stray byte (likely frame boundary noise): 00
[  1] ver=03 cmd=07 dp_id=0x02 dp_type=02(value) = 760 (0x000002F8)  raw_payload=[02 02 00 04 00 00 02 F8] chk=13
[  2] ver=03 cmd=07 dp_id=0x10 dp_type=02(value) = 0 (0x00000000)  raw_payload=[10 02 00 04 00 00 00 00] chk=27
[  3] ver=03 cmd=07 dp_id=0x11 dp_type=02(value) = 0 (0x00000000)  raw_payload=[11 02 00 04 00 00 00 00] chk=28
[  4] ver=03 cmd=07 dp_id=0x13 dp_type=01(bool) = 0 (0x00)  raw_payload=[13 01 00 01 00] chk=23
[  5] ver=03 cmd=07 dp_id=0x15 dp_type=02(value) = 8 (0x00000008)  raw_payload=[15 02 00 04 00 00 00 08] chk=34
[  6] ver=03 cmd=07 dp_id=0x16 dp_type=02(value) = 1 (0x00000001)  raw_payload=[16 02 00 04 00 00 00 01] chk=2E
[  7] ver=03 cmd=07 dp_id=0x19 dp_type=04(enum) = 1 (0x01)  raw_payload=[19 04 00 01 01] chk=2D
[  8] ver=03 cmd=07 dp_id=0x1A dp_type=04(enum) = 0 (0x00)  raw_payload=[1A 04 00 01 00] chk=2D
[  9] ver=03 cmd=07 dp_id=0x1B dp_type=02(value) = 0 (0x00000000)  raw_payload=[1B 02 00 04 00 00 00 00] chk=32
[ 10] ver=03 cmd=07 dp_id=0x1C dp_type=04(enum) = 0 (0x00)  raw_payload=[1C 04 00 01 00] chk=2F
[ 11] ver=03 cmd=07 dp_id=0x28 dp_type=02(value) = 20 (0x00000014)  raw_payload=[28 02 00 04 00 00 00 14] chk=53
[ 12] ver=03 cmd=07 dp_id=0x29 dp_type=02(value) = 10 (0x0000000A)  raw_payload=[29 02 00 04 00 00 00 0A] chk=4A
[ 13] ver=03 cmd=07 dp_id=0x2A dp_type=02(value) = 30 (0x0000001E)  raw_payload=[2A 02 00 04 00 00 00 1E] chk=5F
[ 14] ver=03 cmd=07 dp_id=0x2B dp_type=02(value) = 50 (0x00000032)  raw_payload=[2B 02 00 04 00 00 00 32] chk=74
[ 15] ver=03 cmd=07 dp_id=0x2C dp_type=02(value) = 2 (0x00000002)  raw_payload=[2C 02 00 04 00 00 00 02] chk=45
[ 16] ver=03 cmd=07 dp_id=0x2D dp_type=01(bool) = 0 (0x00)  raw_payload=[2D 01 00 01 00] chk=3D
[ 17] ver=03 cmd=07 dp_id=0x2E dp_type=04(enum) = 0 (0x00)  raw_payload=[2E 04 00 01 00] chk=41
[ 18] ver=03 cmd=07 dp_id=0x32 dp_type=02(value) = 5 (0x00000005)  raw_payload=[32 02 00 04 00 00 00 05] chk=4E
[ 19] ver=03 cmd=07 dp_id=0x33 dp_type=02(value) = 5 (0x00000005)  raw_payload=[33 02 00 04 00 00 00 05] chk=4F
[ 20] ver=03 cmd=07 dp_id=0x34 dp_type=02(value) = 350 (0x0000015E)  raw_payload=[34 02 00 04 00 00 01 5E] chk=AA
[ 21] ver=03 cmd=07 dp_id=0x35 dp_type=02(value) = 10 (0x0000000A)  raw_payload=[35 02 00 04 00 00 00 0A] chk=56
[ 22] ver=03 cmd=07 dp_id=0x36 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[36 02 00 04 00 00 00 1E] chk=6B
[ 23] ver=03 cmd=07 dp_id=0x37 dp_type=01(bool) = 0 (0x00)  raw_payload=[37 01 00 01 00] chk=47
[ 24] ver=03 cmd=07 dp_id=0x38 dp_type=04(enum) = 0 (0x00)  raw_payload=[38 04 00 01 00] chk=4B
[ 25] ver=03 cmd=07 dp_id=0x3C dp_type=02(value) = 400 (0x00000190)  raw_payload=[3C 02 00 04 00 00 01 90] chk=E4
[ 26] ver=03 cmd=07 dp_id=0x3D dp_type=02(value) = 40 (0x00000028)  raw_payload=[3D 02 00 04 00 00 00 28] chk=7C
[ 27] ver=03 cmd=07 dp_id=0x3E dp_type=02(value) = 50 (0x00000032)  raw_payload=[3E 02 00 04 00 00 00 32] chk=87
[ 28] ver=03 cmd=07 dp_id=0x3F dp_type=02(value) = 60 (0x0000003C)  raw_payload=[3F 02 00 04 00 00 00 3C] chk=92
[ 29] ver=03 cmd=07 dp_id=0x40 dp_type=01(bool) = 0 (0x00)  raw_payload=[40 01 00 01 00] chk=50
[ 30] ver=03 cmd=07 dp_id=0x41 dp_type=01(bool) = 0 (0x00)  raw_payload=[41 01 00 01 00] chk=51
[ 31] ver=03 cmd=07 dp_id=0x42 dp_type=02(value) = 2 (0x00000002)  raw_payload=[42 02 00 04 00 00 00 02] chk=5B
[ 32] ver=03 cmd=07 dp_id=0x46 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[46 02 00 04 00 00 00 1E] chk=7B
[ 33] ver=03 cmd=07 dp_id=0x47 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[47 02 00 04 00 00 00 1E] chk=7C
[ 34] ver=03 cmd=07 dp_id=0x01 dp_type=04(enum) = 0 (0x00)  raw_payload=[01 04 00 01 00] chk=14
[ 35] ver=03 cmd=07 dp_id=0x49 dp_type=02(value) = 0 (0x00000000)  raw_payload=[49 02 00 04 00 00 00 00] chk=60
[ 36] ver=03 cmd=07 dp_id=0x50 dp_type=01(bool) = 0 (0x00)  raw_payload=[50 01 00 01 00] chk=60
[ 37] ver=03 cmd=07 dp_id=0x51 dp_type=01(bool) = 0 (0x00)  raw_payload=[51 01 00 01 00] chk=61
[ 38] ver=03 cmd=07 dp_id=0x52 dp_type=01(bool) = 0 (0x00)  raw_payload=[52 01 00 01 00] chk=62
[ 39] ver=03 cmd=07 dp_id=0x02 dp_type=02(value) = 760 (0x000002F8)  raw_payload=[02 02 00 04 00 00 02 F8] chk=13
[ 40] ver=03 cmd=07 dp_id=0x53 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[53 02 00 04 00 00 00 1E] chk=88
[ 41] ver=03 cmd=07 dp_id=0x54 dp_type=02(value) = 30 (0x0000001E)  raw_payload=[54 02 00 04 00 00 00 1E] chk=89
[ 42] ver=03 cmd=07 dp_id=0x55 dp_type=01(bool) = 0 (0x00)  raw_payload=[55 01 00 01 00] chk=65
