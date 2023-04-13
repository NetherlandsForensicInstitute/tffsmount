# TFFS Filesystem Mounter

## Project Description

This project contains code to parse and mount (read only) the TFFS filesystem found in certain Automotive systems.
Earlier we created a similar tool: [qnxmount](https://github.com/NetherlandsForensicInstitute/qnxmount) for other filesystems found in Automotive applications running the QNX OS.

Most of the initial research and reverse engineering of TFFS was done by the Digital Analysis Division of the National Forensic Service (NFS) of the Republic of Korea.
This research is documented in their [paper](https://doi.org/10.1016/j.fsidi.2023.301500) published at DFRWS 2023 and their code can be found [here](https://github.com/NFSDigital/hkmc_dvrs_filesystem_parser).

The information in the paper was augmented with some additional reverse engineering efforts of our own based on executable files found in Automotive systems.
All of this filesystem structure information combined was put in the `parser.ksy` file, which is written in the declarative binary structure language: [kaitai](https://kaitai.io/), enabling the automatic generation of parser code.
The filesystem can then be mounted using FUSE with some python glue code between the FUSE python bindings and the generated parser.

This project is only tested on Linux machines.


## Getting started
Make sure you have fuse installed:
```shell
sudo apt install fuse
```
Set up your Python virtual environment and activate it:
```shell
python3 -m venv venv
source ./venv/bin/activate
```
Install tffsmount:
```shell
pip install .
```

## Usage
General use of the module is as follows:
```shell
~ python -m tffsmount -h
usage: tffsmount [-h] [-o OFFSET] image mount_point

positional arguments:
  image                 Path to image containing tffs file system
  mount_point           Path to mount point

options:
  -h, --help            show this help message and exit
  -o OFFSET, --offset OFFSET
                        Offset of tffs partition in image
```

Note that the offset and page size can be entered in decimal, octal, binary, or hexadecimal format. For example, we can mount an image with a tffs filesystem at offset 0x1000 with:
```shell
python3 -m tffsmount -o 0x1000 /image /mountpoint
```
Using the option `-o 4096` would give the same result.

If mounting succeeds you will see the log message `"Mounting image /image on mount point /mountpoint"` appear and the process will hang. Navigate to the given mount point with another terminal session or a file browser to access the file system.

Unmounting can be done from the terminal with:
```shell
sudo umount /mountpoint
```
The logs will show show that the image was successfully unmounted and tffsmount will exit.

## Contributing and Testing
If you want develop the tool and run tests, first fork the repository. Contributions can be submitted as a merge request.

To get started clone the forked repository and create a virtual environment. Install the test dependencies.
```shell
pip install .[test]
```

The folder **tests** contains functional tests to test the parser against known input data.
To run these tests you need a file system image and an accompanying tar archive.
The tests run are functional tests that check whether the parsed data from the test image is equal to the data stored in the archive.
Default test_images are located in the folders **test_data**.
If you want to test your own image replace the files **test_image.bin** and **test_image.tar.gz** with your own.

A test image can be created by running the script `make_test_fs.sh` inside an environment where you have access to `mktffs` and the Tuxera kernel module (`tffs.ko`) loaded.
The script will create the desired files and directories which you will then need to tar as well as use dd to create a physical image.

To run the tests in this repo navigate to the main directory of the repo and run:
```shell
pytest
```
