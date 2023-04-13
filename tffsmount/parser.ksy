meta:
  id: parser
  title: tffs_parser
  file-extension: tffs
  endian: le
  xref:
    headers: https://www.sciencedirect.com/science/article/pii/S266628172300001X

seq:
  - id: boot
    type: bootsector
    size: 0x200

types:
  bootsector:
    seq:
      - id: jmp
        contents: [0xeb, 0x7e, 0x90]
      - id: magic
        contents: 'TFFS    '
      - id: zeros_bios_param_block
        size: 0x35
      - id: reserved1
        size: 1
      - id: bytes_per_sector_shift
        type: u1
      - id: sectors_per_cluster_shift
        type: u1
      - id: bits_per_cam_entry
        type: u1
        doc: 'This is tied directly to the datatype of cam entries. Should reconsider when encountering larger than 32'
      - id: reverved2
        size: 4
      - id: num_reserved_sectors
        type: u4
      - id: num_reserved_plus_cam_sectors
        type: u4
      - id: total_sector_count
        type: u8
      - id: num_cam_entries
        type: u8
      - id: root_dirent_offset
        type: u8
      - id: backup_boot_sector_number
        type: u4
      - id: unknown
        size: 0x190
      - id: crc
        type: u4
    instances:
      sector_size:
        value: 1<<bytes_per_sector_shift
      cluster_size:
        value: (1<<sectors_per_cluster_shift) * sector_size
      backup_bootsector:
        io: _root._io
        pos: backup_boot_sector_number * sector_size
        size: 512
        type: bootsector
      num_cam_sectors:
        value: num_reserved_plus_cam_sectors - num_reserved_sectors
      cam:
        io: _root._io
        pos: num_reserved_sectors * sector_size
        size: num_cam_sectors * sector_size
        type: cam_entries
      data_start:
        value: num_reserved_plus_cam_sectors * sector_size
      root:
        io: _root._io
        pos: root_dirent_offset
        type: direntry_set
  direntry:
    seq:
      - id: name_length
        type: u1
      - id: name_hash
        type: u2
      - id: type
        type: dirent_type
      - id: inode_number
        type: u8
      - id: key1
        type: u4
      - id: key2
        type: u4
      - id: uid
        type: u4
      - id: gid
        type: u4
      - id: size
        type: u8
      - id: cluster_count # Zero for directory
        type: u4
      - id: first_cluster_number
        type: u4
      - id: extended_flags
        type: extended_flags
      - id: first_extended_attr_cluster # TODO: This probably leads to fscrypto key_ref
        type: u4
      - id: zero
        type: u4
      - id: atime_ns
        type: u4
      - id: mtime_ns
        type: u4
      - id: ctime_ns
        type: u4
      - id: atime_s # or ctime?
        type: u8
      - id: mtime_s
        type: u8
      - id: ctime_s # or atime?
        type: u8
      - id: name
        size: name_length
        type: strz
        encoding: 'utf-8'
    instances:
      first_cluster:
        value: _root.boot.cam.entries[first_cluster_number]
      flags:
        value: _parent.flags
      is_indirect:
        value: "(flags & 0x4000 == 0x4000) ? true : false"
      is_dir:
        value: type.is_dir

  cam_entries:
    seq:
      - id: entries
        type: cluster_number(_index)
        repeat: expr
        repeat-expr: _root.boot.num_cam_entries
  cluster_number:
    # 0xFFFFFFFF is not allocated
    # 0xFFFFFFFE is end of chain?
    # 0xFFFFFFFD also spotted in code, not sure what it means
    params:
      - id: i       # _index
        type: u4
        doc: 'see boot.bits_per_cam_entries'
    seq:
      - id: num
        type: u4
    instances:
      cluster:
        io: _root._io
        pos: _root.boot.data_start + i * _root.boot.cluster_size
        size: _root.boot.cluster_size
      # TODO: maybe handle this in a nicer way in python, implementing a stream that Kaitai can handle
      direntry_chain:
        doc: 'Used to flatten the cluster chain to a single stream in python'
        size: 0 # required to use process,
        process: tffsmount.kaitai_process.cluster_chain(i, _root.boot.cam)
        type: direntry_sets
      data_chain:
        size: 0
        process: tffsmount.kaitai_process.cluster_chain(i, _root.boot.cam)
  direntry_sets:
    seq:
      - id: entries
        type: direntry_set
        repeat: until
        repeat-until: _.num_slots == 0
  direntry_set:
    seq:
      - size: 0
        if: start_offset < 0     # trick to cache start offset in an instance: https://github.com/kaitai-io/kaitai_struct/issues/868
      - id: flags
        type: u2
      - id: num_slots
        type: u1
      - id: entry
        size: num_slots * tffs_dir_slot_size - 3
        if: num_slots > 0
        type:
          switch-on: in_use
          cases:
            true: direntry
            false: dummy_type
    instances:
      tffs_dir_slot_size:
        value: 0x20
      in_use:
        value: "(flags & 0x8000 == 0x8000) ? true : false"  # Either TFFS_FREE_ENTRY or TFFS_NEVER_USED_ENTRY
      start_offset:
        value: _io.pos
      raw:
        pos: start_offset
        size: num_slots * tffs_dir_slot_size - 4
      crc:
        doc: "calculated over 'raw': crcengine.create(poly=0x1EDC6F41, width=32, seed=0, ref_in=True, ref_out=True, name='tffs-crc32c', xor_out=0)"
        pos: start_offset + num_slots * tffs_dir_slot_size - 4
        type: u4
  dirent_type:
    seq:
      - id: mode
        type: u2
    instances:
      is_dir:
        value: "(mode & 0xf000 == 0x4000) ? true : false"
  extended_flags:
    seq:
      - id: val
        type: u4
    instances:
      is_symlink:
        value: (val & 8) == 8
  dummy_type: {}
