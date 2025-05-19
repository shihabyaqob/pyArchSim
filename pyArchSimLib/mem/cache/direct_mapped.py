# =============================================================================
# File: direct_mapped.py
# Author: Shihab Hasan
# Date:   2025-05-21
#
# Description:
#   Implements a direct‐mapped L1 cache with hit/miss counters and
#   configurable miss-penalty.
# =============================================================================

MISS_PENALTY = 10  # cycles of extra delay on a miss

class DirectMappedCache:
    def __init__(self, port_id, size, line_size, lower):
        self.port_id      = port_id
        self.line_sz      = line_size
        self.n_lines      = size // line_size
        self.lower        = lower

        # Storage
        self.valid        = [False] * self.n_lines
        self.tags         = [None]  * self.n_lines
        self.data         = [bytearray(line_size) for _ in range(self.n_lines)]

        # State
        self.pending      = None      # (idx, tag, orig_req)
        self.resp_buf     = None
        self.penalty_rem  = 0         # cycles remaining on current miss

        # Statistics
        self.hits         = 0
        self.misses       = 0

    # Hook multi-port memory interface
    def setMemCanReq(self, fn):   self.MemCanReq   = fn
    def setMemSendReq(self, fn):  self.MemSendReq  = fn
    def setMemHasResp(self, fn):  self.MemHasResp  = fn
    def setMemRecvResp(self, fn): self.MemRecvResp = fn

    # Upstream interface
    def canReq(self):
        return self.resp_buf is None and self.penalty_rem == 0 and self.pending is None

    def sendReq(self, req):
        assert self.resp_buf is None and self.penalty_rem == 0 and self.pending is None
        addr = req['addr']
        idx  = (addr // self.line_sz) % self.n_lines
        tag  = addr // (self.line_sz * self.n_lines)

        if self.valid[idx] and self.tags[idx] == tag:
            # Hit
            self.hits += 1
            off   = addr % self.line_sz
            sz    = req['size']
            chunk = self.data[idx][off:off+sz]
            self.resp_buf = {
                'op':   req['op'], 'addr': addr,
                'data': list(chunk), 'size': sz,
                'mask': req['mask'],   'tag': req['tag']
            }
        else:
            # Miss: start penalty timer
            self.misses += 1
            self.penalty_rem = MISS_PENALTY
            self.pending     = (idx, tag, req)

    def hasResp(self):
        return self.resp_buf is not None

    def recvResp(self):
        resp          = self.resp_buf
        self.resp_buf = None
        return resp

    def tick(self):
        # If we're still in the miss penalty, just count down
        if self.penalty_rem > 0:
            self.penalty_rem -= 1
            return

        # If penalty is done and we have a pending miss, issue the lower request
        if self.pending and not hasattr(self, '_miss_issued'):
            idx, tag, orig = self.pending
            addr_aligned   = (orig['addr'] // self.line_sz) * self.line_sz
            miss_req = {
                'op':   0, 'data': [],
                'addr': addr_aligned,
                'size': self.line_sz, 'mask': None,
                'tag':  addr_aligned
            }
            self.MemSendReq(self.port_id, miss_req)
            self._miss_issued = True

        # Advance the lower-level memory to potentially satisfy the miss
        self.lower.tick()

        # Check for lower‐level response
        if self.pending and self.MemHasResp(self.port_id):
            resp_lower     = self.MemRecvResp(self.port_id)
            idx, tag, orig = self.pending

            # Install line (mask to 8 bits)
            clean = bytearray((b & 0xFF) for b in resp_lower['data'])
            self.data[idx][:] = clean
            self.valid[idx]   = True
            self.tags[idx]    = tag

            # Satisfy original
            addr = orig['addr']
            off  = addr % self.line_sz
            sz   = orig['size']
            chunk = clean[off:off+sz]
            self.resp_buf = {
                'op':   orig['op'], 'addr': addr,
                'data': list(chunk), 'size': sz,
                'mask': orig['mask'],  'tag': orig['tag']
            }

            # Clear miss state
            self.pending      = None
            del self._miss_issued

    def linetrace(self):
        if self.resp_buf:
            return 'DM:hit '
        if self.pending or self.penalty_rem > 0:
            return 'DM:miss'
        return '       '
