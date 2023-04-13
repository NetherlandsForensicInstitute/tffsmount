import errno
import logging
from pathlib import Path
from typing import Dict

from fuse import FUSE, FuseOSError, Operations

from tffsmount.interface import TFFS
from tffsmount.stream import Stream

LOGGER = logging.getLogger(__name__)


class FuseTFFS(Operations):
    """Fuse implementation of the TFFS file system."""

    def __init__(self, stream: Stream):
        self.tffs = TFFS(stream)

    def getattr(self, path, fh=None):
        LOGGER.debug(f"getattr({path})")
        path = Path(path)

        dir_entry = self.tffs.get_dir_entry_from_path(path)
        if dir_entry:
            # LOGGER.debug(f"{stat.filemode(dir_entry.type.mode)} {dir_entry.zero=} {dir_entry.unknown_random=}")
            result = dict(
                st_size=dir_entry.size,
                st_nlink=1,
                st_mode=self.tffs.stat(dir_entry),
                st_ctime=dir_entry.ctime_s,
                st_mtime=dir_entry.mtime_s,
                st_atime=dir_entry.atime_s,
                st_uid=dir_entry.uid,
                st_gid=dir_entry.gid,
            )
            return result
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        LOGGER.debug(f"readdir({path})")
        path = Path(path)

        dir_entry = self.tffs.get_dir_entry_from_path(path)
        for entry in self.tffs.read_dir(dir_entry):
            if entry.name and not (entry.name == "$TFFS_Indirect_Inodes" or entry.inode_number == 2):
                yield entry.name

    def read(self, path, size, offset, fh):
        LOGGER.debug(f"read({path}, {size}, {offset})")
        path = Path(path)
        dir_entry = self.tffs.get_dir_entry_from_path(path)
        return self.tffs.read_file(dir_entry)[offset : offset + size]

    def readlink(self, path):
        LOGGER.debug(f"readlink({path})")
        path = Path(path)
        dir_entry = self.tffs.get_dir_entry_from_path(path)
        if not dir_entry:
            raise FuseOSError(errno.ENOENT)
        return self.tffs.read_file(dir_entry)[4:].decode("utf8")


def mount(image, mount_point, offset):
    with Stream(image, offset) as stream:
        tffs = FuseTFFS(stream)
        FUSE(tffs, str(mount_point), nothreads=True, foreground=True)
