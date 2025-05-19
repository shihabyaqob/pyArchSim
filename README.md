# pyArchSim

***pyArchSim** is a cycle-accurate, five-stage MIPS pipeline simulator designed for educational and research purposes. This Python-based framework enables detailed exploration of microarchitectural concepts, including pipeline hazards, cache hierarchies, and memory latency effects.
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

**Examples**: 
   ```bash
   # 1) No caches at all
   ./pasim test.asm --linetrace --icache none        --dcache none
   
   # 2) Only I-cache direct-mapped
   ./pasim test.asm --linetrace --icache dm:1024:16  --dcache none
   
   # 3) Only D-cache direct-mapped
   ./pasim test.asm --linetrace --icache none        --dcache dm:1024:16
   
   # 4) Both caches direct-mapped
   ./pasim test.asm --linetrace --icache dm:1024:16  --dcache dm:1024:16
   
   # 5) Only I-cache 4-way set-associative
   ./pasim test.asm --linetrace --icache sa:2048:4:32 --dcache none
   
   # 6) Only D-cache 4-way set-associative
   ./pasim test.asm --linetrace --icache none        --dcache sa:2048:4:32
   
   # 7) Both caches set-associative
   ./pasim test.asm --linetrace --icache sa:2048:4:32 --dcache sa:2048:4:32
   
   # 8) Mixed: I-cache DM, D-cache SA
   ./pasim test.asm --linetrace --icache dm:16384:64 --dcache sa:8192:4:64
   
   # 9) Mixed: I-cache SA, D-cache DM
   ./pasim test.asm --linetrace --icache sa:8192:2:32  --dcache dm:8192:32

   ```
---
## Cache Configuration

* **Direct-Mapped** (`dm`) format:  e.g. `dm:8192:64` for an 8 KB cache with 64 B lines.
* **Set-Associative** (`sa`) format:  e.g. `sa:16384:4:32` for a 16 KB, 4-way cache with 32 B lines.
* **Miss Penalty**: Adjust the constant `MISS_PENALTY` at the top of `direct_mapped.py` and `set_associative.py` to simulate additional memory latency (default: 10 cycles).
---
## Testing

A synthetic workload (`test.asm`) is provided to stress cache behavior:

