from pathlib import Path
from stat import S_ISDIR, S_ISLNK, S_ISREG, S_ISFIFO, S_ISCHR, S_ISBLK
from tffsmount.interface import TFFS
from tffsmount.stream import Stream
import tarfile

TEST_DATA = Path(__file__).parent / "test_data"


def test_image():
    compare_parsing_of_image_with_tar(TEST_DATA / "test_image.bin", TEST_DATA / "test_image.tar.gz")


def compare_parsing_of_image_with_tar(image_path, tar_path):
    with Stream(image_path) as stream, tarfile.open(tar_path) as tffs_tar:
        tffs_image = TFFS(stream)
        for member in tffs_tar.getmembers():
            dir_entry = tffs_image.get_dir_entry_from_path(Path(member.name))

            assert_inode_contents_equal(member, tffs_image, dir_entry)
            if member.isreg():  # for regular files check if contents equal
                assert tffs_tar.extractfile(member).read() == tffs_image.read_file(dir_entry)


def assert_inode_contents_equal(tar_inode, tffs, dir_entry):
    assert tar_inode.uid == dir_entry.uid
    assert tar_inode.gid == dir_entry.gid
    assert tar_inode.mtime == dir_entry.mtime_s
    mode = tffs.stat(dir_entry)
    assert tar_inode.isdir() == S_ISDIR(mode)
    assert tar_inode.issym() == S_ISLNK(mode)
    assert tar_inode.isreg() == S_ISREG(mode)
    assert tar_inode.isfifo() == S_ISFIFO(mode)
    assert tar_inode.isblk() == S_ISBLK(mode)
    assert tar_inode.ischr() == S_ISCHR(mode)
    """
    Mode bits are saved differently in tar files than in regular inodes.
    The permission, setuid, setgid and reserved bits are masked when the mode is saved to tar.
    The other bits (such as whether the file is a directory) are saved elsewhere.
    Directly comparing the modes would therefore result in an assertion error.
    To account for this the mode bits are masked with 0o7777.
    For more info on how tar saves mode bits see https://www.gnu.org/software/tar/manual/html_node/Standard.html
    """
    assert tar_inode.mode & 0o7777 == mode & 0o7777  # permissions, setuid, setgid, reserved bit
