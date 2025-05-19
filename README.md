# pyArchSim

**pyArchSim** is a cycle-accurate, five-stage MIPS pipeline simulator designed for educational and research purposes. This Python-based framework enables detailed exploration of microarchitectural concepts, including pipeline hazards, cache hierarchies, and memory latency effects.
---
## Features

* **Five-Stage Pipeline**: Implements IF, ID, EX, MEM, WB stages with hazard detection and forwarding.
* **Configurable Caches**:

  * Direct-Mapped (DM)
  * N-Way Set-Associative (SA)
  * Customizable cache size, line size, and associativity.
* **Miss Penalty Modeling**: Introduce a user-defined stall penalty on cache misses to simulate realistic memory latencies.
* **Hit/Miss Instrumentation**: Runtime counters for cache hits and misses, reported alongside IPC/CPI statistics.
* **ROI Markers**: MIPS syscalls `88`/`89` demarcate regions of interest for focused performance measurement.
* **Flexible Memory**: Multi-ported memory model with optional latency extensions.
* **Command-Line Driver (`pasim`)**:

  * Assemble and load MIPS assembly files
  * Specify caches via `--icache` and `--dcache` flags
  * Output detailed cycle‐accurate trace and summary statistics
---
## Installation

  **Clone** the repository:

   ```bash
   git clone https://github.com/shihabyaqob/pyArchSim.git
   cd pyArchSim
   ```
---
## Usage

   ```bash
   ./pasim \<assembly\_file.asm> \[options]
   ```

### Key Options

* `-l, --linetrace`               : Enable cycle-by-cycle trace output
* `-f, --linetrace-file <file>`   : Redirect trace output to a file
* `-m, --max-num-cycles <N>`      : Limit simulation to N cycles (default: 1,000,000)
* `--icache <cfg>`                : Instruction cache config: `none`, `dm:SIZE:LINE_SZ`, or `sa:SIZE:WAYS:LINE_SZ`
* `--dcache <cfg>`                : Data cache config (same format)

**Example**: 4 KB, 64 B direct-mapped I-cache and 8 KB, 4-way, 32 B SA D-cache with linetrace:
   ```bash
   ./pasim test.asm --linetrace --icache dm:4096:64 --dcache sa:8192:4:32

   ```
