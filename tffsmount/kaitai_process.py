class ClusterChain:
    def __init__(self, idx, cam):
        self.idx = idx
        self.cam = cam

    def get_chain(self):
        num = self.cam.entries[self.idx].num
        # 0xFFFFFFFF is not allocated
        # 0xFFFFFFFE is end of chain?
        # 0xFFFFFFFD also spotted in code, not sure what it means
        while num < 0xFFFFFFFD:
            cluster = self.cam.entries[self.idx].cluster
            yield cluster
            self.idx = num
            num = self.cam.entries[self.idx].num
        cluster = self.cam.entries[self.idx].cluster
        yield cluster

    def decode(self, data):
        # This function actually gets called by the Kaitai parser with 'data' being the input (sub-)stream
        return b"".join(self.get_chain())
