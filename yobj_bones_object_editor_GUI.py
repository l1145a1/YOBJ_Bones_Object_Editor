import struct
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

# Global Variables
bones = []
bones_offset = []
bones_name = []
bones_parrent = []
read_bones_offset = 0
bones_count = 0

header_object_offset = 0
object_count = 0
object_offset = []
header_bones_offset = []

object_bones_offset = []
object_bones = []

selected_object = None
selected_object_bone = None
selected_bones = None

view_stack = []

# Functions
# Fungsi membuat backup
def backup_file(target_file):
    """Membuat backup file dengan ekstensi .bak"""
    try:
        # Membuka file target untuk dibaca
        with open(target_file, "r+b") as target_yobj:
            # Menentukan nama file backup
            backup_file = target_file + ".bak"

            # Membuat file backup dan menyalin kontennya
            with open(backup_file, "wb") as backup:
                target_yobj.seek(0)  # Pastikan pointer di awal file
                shutil.copyfileobj(target_yobj, backup)

            print(f"Backup file berhasil dibuat: {backup_file}")
            return True
    except IOError as e:
        print(f"Error saat membuat backup file: {e}")
        return False

def read_bones(f):
    global bones_count, read_bones_offset
    bones.clear()
    bones_offset.clear()
    bones_name.clear()
    bones_parrent.clear()

    f.seek(28)
    bones_count = struct.unpack('<i', f.read(4))[0]
    print(f"Bones count: {bones_count}")

    f.seek(40)
    read_bones_offset = struct.unpack('<i', f.read(4))[0]
    print(f"Bones offset: {read_bones_offset + 8}")

    f.seek(read_bones_offset + 8)
    for i in range(bones_count):
        offset = f.tell()
        bones_offset.append(offset)

        pointer = f.read(16).decode('ascii').strip('\x00')
        bones_name.append(pointer)

        f.read(32)
        pointer = struct.unpack('<i', f.read(4))[0]
        bones_parrent.append(pointer)

        f.seek(-52, 1)
        pointer = f.read(80)
        bones.append(pointer)

def read_object(f):
    global header_object_offset, object_count
    object_offset.clear()
    header_bones_offset.clear()

    f.seek(24)
    object_count = struct.unpack('<i', f.read(4))[0]
    print(f"Object count: {object_count}")

    f.seek(36)
    header_object_offset = struct.unpack('<i', f.read(4))[0]
    print(f"Object offset: {header_object_offset + 8}")

    f.seek(header_object_offset + 8)
    for i in range(object_count):
        offset = f.tell()
        object_offset.append(offset)

        f.read(8)
        b_header = struct.unpack('<i', f.read(4))[0]
        header_bones_offset.append(b_header)

        print(f"Object {i}, Offset {offset}, Bones Header Offset {b_header}")
        f.read(52)

def read_object_bones(f, input):
    global object_bones_offset, object_bones
    object_bones_offset = []
    object_bones = []
    f.seek(header_bones_offset[input] + 12)
    count = struct.unpack('<i', f.read(4))[0]
    print(f"Bones Count: {count}")
    f.read(8)
    for i in range(count):
        offset = f.tell()
        object_bones_offset.append(offset)
        bone = struct.unpack('<i', f.read(4))[0]
        object_bones.append(bone)
        name = bones_name[bone]
        print(f"Index {i}, Offset {offset}, Bone {bone} ({name})")

def browse_file():
    global file_path
    file_path = filedialog.askopenfilename(title="Select YOBJ File", filetypes=[("YOBJ files", "*.yobj"), ("All files", "*.*")])
    if not file_path:
        return

    file_path_var.set(file_path)  # Set the file path to the variable

    try:
        with open(file_path, 'rb') as f:
            read_bones(f)
            read_object(f)

        update_object_list()
        view_mode.set("objects")
        messagebox.showinfo("Success", "File loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")

def on_double_click(event):
    if not file_path_var.get():  # Check if the file path is set
        messagebox.showerror("Error", "No file loaded. Please browse for a file first.")
        return

    if view_mode.get() == "objects":
        selected_index = object_list.curselection()
        if selected_index:
            index = selected_index[0]
            try:
                with open(file_path_var.get(), 'rb') as f:
                    read_object_bones(f, index)
                view_mode.set("bones")
                update_bones_list()
                print(f"Switched to bones view for Object {index}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read object bones: {e}")
    else:
        print("Already in bones view.")


def update_object_list():
    object_list.delete(0, tk.END)
    for i, offset in enumerate(object_offset):
        bones_header = header_bones_offset[i]
        object_list.insert(tk.END, f"Object {i}, Offset {offset}, Bones Header Offset {bones_header}")

