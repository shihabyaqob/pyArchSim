# =============================================================================
# File: five_stage_proc.py
# Author: Khalid Al-Hawaj ,19 May 2025
# Modified by: Shihab Hasan , 21 May 2025
#
# Description:
#   Defines the FiveStageInorderProcessor which wraps the
#   five-stage pipeline core.  Manages program counter, register file,
#   syscall handling, ROI markers, and collects global and ROI statistics.
#   Hooks in instruction and data caches and the multiported memory interface.
# =============================================================================

import random

from pyArchSimLib.proc.core import FiveStageInorderCore
from pyArchSimLib.mem.cache import NoCache

class FiveStageInorderProcessor():
    def __init__(self, icache=None, dcache=None):
        # Core pipeline slice
        self.core = FiveStageInorderCore()

        # Caches (injected or default to no-cache)
        self.icache = icache if icache else NoCache(0)
        self.dcache = dcache if dcache else NoCache(1)

        # Memory interface hooks for syscalls (set by system)
        self.MemReadFunct  = None
        self.MemWriteFunct = None

        # Connect instruction‐fetch to I-cache
        self.core.setIMemCanReq   (self.icache.canReq)
        self.core.setIMemSendReq  (self.icache.sendReq)
        self.core.setIMemHasResp  (self.icache.hasResp)
        self.core.setIMemRecvResp (self.icache.recvResp)

        # Connect data‐access to D-cache
        self.core.setDMemCanReq   (self.dcache.canReq)
        self.core.setDMemSendReq  (self.dcache.sendReq)
        self.core.setDMemHasResp  (self.dcache.hasResp)
        self.core.setDMemRecvResp (self.dcache.recvResp)

    # Allow the top‐level system to install the read/write functions
    def setMemReadFunc(self, MemReadFunct):
        self.MemReadFunct = MemReadFunct
        self.core.setMemReadFunct(MemReadFunct)

    def setMemWriteFunc(self, MemWriteFunct):
        self.MemWriteFunct = MemWriteFunct
        self.core.setMemWriteFunct(MemWriteFunct)

    # Forward the multi‐ported memory interface down to both caches
    def setMemCanReq(self, MemCanReq):
        self.MemCanReq = MemCanReq
        self.icache.setMemCanReq(MemCanReq)
        self.dcache.setMemCanReq(MemCanReq)

    def setMemSendReq(self, MemSendReq):
        self.MemSendReq = MemSendReq
        self.icache.setMemSendReq(MemSendReq)
        self.dcache.setMemSendReq(MemSendReq)

    def setMemHasResp(self, MemHasResp):
        self.MemHasResp = MemHasResp
        self.icache.setMemHasResp(MemHasResp)
        self.dcache.setMemHasResp(MemHasResp)

    def setMemRecvResp(self, MemRecvResp):
        self.MemRecvResp = MemRecvResp
        self.icache.setMemRecvResp(MemRecvResp)
        self.dcache.setMemRecvResp(MemRecvResp)

    # Expose ROI and completion flags
    def roiFlag(self):
        return self.core.roiFlag()

    def instCompletionFlag(self):
        return self.core.instCompletionFlag()

    # Exit status from the pipeline (syscall return)
    def getExitStatus(self):
        return self.core.getExitStatus()

    # Advance one cycle: first core, then both caches
    def tick(self):
        self.core.tick()
        self.icache.tick()
        self.dcache.tick()

    # Produce a combined trace: core trace plus cache hit/miss markers
    def linetrace(self):
        core_lt   = self.core.linetrace()
        icache_lt = self.icache.linetrace()
        dcache_lt = self.dcache.linetrace()

        lt_buf = core_lt
        if icache_lt:
            lt_buf += ' | ' + icache_lt
        if dcache_lt:
            lt_buf += ' | ' + dcache_lt

        return lt_buf
