from PIL import Image
import numpy as np
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os

def generate_random_positions(seed, num_bits, height, width):
    random.seed(seed)
    all_positions = [(x, y) for x in range(width) for y in range(height)]
    random.shuffle(all_positions)
    return all_positions[:num_bits]

def encode(image_path, secret_message, seed):
    image = Image.open(image_path)
    data = np.array(image)

    binary_message = ''.join(format(ord(char), '08b') for char in secret_message)
    binary_message += '1111111111111110'  # Marker kraja poruke

    if len(binary_message) > data.size:
        raise ValueError("Poruka je predugačka za ovu sliku.")

    height, width, _ = data.shape

    positions = generate_random_positions(seed, len(binary_message), height, width)

    for idx, (x, y) in enumerate(positions):
        if idx < len(binary_message):
            bit = int(binary_message[idx])
            data[y][x][0] = (data[y][x][0] & ~1) | bit

    base_name, _ = os.path.splitext(image_path)
    output_path = f"{base_name}_encoded.png"
    encoded_image = Image.fromarray(data)
    encoded_image.save(output_path)
    messagebox.showinfo("Uspeh", f"Poruka je uspešno kodirana u sliku: {output_path}")

def decode(image_path, seed):
    print("Pokreće se dekodiranje...")
    image = Image.open(image_path)
    data = np.array(image)

    binary_message = ""

    height, width, _ = data.shape
    max_bits = data.size  
    positions = generate_random_positions(seed, max_bits, height, width)

    
    for idx, (x, y) in enumerate(positions):
        if y < height and x < width:
            bit = str(data[y][x][0] & 1)  
            binary_message += bit

            if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                print("Kraj poruke detektovan!")
                break

    secret_message = ""
    for i in range(0, len(binary_message) - 16, 8):
        byte = binary_message[i:i + 8]
        secret_message += chr(int(byte, 2))

    if secret_message:
        messagebox.showinfo("Dekodirana poruka", f"Dekodirana poruka: {secret_message}")
    else:
        messagebox.showinfo("Dekodirana poruka", "Nema dekodirane poruke.")
    return secret_message

def select_image(entry_field):
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        entry_field.delete(0, tk.END)
        entry_field.insert(0, file_path)

def encode_message():
    image_path = entry_image_path_encode.get()
    secret_message = entry_secret_message.get("1.0", tk.END).strip()
    seed = entry_seed_encode.get()

    if not image_path or not seed.isdigit():
        messagebox.showerror("Greška", "Molimo vas da izaberete sliku i unesete validan seed.")
        return

    encode(image_path, secret_message, int(seed))

def decode_message():
    image_path = entry_image_path_decode.get()
    seed = entry_seed_decode.get()

    if not image_path or not seed.isdigit():
        messagebox.showerror("Greška", "Molimo vas da izaberete sliku i unesete validan seed.")
        return

    decode(image_path, int(seed))

# GUI
root = tk.Tk()
root.title("Steganografija - Spread Spectrum")

notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# Tab za kodiranje
encode_frame = ttk.Frame(notebook)
notebook.add(encode_frame, text="Kodiranje")


tk.Label(encode_frame, text="Izaberi sliku:").grid(row=0, column=0, sticky="w")  # Poravnanje levo
entry_image_path_encode = tk.Entry(encode_frame, width=50)
entry_image_path_encode.grid(row=0, column=1, sticky="w")
tk.Button(encode_frame, text="Browse", command=lambda: select_image(entry_image_path_encode)).grid(row=0, column=2)

tk.Label(encode_frame, text="Tajna poruka:").grid(row=1, column=0, sticky="w")  # Poravnanje levo

entry_secret_message = tk.Text(encode_frame, width=38, height=10, wrap="word")
entry_secret_message.grid(row=1, column=1, columnspan=2, sticky="w")

tk.Label(encode_frame, text="Seed (ključ):").grid(row=2, column=0)
entry_seed_encode = tk.Entry(encode_frame, width=50)
entry_seed_encode.grid(row=2, column=1, columnspan=2, sticky="w")

tk.Button(encode_frame, text="Kodiraj", command=encode_message).grid(row=3, column=0)

# Tab za dekodiranje
decode_frame = ttk.Frame(notebook)
notebook.add(decode_frame, text="Dekodiranje")

tk.Label(decode_frame, text="Izaberi sliku:").grid(row=0, column=0)
entry_image_path_decode = tk.Entry(decode_frame, width=50)
entry_image_path_decode.grid(row=0, column=1)
tk.Button(decode_frame, text="Browse", command=lambda: select_image(entry_image_path_decode)).grid(row=0, column=2)

tk.Label(decode_frame, text="Seed (ključ):").grid(row=1, column=0)
entry_seed_decode = tk.Entry(decode_frame, width=50)
entry_seed_decode.grid(row=1, column=1)

tk.Button(decode_frame, text="Dekodiraj", command=decode_message).grid(row=2, column=0)

root.mainloop()