+----------+------------+----------+----------+----------+----------+---------+---------+-----+
|   Cycle  |    Fetch   |  Decode  | Execute  |  Memory  | Complete | I_Cache | D_Cache | Mem |
+----------+------------+----------+----------+----------+----------+---------+---------+-----+
|        0 | 0x04000000 |          |          |          |          | DM:miss |         | mem |
|        1 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        2 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        3 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        4 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        5 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        6 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        7 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        8 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|        9 | S <<<      | S mem    |          |          |          | DM:miss |         | mem |
|       10 | S <<<      | S mem    |          |          |          | DM:hit  |         | mem |
|       11 | 0x04000004 | lui      |          |          |          | DM:hit  |         | mem |
|       12 | S <<<      | S raw    | lui      |          |          |         |         | mem |
|       13 | 0x04000008 | ori      |          | lui      |          | DM:hit  |         | mem |
|       14 | S <<<      | S raw    | ori      |          | lui      |         |         | mem |
|       15 | 0x0400000c | lw       |          | ori      |          | DM:hit  |         | mem |
|       16 | 0x04000010 | lui      | lw       |          | ori      | DM:hit  | SA:miss | mem |
|       17 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       18 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       19 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       20 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       21 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       22 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       23 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       24 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       25 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       26 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:hit  | mem |
|       27 | S <<<      | S raw    | lui      | lw       |          |         |         | mem |
|       28 | 0x04000014 | ori      |          | lui      | lw       | DM:hit  |         | mem |
|       29 | 0x04000018 | lui      | ori      |          | lui      | DM:hit  |         | mem |
|       30 | S <<<      | S raw    | lui      | ori      |          |         |         | mem |
|       31 | 0x0400001c | ori      |          | lui      | ori      | DM:hit  |         | mem |
|       32 | 0x04000020 | lui      | ori      |          | lui      | DM:hit  |         | mem |
|       33 | S <<<      | S raw    | lui      | ori      |          |         |         | mem |
|       34 | 0x04000024 | ori      |          | lui      | ori      | DM:hit  |         | mem |
|       35 | 0x04000028 | addiu    | ori      |          | lui      | DM:hit  |         | mem |
|       36 | S <<<      | S        | >>       | addiu    | ori      |         |         | mem |
|       37 | S <<<      | S        | >>       |          | addiu    |         |         | mem |
|       38 | S <<<      | S        | >>       |          |          |         |         | mem |
|       39 | 0x0400002c | syscall  |          |          |          | DM:hit  |         | mem |
|       40 | S <<<      | S >>     |          | syscall  |          | DM:hit  |         | mem |
|       41 | S <<<      | S >>     |          |          | syscall  | DM:hit  |         | mem |
|       42 | S <<<      | S >>     |          |          |          | DM:hit  |         | mem |
|       43 | 0x04000030 | beq      |          |          |          | DM:hit  |         | mem |
|       44 | 0x04000034 | lw       | beq      |          |          | DM:hit  |         | mem |
|       45 | 0x04000038 | lw       | lw       | beq      |          | DM:hit  | SA:miss | mem |
|       46 | S <<<      | S <<<    | S <<<    | S dmem   | beq      | DM:hit  | SA:miss | mem |
|       47 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       48 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       49 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       50 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       51 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       52 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       53 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       54 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|       55 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:hit  | mem |
|       56 | S <<<      | S raw    | lw       | lw       |          |         | SA:miss | mem |
|       57 | S <<<      | S raw    |          | S dmem   | lw       |         | SA:miss | mem |
|       58 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       59 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       60 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       61 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       62 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       63 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       64 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       65 | S <<<      | S raw    |          | S dmem   |          |         | SA:miss | mem |
|       66 | S <<<      | S raw    |          | S dmem   |          |         | SA:hit  | mem |
|       67 | S <<<      | S raw    |          | lw       |          |         |         | mem |
|       68 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|       69 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|       70 | 0x04000040 | sw       |          | addu     |          | DM:miss |         | mem |
|       71 | S <<<      | S mem    | sw       |          | addu     | DM:miss | SA:miss | mem |
|       72 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       73 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       74 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       75 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       76 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       77 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       78 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       79 | S <<<      | S mem    |          | S dmem   |          | DM:miss | SA:miss | mem |
|       80 | S <<<      | S mem    |          | S dmem   |          | DM:hit  | SA:miss | mem |
|       81 | 0x04000044 | addiu    |          | S dmem   |          | DM:hit  | SA:hit  | mem |
|       82 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|       83 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|       84 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|       85 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|       86 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|       87 | -          | -        | bne      |          | addiu    | DM:hit  |         | mem |
|       88 | 0x04000030 | -        | -        | bne      |          | DM:hit  |         | mem |
|       89 | 0x04000034 | lw       | -        | -        | bne      | DM:hit  |         | mem |
|       90 | 0x04000038 | lw       | lw       | -        | -        | DM:hit  | SA:hit  | mem |
|       91 | S <<<      | S raw    | lw       | lw       | -        |         | SA:hit  | mem |
|       92 | S <<<      | S raw    |          | lw       | lw       |         |         | mem |
|       93 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|       94 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|       95 | 0x04000040 | sw       |          | addu     |          | DM:hit  |         | mem |
|       96 | 0x04000044 | addiu    | sw       |          | addu     | DM:hit  | SA:hit  | mem |
|       97 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|       98 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|       99 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|      100 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|      101 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|      102 | -          | -        | bne      |          | addiu    | DM:hit  |         | mem |
|      103 | 0x04000030 | -        | -        | bne      |          | DM:hit  |         | mem |
|      104 | 0x04000034 | lw       | -        | -        | bne      | DM:hit  |         | mem |
|      105 | 0x04000038 | lw       | lw       | -        | -        | DM:hit  | SA:hit  | mem |
|      106 | S <<<      | S raw    | lw       | lw       | -        |         | SA:hit  | mem |
|      107 | S <<<      | S raw    |          | lw       | lw       |         |         | mem |
|      108 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|      109 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|      110 | 0x04000040 | sw       |          | addu     |          | DM:hit  |         | mem |
|      111 | 0x04000044 | addiu    | sw       |          | addu     | DM:hit  | SA:miss | mem |
|      112 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      113 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      114 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      115 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      116 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      117 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      118 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      119 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      120 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:miss | mem |
|      121 | S <<<      | S <<<    | S <<<    | S dmem   |          | DM:hit  | SA:hit  | mem |
|      122 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|      123 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|      124 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|      125 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|      126 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|      127 | -          | -        | bne      |          | addiu    | DM:hit  |         | mem |
|      128 | 0x04000030 | -        | -        | bne      |          | DM:hit  |         | mem |
|      129 | 0x04000034 | lw       | -        | -        | bne      | DM:hit  |         | mem |
|      130 | 0x04000038 | lw       | lw       | -        | -        | DM:hit  | SA:hit  | mem |
|      131 | S <<<      | S raw    | lw       | lw       | -        |         | SA:hit  | mem |
|      132 | S <<<      | S raw    |          | lw       | lw       |         |         | mem |
|      133 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|      134 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|      135 | 0x04000040 | sw       |          | addu     |          | DM:hit  |         | mem |
|      136 | 0x04000044 | addiu    | sw       |          | addu     | DM:hit  | SA:hit  | mem |
|      137 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|      138 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|      139 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|      140 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|      141 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|      142 | -          | -        | bne      |          | addiu    | DM:hit  |         | mem |
|      143 | 0x04000030 | -        | -        | bne      |          | DM:hit  |         | mem |
|      144 | 0x04000034 | lw       | -        | -        | bne      | DM:hit  |         | mem |
|      145 | 0x04000038 | lw       | lw       | -        | -        | DM:hit  | SA:hit  | mem |
|      146 | S <<<      | S raw    | lw       | lw       | -        |         | SA:hit  | mem |
|      147 | S <<<      | S raw    |          | lw       | lw       |         |         | mem |
|      148 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|      149 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|      150 | 0x04000040 | sw       |          | addu     |          | DM:hit  |         | mem |
|      151 | 0x04000044 | addiu    | sw       |          | addu     | DM:hit  | SA:hit  | mem |
|      152 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|      153 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|      154 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|      155 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|      156 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|      157 | -          | -        | bne      |          | addiu    | DM:hit  |         | mem |
|      158 | 0x04000030 | -        | -        | bne      |          | DM:hit  |         | mem |
|      159 | 0x04000034 | lw       | -        | -        | bne      | DM:hit  |         | mem |
|      160 | 0x04000038 | lw       | lw       | -        | -        | DM:hit  | SA:hit  | mem |
|      161 | S <<<      | S raw    | lw       | lw       | -        |         | SA:hit  | mem |
|      162 | S <<<      | S raw    |          | lw       | lw       |         |         | mem |
|      163 | 0x0400003c | addu     |          |          | lw       | DM:hit  |         | mem |
|      164 | S <<<      | S raw    | addu     |          |          |         |         | mem |
|      165 | 0x04000040 | sw       |          | addu     |          | DM:hit  |         | mem |
|      166 | 0x04000044 | addiu    | sw       |          | addu     | DM:hit  | SA:hit  | mem |
|      167 | 0x04000048 | addiu    | addiu    | sw       |          | DM:hit  |         | mem |
|      168 | 0x0400004c | addiu    | addiu    | addiu    | sw       | DM:hit  |         | mem |
|      169 | 0x04000050 | addiu    | addiu    | addiu    | addiu    | DM:hit  |         | mem |
|      170 | S <<<      | S raw    | addiu    | addiu    | addiu    |         |         | mem |
|      171 | 0x04000054 | bne      |          | addiu    | addiu    | DM:hit  |         | mem |
|      172 | 0x04000058 | addiu    | bne      |          | addiu    | DM:hit  |         | mem |
|      173 | S <<<      | S        | >>       | addiu    | bne      |         |         | mem |
|      174 | S <<<      | S        | >>       |          | addiu    |         |         | mem |
|      175 | S <<<      | S        | >>       |          |          |         |         | mem |
|      176 | 0x0400005c | syscall  |          |          |          | DM:hit  |         | mem |
|      177 | S <<<      | S >>     |          | syscall  |          | DM:hit  |         | mem |
|      178 | S <<<      | S >>     |          |          | syscall  | DM:hit  |         | mem |
|      179 | S <<<      | S >>     |          |          |          | DM:hit  |         | mem |
|      180 | 0x04000060 | addiu    |          |          |          | DM:hit  |         | mem |
|      181 | S <<<      | S        | >>       | addiu    |          |         |         | mem |
|      182 | S <<<      | S        | >>       |          | addiu    |         |         | mem |
|      183 | S <<<      | S        | >>       |          |          |         |         | mem |
|      184 | 0x04000064 | syscall  |          |          |          | DM:hit  |         | mem |
|      185 | S <<<      | S >>     |          | syscall  |          | DM:hit  |         | mem |

 + Overall Total Statistics:
     - Total Cycles                  = 186
     - Total Completed Instructions  = 69
     - Average IPC                   = 0.37
     - Average CPI                   = 2.70

 + ROI Statistics:
     - ROI Cycles                    = 137
     - ROI Completed Instructions    = 57
     - ROI Average IPC               = 0.42
     - ROI Average CPI               = 2.40

 + Cache Statistics:
     - I-Cache Hits   = 79
     - I-Cache Misses = 2
     - D-Cache Hits   = 14
     - D-Cache Misses = 5
---

## Cache Configuration

* **Direct-Mapped** (`dm`) format:
  \`\`\`dm\:SIZE\:LINE\_SZ\`\`\`
  e.g. `dm:8192:64` for an 8 KB cache with 64 B lines.

* **Set-Associative** (`sa`) format:
  \`\`\`sa\:SIZE\:WAYS\:LINE\_SZ\`\`\`
  e.g. `sa:16384:4:32` for a 16 KB, 4-way cache with 32 B lines.

* **Miss Penalty**: Adjust the constant `MISS_PENALTY` at the top of `direct_mapped.py` and `set_associative.py` to simulate additional memory latency (default: 10 cycles).
---
## Testing

A synthetic workload (`test.asm`) is provided to stress cache behavior:

