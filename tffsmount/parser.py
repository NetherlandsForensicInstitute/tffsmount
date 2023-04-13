# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import tffsmount.kaitai_process


if getattr(kaitaistruct, "API_VERSION", (0, 9)) < (0, 9):
    raise Exception(
        "Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__)
    )


class Parser(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_boot = self._io.read_bytes(512)
        _io__raw_boot = KaitaiStream(BytesIO(self._raw_boot))
        self.boot = Parser.Bootsector(_io__raw_boot, self, self._root)

    class DirentrySet(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self.start_offset < 0:
                self._unnamed0 = self._io.read_bytes(0)

            self.flags = self._io.read_u2le()
            self.num_slots = self._io.read_u1()
            if self.num_slots > 0:
                _on = self.in_use
                if _on == True:
                    self._raw_entry = self._io.read_bytes(((self.num_slots * self.tffs_dir_slot_size) - 3))
                    _io__raw_entry = KaitaiStream(BytesIO(self._raw_entry))
                    self.entry = Parser.Direntry(_io__raw_entry, self, self._root)
                elif _on == False:
                    self._raw_entry = self._io.read_bytes(((self.num_slots * self.tffs_dir_slot_size) - 3))
                    _io__raw_entry = KaitaiStream(BytesIO(self._raw_entry))
                    self.entry = Parser.DummyType(_io__raw_entry, self, self._root)
                else:
                    self.entry = self._io.read_bytes(((self.num_slots * self.tffs_dir_slot_size) - 3))

        @property
        def in_use(self):
            if hasattr(self, "_m_in_use"):
                return self._m_in_use

            self._m_in_use = True if (self.flags & 32768) == 32768 else False
            return getattr(self, "_m_in_use", None)

        @property
        def tffs_dir_slot_size(self):
            if hasattr(self, "_m_tffs_dir_slot_size"):
                return self._m_tffs_dir_slot_size

            self._m_tffs_dir_slot_size = 32
            return getattr(self, "_m_tffs_dir_slot_size", None)

        @property
        def start_offset(self):
            if hasattr(self, "_m_start_offset"):
                return self._m_start_offset

            self._m_start_offset = self._io.pos()
            return getattr(self, "_m_start_offset", None)

        @property
        def raw(self):
            if hasattr(self, "_m_raw"):
                return self._m_raw

            _pos = self._io.pos()
            self._io.seek(self.start_offset)
            self._m_raw = self._io.read_bytes(((self.num_slots * self.tffs_dir_slot_size) - 4))
            self._io.seek(_pos)
            return getattr(self, "_m_raw", None)

        @property
        def crc(self):
            """calculated over 'raw': crcengine.create(poly=0x1EDC6F41, width=32, seed=0, ref_in=True, ref_out=True, name='tffs-crc32c', xor_out=0)."""
            if hasattr(self, "_m_crc"):
                return self._m_crc

            _pos = self._io.pos()
            self._io.seek(((self.start_offset + (self.num_slots * self.tffs_dir_slot_size)) - 4))
            self._m_crc = self._io.read_u4le()
            self._io.seek(_pos)
            return getattr(self, "_m_crc", None)

    class DirentrySets(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            i = 0
            while True:
                _ = Parser.DirentrySet(self._io, self, self._root)
                self.entries.append(_)
                if _.num_slots == 0:
                    break
                i += 1

    class Direntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.name_length = self._io.read_u1()
            self.name_hash = self._io.read_u2le()
            self.type = Parser.DirentType(self._io, self, self._root)
            self.inode_number = self._io.read_u8le()
            self.key1 = self._io.read_u4le()
            self.key2 = self._io.read_u4le()
            self.uid = self._io.read_u4le()
            self.gid = self._io.read_u4le()
            self.size = self._io.read_u8le()
            self.cluster_count = self._io.read_u4le()
            self.first_cluster_number = self._io.read_u4le()
            self.extended_flags = Parser.ExtendedFlags(self._io, self, self._root)
            self.first_extended_attr_cluster = self._io.read_u4le()
            self.zero = self._io.read_u4le()
            self.atime_ns = self._io.read_u4le()
            self.mtime_ns = self._io.read_u4le()
            self.ctime_ns = self._io.read_u4le()
            self.atime_s = self._io.read_u8le()
            self.mtime_s = self._io.read_u8le()
            self.ctime_s = self._io.read_u8le()
            self.name = (KaitaiStream.bytes_terminate(self._io.read_bytes(self.name_length), 0, False)).decode("utf-8")

        @property
        def first_cluster(self):
            if hasattr(self, "_m_first_cluster"):
                return self._m_first_cluster

            self._m_first_cluster = self._root.boot.cam.entries[self.first_cluster_number]
            return getattr(self, "_m_first_cluster", None)

        @property
        def flags(self):
            if hasattr(self, "_m_flags"):
                return self._m_flags

            self._m_flags = self._parent.flags
            return getattr(self, "_m_flags", None)

        @property
        def is_indirect(self):
            if hasattr(self, "_m_is_indirect"):
                return self._m_is_indirect

            self._m_is_indirect = True if (self.flags & 16384) == 16384 else False
            return getattr(self, "_m_is_indirect", None)

        @property
        def is_dir(self):
            if hasattr(self, "_m_is_dir"):
                return self._m_is_dir

            self._m_is_dir = self.type.is_dir
            return getattr(self, "_m_is_dir", None)

    class DummyType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            pass

    class CamEntries(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.entries = []
            for i in range(self._root.boot.num_cam_entries):
                self.entries.append(Parser.ClusterNumber(i, self._io, self, self._root))

    class Bootsector(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.jmp = self._io.read_bytes(3)
            if not self.jmp == b"\xEB\x7E\x90":
                raise kaitaistruct.ValidationNotEqualError(
                    b"\xEB\x7E\x90", self.jmp, self._io, "/types/bootsector/seq/0"
                )
            self.magic = self._io.read_bytes(8)
            if not self.magic == b"\x54\x46\x46\x53\x20\x20\x20\x20":
                raise kaitaistruct.ValidationNotEqualError(
                    b"\x54\x46\x46\x53\x20\x20\x20\x20", self.magic, self._io, "/types/bootsector/seq/1"
                )
            self.zeros_bios_param_block = self._io.read_bytes(53)
            self.reserved1 = self._io.read_bytes(1)
            self.bytes_per_sector_shift = self._io.read_u1()
            self.sectors_per_cluster_shift = self._io.read_u1()
            self.bits_per_cam_entry = self._io.read_u1()
            self.reverved2 = self._io.read_bytes(4)
            self.num_reserved_sectors = self._io.read_u4le()
            self.num_reserved_plus_cam_sectors = self._io.read_u4le()
            self.total_sector_count = self._io.read_u8le()
            self.num_cam_entries = self._io.read_u8le()
            self.root_dirent_offset = self._io.read_u8le()
            self.backup_boot_sector_number = self._io.read_u4le()
            self.unknown = self._io.read_bytes(400)
            self.crc = self._io.read_u4le()

        @property
        def data_start(self):
            if hasattr(self, "_m_data_start"):
                return self._m_data_start

            self._m_data_start = self.num_reserved_plus_cam_sectors * self.sector_size
            return getattr(self, "_m_data_start", None)

        @property
        def cam(self):
            if hasattr(self, "_m_cam"):
                return self._m_cam

            io = self._root._io
            _pos = io.pos()
            io.seek((self.num_reserved_sectors * self.sector_size))
            self._raw__m_cam = io.read_bytes((self.num_cam_sectors * self.sector_size))
            _io__raw__m_cam = KaitaiStream(BytesIO(self._raw__m_cam))
            self._m_cam = Parser.CamEntries(_io__raw__m_cam, self, self._root)
            io.seek(_pos)
            return getattr(self, "_m_cam", None)

        @property
        def num_cam_sectors(self):
            if hasattr(self, "_m_num_cam_sectors"):
                return self._m_num_cam_sectors

            self._m_num_cam_sectors = self.num_reserved_plus_cam_sectors - self.num_reserved_sectors
            return getattr(self, "_m_num_cam_sectors", None)

        @property
        def backup_bootsector(self):
            if hasattr(self, "_m_backup_bootsector"):
                return self._m_backup_bootsector

            io = self._root._io
            _pos = io.pos()
            io.seek((self.backup_boot_sector_number * self.sector_size))
            self._raw__m_backup_bootsector = io.read_bytes(512)
            _io__raw__m_backup_bootsector = KaitaiStream(BytesIO(self._raw__m_backup_bootsector))
            self._m_backup_bootsector = Parser.Bootsector(_io__raw__m_backup_bootsector, self, self._root)
            io.seek(_pos)
            return getattr(self, "_m_backup_bootsector", None)

        @property
        def sector_size(self):
            if hasattr(self, "_m_sector_size"):
                return self._m_sector_size

            self._m_sector_size = 1 << self.bytes_per_sector_shift
            return getattr(self, "_m_sector_size", None)

        @property
        def root(self):
            if hasattr(self, "_m_root"):
                return self._m_root

            io = self._root._io
            _pos = io.pos()
            io.seek(self.root_dirent_offset)
            self._m_root = Parser.DirentrySet(io, self, self._root)
            io.seek(_pos)
            return getattr(self, "_m_root", None)

        @property
        def cluster_size(self):
            if hasattr(self, "_m_cluster_size"):
                return self._m_cluster_size

            self._m_cluster_size = (1 << self.sectors_per_cluster_shift) * self.sector_size
            return getattr(self, "_m_cluster_size", None)

    class ExtendedFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.val = self._io.read_u4le()

        @property
        def is_symlink(self):
            if hasattr(self, "_m_is_symlink"):
                return self._m_is_symlink

            self._m_is_symlink = (self.val & 8) == 8
            return getattr(self, "_m_is_symlink", None)

    class DirentType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = self._io.read_u2le()

        @property
        def is_dir(self):
            if hasattr(self, "_m_is_dir"):
                return self._m_is_dir

            self._m_is_dir = True if (self.mode & 61440) == 16384 else False
            return getattr(self, "_m_is_dir", None)

    class ClusterNumber(KaitaiStruct):
        def __init__(self, i, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.i = i
            self._read()

        def _read(self):
            self.num = self._io.read_u4le()

        @property
        def cluster(self):
            if hasattr(self, "_m_cluster"):
                return self._m_cluster

            io = self._root._io
            _pos = io.pos()
            io.seek((self._root.boot.data_start + (self.i * self._root.boot.cluster_size)))
            self._m_cluster = io.read_bytes(self._root.boot.cluster_size)
            io.seek(_pos)
            return getattr(self, "_m_cluster", None)

        @property
        def direntry_chain(self):
            """Used to flatten the cluster chain to a single stream in python."""
            if hasattr(self, "_m_direntry_chain"):
                return self._m_direntry_chain

            self._raw__raw__m_direntry_chain = self._io.read_bytes(0)
            _process = tffsmount.kaitai_process.ClusterChain(self.i, self._root.boot.cam)
            self._raw__m_direntry_chain = _process.decode(self._raw__raw__m_direntry_chain)
            _io__raw__m_direntry_chain = KaitaiStream(BytesIO(self._raw__m_direntry_chain))
            self._m_direntry_chain = Parser.DirentrySets(_io__raw__m_direntry_chain, self, self._root)
            return getattr(self, "_m_direntry_chain", None)

        @property
        def data_chain(self):
            if hasattr(self, "_m_data_chain"):
                return self._m_data_chain

            self._raw__m_data_chain = self._io.read_bytes(0)
            _process = tffsmount.kaitai_process.ClusterChain(self.i, self._root.boot.cam)
            self._m_data_chain = _process.decode(self._raw__m_data_chain)
            return getattr(self, "_m_data_chain", None)
