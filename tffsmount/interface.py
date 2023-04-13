import crcengine
from pathlib import Path
from tffsmount.parser import Parser
from functools import lru_cache
import logging

from tffsmount.stream import Stream

LOGGER = logging.getLogger(__name__)
CRC = crcengine.create(poly=0x1EDC6F41, width=32, seed=0, ref_in=True, ref_out=True, name="tffs-crc32c", xor_out=0)


def hash(init_val, data):
    val = init_val
    for d in data:
        val = (val ^ d) * 0x1000193
        val = val & 0xFFFFFFFF
    return val


def name_hash(name):
    val = hash(0x8E113957, name.encode("utf-8"))
    return (val >> 0x10) ^ (val & 0xFFFF)


class TFFS:
    def __init__(self, stream: Stream):
        self.stream = stream
        self.parser = Parser(self.stream)
        boot: Parser.Bootsector = self.parser.boot
        assert boot.root.in_use, "Invalid root dir/volume label"
        self.root: Parser.Direntry = boot.root.entry
        assert self.root.inode_number == 2, "Invalid root_dir/volume_label inode number"

        # set up indirect inode lookup
        tffs_indirect_inodes = self.get_dir_entry_from_path(Path("/$TFFS_Indirect_Inodes"), resolve_indirect=False)
        self.indirect_inodes = {
            entry.inode_number: entry for entry in self.read_dir(tffs_indirect_inodes, check_name_hash=False)
        }  # Name hashes are not populated in the $TFFS_Indirect_Inodes direntries

    def read_dir(self, dir_entry: Parser.Direntry, check_name_hash=True):
        assert dir_entry.is_dir, "Directory entry is not a directory"
        # up to last one due to the repeat-until in ksy
        for entry_set in dir_entry.first_cluster.direntry_chain.entries[:-1]:
            if not entry_set.in_use:
                continue

            # Check entry slots crc
            crc_calc = CRC(entry_set.raw)
            if entry_set.crc != crc_calc:
                raise ValueError("Invalid entry set crc")

            # Check name hash
            name_hash_calc = name_hash(entry_set.entry.name)
            if check_name_hash and (name_hash_calc != entry_set.entry.name_hash):
                raise ValueError("Invalid entry name hash")
            yield entry_set.entry

    def stat(self, dir_entry: Parser.Direntry):
        return dir_entry.type.mode

    def read_file(self, dir_entry: Parser.Direntry):
        assert not dir_entry.type.is_dir, "Directory entry is not a file"
        if dir_entry.size == 0:
            # accessing the cluster chain will result in IndexError with 0xffffffff as first cluster number
            return b""
        return dir_entry.first_cluster.data_chain[: dir_entry.size]

    @lru_cache(maxsize=4096)
    def get_dir_entry_from_path(self, path: Path, resolve_indirect=True) -> Parser.Direntry:
        if not path.name:
            return self.root
        parent_entry = self.get_dir_entry_from_path(path.parent)
        for entry in self.read_dir(parent_entry):
            if entry.name == path.name:
                if resolve_indirect and entry.is_indirect and entry.inode_number in self.indirect_inodes:
                    return self.indirect_inodes[entry.inode_number]
                return entry
