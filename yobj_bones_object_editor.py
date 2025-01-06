import struct
import sys
import os

bones=[]
bones_offset=[]
bones_name=[]
bones_parrent=[]
read_bones_offset=0
bones_count=0

header_object_offset=0
object_count=0
object_offset=[]
header_bones_offset=[]

object_bones_offset=[]
object_bones=[]

def read_bones(f):
    global bones_count, read_bones_offset
    f.seek(28)
    bones_count=struct.unpack('<i', f.read(4))[0]
    print(f"bones count: {bones_count}")
    f.seek(40)
    read_bones_offset=struct.unpack('<i', f.read(4))[0]
    print(f"bones offset: {read_bones_offset+8}")
    f.seek(read_bones_offset+8)
    for i in range(bones_count):
        offset=f.tell()
        bones_offset.append(offset)
        pointer = f.read(16).decode('ascii')
        bones_name.append(pointer)
        f.read(32)
        pointer = struct.unpack('<i', f.read(4))[0]
        bones_parrent.append(pointer)
        f.seek(-52, 1)
        pointer = f.read(80)
        bones.append(pointer)
        pass
    pass
def read_object(f):
    global header_object_offset, object_count
    f.seek(24)
    object_count=struct.unpack('<i', f.read(4))[0]
    print(f"Object Count: {object_count}")
    f.seek(36)
    header_object_offset=struct.unpack('<i', f.read(4))[0]
    print(f"Object Offset: {header_object_offset+8}")
    f.seek(header_object_offset+8)
    for i in range(object_count):
        offset=f.tell()
        object_offset.append(offset)
        f.read(8)
        b_header=struct.unpack('<i', f.read(4))[0]
        header_bones_offset.append(b_header)
        print(f"Object {i}, Offset {offset}, Bones Header Offset {b_header}")
        f.read(52)
        pass
    pass
def read_object_bones(f, input):
    global object_bones_offset, object_bones
    object_bones_offset = []
    object_bones = []
    f.seek(header_bones_offset[input]+12)
    count=struct.unpack('<i', f.read(4))[0]
    print(f"Bones Count: {count}")
    f.read(8)
    for i in range(count):
        offset = f.tell()
        object_bones_offset.append(offset)
        bone = struct.unpack('<i', f.read(4))[0]
        object_bones.append(bone)
        name = bones_name[bone]
        print(f"Index {i}, Offset {offset}, Bone {bone} ({name})")
        pass
    pass
def bones_list(f):
    global bones_count, read_bones_offset
    for i in range(bones_count):
        name = bones_name[i]
        offset = bones_offset[i]
        parrent = bones_parrent[i]
        parrent_name = "none"
        if parrent != -1:
            parrent_name = bones_name[parrent]
            pass
        print(f"Index {i}, Name {name}, Offset {offset}, Parrent {parrent} ({parrent_name})")
        pass

    pass
def change_object_bones(f, index):
    global object_bones, object_bones_offset
    f.seek(object_bones_offset[index])
    pointer=object_bones[index]
    print(f"Old Bone: {pointer} ({bones_name[pointer]})")
    pointer=int(input("New Bone: "))
    f.write(struct.pack('<i',pointer))
    object_bones[index]=pointer
    print(f"Write at Offset {object_bones_offset[index]}, Value {object_bones[index]} ({bones_name[pointer]})")
    pass

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} infile")
        return 1

    try:
        yobj_file = open(sys.argv[1], "r+b")
    except IOError:
        print(f"Cannot open {sys.argv[1]}")
        return 1
    read_bones(yobj_file)
    read_object(yobj_file)
    index=int(input("Index: "))
    read_object_bones(yobj_file, index)
    index=int(input("Index: "))
    bones_list(yobj_file)
    change_object_bones(yobj_file, index)
    yobj_file.close()

    return 0

if __name__ == "__main__":
    main()
