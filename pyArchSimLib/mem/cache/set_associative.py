# =============================================================================
# File: set_associative.py
# Author: Shihab Hasan
# Date:   2025-05-21
#
# Description:
#   Implements an N-way set-associative L1 cache with LRU replacement,
#   hit/miss counters, and configurable miss-penalty.
# =============================================================================

MISS_PENALTY = 10  # cycles of extra delay on a miss

class SetAssociativeCache:
    def __init__(self, port_id, size, ways, line_size, lower):
        self.port_id      = port_id
        self.line_sz      = line_size
        self.n_sets       = (size // line_size) // ways
        self.ways         = ways
        self.lower        = lower

        # Storage: valid/tag/data per [set][way]
        self.valid        = [[False]*ways for _ in range(self.n_sets)]
        self.tags         = [[None]*ways  for _ in range(self.n_sets)]
        self.data         = [[bytearray(line_size) for _ in range(ways)]
                              for _ in range(self.n_sets)]

        # Simple LRU: list of ways, 0 = LRU, end = MRU
        self.lru          = [[i for i in range(ways)] for _ in range(self.n_sets)]

        # State
        self.pending      = None   # (set_id, way_to_evict, tag, orig_req)
        self.resp_buf     = None
        self.penalty_rem  = 0      # cycles remaining on current miss

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
        return (self.resp_buf is None and self.penalty_rem == 0
                and self.pending is None)

    def sendReq(self, req):
        assert self.resp_buf is None and self.penalty_rem == 0 and self.pending is None
        addr    = req['addr']
        set_id  = (addr // self.line_sz) % self.n_sets
        tag_val = addr // (self.line_sz * self.n_sets)

        # Search for hit
        for way in range(self.ways):
            if self.valid[set_id][way] and self.tags[set_id][way] == tag_val:
                self.hits += 1
                off   = addr % self.line_sz
                chunk = self.data[set_id][way][off:off+req['size']]
                self.resp_buf = {
                    'op':   req['op'], 'addr': addr,
                    'data': list(chunk), 'size': req['size'],
                    'mask': req['mask'], 'tag': req['tag']
                }
                # Update LRU: move this way to MRU
                self.lru[set_id].remove(way)
                self.lru[set_id].append(way)
                return

        # Miss: start penalty
        self.misses      += 1
        self.penalty_rem = MISS_PENALTY
        # choose eviction way now but delay issuing
        evict_way        = self.lru[set_id].pop(0)
        self.pending     = (set_id, evict_way, tag_val, req)

    def hasResp(self):
        return self.resp_buf is not None

    def recvResp(self):
        resp          = self.resp_buf
        self.resp_buf = None
        return resp

    def tick(self):
        # Stall during penalty
        if self.penalty_rem > 0:
            self.penalty_rem -= 1
            return

        # After penalty, issue the lower-level fetch if not already done
        if self.pending and not hasattr(self, '_miss_issued'):
            set_id, way, tag_val, orig = self.pending
            aligned_addr = (orig['addr'] // self.line_sz) * self.line_sz
            miss_req = {
                'op':   0, 'data': [],
                'addr': aligned_addr,
                'size': self.line_sz, 'mask': None,
                'tag':  aligned_addr
            }
            self.MemSendReq(self.port_id, miss_req)
            self._miss_issued = True

        # Advance lower memory
        self.lower.tick()

        # Check for response
        if self.pending and self.MemHasResp(self.port_id):
            resp_lower        = self.MemRecvResp(self.port_id)
            set_id, way, tag_val, orig = self.pending

            # Install block
            clean = bytearray((b & 0xFF) for b in resp_lower['data'])
            self.data[set_id][way][:] = clean
            self.valid[set_id][way]   = True
            self.tags[set_id][way]    = tag_val
            self.lru[set_id].append(way)

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
            self.pending = None
            del self._miss_issued

    def linetrace(self):
        if self.resp_buf:
            return 'SA:hit '
        if self.pending or self.penalty_rem > 0:
            return 'SA:miss'
        return '       '
