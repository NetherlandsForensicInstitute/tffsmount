import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from tffsmount.mount import mount
from tffsmount.logger import setup_logging


LOGGER = logging.getLogger("tffsmount")


def main(args):
    LOGGER.info(f"Mounting image {args.image} on mount point {args.mount_point}")
    mount(args.image, args.mount_point, args.offset)
    LOGGER.info(f"Unmounting image {args.image} from mount point {args.mount_point}")


if __name__ == "__main__":
    parser = ArgumentParser(prog="tffsmount")
    parser.add_argument("image", type=Path, help="Path to image containing tffs file system")
    parser.add_argument("mount_point", type=Path, help="Path to mount point")
    parser.add_argument("-o", "--offset", type=lambda x: int(x, 0), help="Offset of tffs partition in image", default=0)
    args = parser.parse_args()

    setup_logging(LOGGER, loglevel=logging.DEBUG)

    if not args.image.exists():
        LOGGER.info(f"Image file {args.image} not found, exiting.")
        sys.exit(-1)

    if not args.mount_point.exists():
        LOGGER.info(f"Mount point {args.mount_point} not found, exiting.")
        sys.exit(-2)

    main(args)