def update_bones_list():
    object_list.delete(0, tk.END)
    for i, offset in enumerate(object_bones_offset):
        bone = object_bones[i]
        name = bones_name[bone]
        object_list.insert(tk.END, f"Index {i}, Offset {offset}, Bone {bone} ({name})")

# Perbarui fungsi on_object_select
def on_object_select(event):
    global selected_object, selected_object_bone, selected_bones
    selected_index = object_list.curselection()
    if selected_index:
        if view_mode.get() == "objects":
            selected_object = selected_index[0]
            print(f"Selected Object Index: {selected_object}")
        elif view_mode.get() == "bones":
            selected_object_bone = selected_index[0]
            print(f"Selected Bone Index: {selected_object_bone}")
        elif view_mode.get() == "bones_view":
            selected_bones = selected_index[0]
            print(f"Selected Bone View Index: {selected_bones}")
    else:
        print("No item selected.")

# Perbarui fungsi on_double_click untuk mendukung bones_view
# Fungsi untuk mengubah tulang pada objek
def change_object_bones(f):
    global selected_bones, object_bones, object_bones_offset, file_path
    backup_file(file_path)
    if selected_bones is None:
        messagebox.showerror("Error", "No bone selected.")
        return

    try:
        # Pindahkan ke offset tulang yang dipilih
        offset = object_bones_offset[selected_object_bone]
        f.seek(offset)

        # Ambil tulang baru dari selected_bones
        new_bone = selected_bones

        # Tulis tulang baru ke file
        f.write(struct.pack('<i', new_bone))

        # Perbarui data di memori
        print(f"Updated Offset {offset} with Bone Index {new_bone} ({bones_name[new_bone]})")
        messagebox.showinfo("Success", "Bone changed successfully!")
    except Exception as e:
        print(f"Error changing bone: {e}")
        messagebox.showerror("Error", f"Failed to update bone: {e}")

# Perbarui logika double-click untuk bones_view
def on_double_click(event):
    if view_mode.get() == "objects":
        selected_index = object_list.curselection()
        if selected_index:
            index = selected_index[0]
            with open(file_path_var.get(), 'rb') as f:
                read_object_bones(f, index)
            view_mode.set("bones")
            update_bones_list()
            print(f"Switched to bones view for Object {index}")
    elif view_mode.get() == "bones":
        selected_index = object_list.curselection()
        if selected_index:
            index = selected_index[0]
            view_mode.set("bones_view")
            update_bones_view()
            print(f"Switched to detailed bones view for Bone {index}")
    elif view_mode.get() == "bones_view":
        if selected_bones is not None:
            with open(file_path_var.get(), 'r+b') as f:
                change_object_bones(f)
            # Perbarui tampilan setelah modifikasi
            with open(file_path_var.get(), 'rb') as f:
                read_object_bones(f, selected_object)
            view_mode.set("bones")  # Kembali ke tampilan bones
            update_bones_list()
            print(f"Bone {selected_bones} updated. Returned to bones view.")
        else:
            print("No bone selected for modification.")

# Fungsi baru untuk update bones_view
def update_bones_view():
    object_list.delete(0, tk.END)
    for i, offset in enumerate(bones_offset):
        name = bones_name[i]
        parrent = bones_parrent[i]
        parrent_name = "None"
        if parrent != -1:
            parrent_name = bones_name[parrent]
        object_list.insert(tk.END, f"Index {i}, Name {name}, Offset {offset}, Parent {parrent} ({parrent_name})")

# Perbarui tombol "Switch to Objects" untuk menjadi tombol "Back"
def back():
    if view_mode.get() == "bones_view":
        view_mode.set("bones")
        update_bones_list()
        print("Switched back to bones view.")
    elif view_mode.get() == "bones":
        view_mode.set("objects")
        update_object_list()
        print("Switched back to objects view.")

def update_mode():
    """Update the UI based on the current view mode."""
    current_mode = view_mode.get()
    object_list.delete(0, tk.END)

    if current_mode == "objects":
        update_object_list()
    elif current_mode == "bones":
        update_bones_list()
    # Add future modes here
    print(f"Current mode: {current_mode}")

# GUI Setup
root = tk.Tk()
root.title("YOBJ Bone Modifier")

view_mode = tk.StringVar(value="objects")
file_path_var = tk.StringVar()

frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

browse_button = tk.Button(frame, text="Browse YOBJ File", command=browse_file)
browse_button.pack(pady=5)

back_button = tk.Button(frame, text="Back", command=back)
back_button.pack(pady=5)

object_list = tk.Listbox(frame, height=15, width=50)
object_list.pack(pady=5, fill=tk.BOTH, expand=True)
object_list.bind("<<ListboxSelect>>", on_object_select)
object_list.bind("<Double-1>", on_double_click)

root.mainloop()
