import struct
import sys
import os

bones=[]
bones_offset=[]
bones_name=[]
bones_parrent=[]
read_bones_offset=0
bones_count=0

read_object_offset=0
object_count=0
object_offset=[]
object_bones_offset=[]
object_bones_count=[]

object_bones=[]
bones_part_offset=[]

def bones_list(f):
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

def object_list(f):
    global read_object_offset, object_count
    f.seek(24)
    object_count=struct.unpack('<i', f.read(4))[0]
    print(f"Object Count: {object_count}")
    f.seek(36)
    read_object_offset=struct.unpack('<i', f.read(4))[0]
    print(f"Object Offset: {read_object_offset+8}")
    f.seek(read_object_offset+8)
    for i in range(object_count):
        pointer=f.tell()
        object_offset.append(pointer)
        f.read(8)
        pointer=struct.unpack('<i', f.read(4))[0]
        object_bones_offset.append(pointer)
        checkpoint = f.tell()
        f.seek(object_bones_offset[i]+12)
        pointer=struct.unpack('<i', f.read(4))[0]
        object_bones_count.append(pointer)
        print(f"Object {i}, Bones Offset {object_bones_offset[i]+8}, Bones Count {object_bones_count[i]}")
        f.seek(checkpoint)
        f.read(52)
        pass
    pass

def object_bones_list(f, index):
    global object_bones, bones_part_offset
    object_bones=[]
    bones_part_offset=[]
    f.seek(object_bones_offset[index]+8)
    count= object_bones_count[index]
    print(f"Bones Count: {count}")
    offset=object_bones_offset[index]+8
    print(f"Bones Offset: {offset}")
    f.read(16)
    for i in range(count):
        pointer=f.tell()
        bones_part_offset.append(pointer)
        pointer=struct.unpack('<i', f.read(4))[0]
        object_bones.append(pointer)
        print(f"Index {i}, Offset {bones_part_offset[i]}, Bones {pointer} ({bones_name[pointer]})")
        pass
    pass

def change_object_bones(f, index):
    global object_bones, bones_part_offset
    f.seek(bones_part_offset[index])
    pointer=object_bones[index]
    print(f"Old Bone: {pointer} ({bones_name[pointer]})")
    pointer=int(input("New Bone: "))
    f.write(struct.pack('<i',pointer))
    object_bones[index]=pointer
    print(f"Write at Offset {bones_part_offset[index]}, Value {object_bones[index]} ({bones_name[pointer]})")
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
    bones_list(yobj_file)
    object_list(yobj_file)
    index=int(input("Index: "))
    object_bones_list(yobj_file, index)
    index=int(input("Index: "))
    change_object_bones(yobj_file, index)
    yobj_file.close()

    return 0

if __name__ == "__main__":
    main()
