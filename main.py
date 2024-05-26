import os
import math
import shutil
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw


class Game:
    def __init__(self, id, name, difficulty):
        self.id = id
        self.name = name
        self.difficulty = difficulty


def resize_image(filename, new_width):
    original_image = Image.open(filename)
    original_width, original_height = original_image.size
    new_height = int((new_width / original_width) * original_height)
    resized_image = original_image.resize(
        (new_width, new_height))
    return resized_image


def add_game():
    try:
        name = entry_name.get()
        difficulty = entry_difficulty.get()
        if not name or not difficulty:
            messagebox.showwarning(
                "Input Error", "Please enter a valid name and difficulty.")
            return

        # Prompt user to select images
        image_files = filedialog.askopenfilenames(
            title="Select Images", filetypes=(
                ("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")
            )
        )
        if not image_files:
            messagebox.showwarning("No Images Selected",
                                   "Please select at least one image.")
            return

        print(image_files)

        # Store images in a list
        images = [os.path.basename(image) for image in image_files]
        print(images)

        # Insert the game into the database
        conn = sqlite3.connect('games.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (name, difficulty) VALUES (?, ?)
        ''', (name, difficulty,))

        conn.commit()
        game_id = cursor.lastrowid
        conn.close()

        try:
            # Fetch the game ID from the database

            # Create the subfolder in the images directory using the game ID
            images_dir = 'images'
            subfolder_path = os.path.join(images_dir, str(game_id))
            os.makedirs(subfolder_path, exist_ok=True)

            # Move the selected image files to the subfolder
            for file_path in image_files:
                shutil.copy(file_path, subfolder_path)
                print(f"Copied {file_path} to {subfolder_path}")

            print("All files have been successfully copied.")

        except ValueError as e:
            print(e)

        messagebox.showinfo("Success", "Game added successfully!")
        entry_name.delete(0, tk.END)
        entry_difficulty.delete(0, tk.END)

        # Refresh the game list on the dashboard
        load_games()
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to load games from the database
def load_games():
    try:
        conn = sqlite3.connect('games.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM games')
        games = cursor.fetchall()
        conn.close()

        # Clear the listbox
        game_listbox.delete(0, tk.END)

        # Populate the listbox with game names
        for game in games:
            game_listbox.insert(tk.END, f"{game[0]}: {game[1]}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Function to handle selecting a game from the list
def select_game(event):
    try:
        selected_game = game_listbox.get(game_listbox.curselection())
        game_id = selected_game.split(":")[0]

        conn = sqlite3.connect('games.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM games WHERE id = ?', (game_id,))
        game = cursor.fetchone()
        conn.close()

        # Navigate to the game detail page
        show_game_detail(Game(game[0], game[1], game[2]))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to show the game detail page


def show_game_detail(game):
    for widget in root.winfo_children():
        widget.destroy()

    subfolder_path = os.path.join('images', str(game.id))
    images = os.listdir(subfolder_path)

    for image in images:
        image_path = os.path.join(subfolder_path, image)
        resized_image = resize_image(image_path, 100)
        img = ImageTk.PhotoImage(image=resized_image)
        label = tk.Label(root, image=img)
        label.image = img
        label.pack(pady=5)

    tk.Label(root, text=f"Game: {game.name}").pack(pady=10)
    tk.Label(root, text=f"Difficulty: {game.difficulty}").pack(pady=10)
    tk.Button(root, text="Add Photos (Unimplemented)", command=lambda: messagebox.showinfo(
        "Info", "Feature not implemented")).pack(pady=5)
    tk.Button(root, text="Generate PDF",
              command=generate_pdf(game)).pack(pady=5)
    tk.Button(root, text="Back to Dashboard",
              command=show_dashboard).pack(pady=5)


def generate_pdf(game):
    create_pdf(os.path.join('images', str(game.id)), f"{game.name}.pdf")


def create_circular_mask(size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255, outline=0)
    return mask


def create_circle_with_images(image_paths, circle_diameter):
    circle_image = Image.new(
        "RGBA", (circle_diameter, circle_diameter), (255, 255, 255, 0))
    mask = create_circular_mask((circle_diameter, circle_diameter))

    num_images = len(image_paths)
    angle_step = 360 / num_images
    radius = circle_diameter // 3  # adjust radius for distance to center

    for i, image_path in enumerate(image_paths):
        image = Image.open(image_path).convert("RGBA")
        max_image_size = circle_diameter // 4  # Adjust this size if needed
        image.thumbnail((max_image_size, max_image_size))

        angle = i * angle_step
        x = radius + int(radius * math.cos(math.radians(angle))
                         ) - image.width // 2
        y = radius + int(radius * math.sin(math.radians(angle))
                         ) - image.height // 2

        circle_image.paste(image, (x, y), image)

    circle_image = Image.composite(circle_image, Image.new(
        "RGBA", (circle_diameter, circle_diameter), (255, 255, 255, 0)), mask)
    return circle_image


def create_pdf(image_folder, output_pdf):
    pdf_width, pdf_height = 595, 842  # A4 size in points (1 point = 1/72 inch)
    padding = 20
    # Adjust number of circles per row if needed
    circle_diameter = (pdf_width - 2 * padding) // 3

    image_files = [os.path.join(image_folder, f) for f in os.listdir(
        image_folder) if f.endswith(('jpg', 'png', 'jpeg'))]

    # Group images into sets for each circle
    num_images_per_circle = 5  # Adjust number of images per circle if needed
    image_groups = [image_files[i:i + num_images_per_circle]
                    for i in range(0, len(image_files), num_images_per_circle)]

    circles_per_row = int(pdf_width // (circle_diameter + padding))
    rows_per_page = int(pdf_height // (circle_diameter + padding))
    total_circles_per_page = circles_per_row * rows_per_page

    pages = []
    for i in range(0, len(image_groups), total_circles_per_page):
        page = Image.new("RGB", (pdf_width, pdf_height), "white")
        page_image_groups = image_groups[i:i + total_circles_per_page]

        for row in range(rows_per_page):
            for col in range(circles_per_row):
                index = row * circles_per_row + col
                if index < len(page_image_groups):
                    circle_images = page_image_groups[index]
                    circle_image = create_circle_with_images(
                        circle_images, circle_diameter)
                    x = padding + col * (circle_diameter + padding)
                    y = padding + row * (circle_diameter + padding)
                    page.paste(circle_image, (x, y), circle_image)
        pages.append(page)

    if pages:
        pages[0].save(output_pdf, save_all=True, append_images=pages[1:])

# A dashboard where games can be added, and listed


def show_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Game Manager").pack(pady=10)

    # Game list
    global game_listbox
    game_listbox = tk.Listbox(root)
    game_listbox.pack(pady=10)
    game_listbox.bind('<<ListboxSelect>>', select_game)

    load_games()

    # Entry fields and button for adding a game
    frame = tk.Frame(root, borderwidth=5, width=100, height=100)
    frame.pack(pady=10)

    tk.Label(frame, text="Game Name:").grid(row=0, column=0)
    global entry_name
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)

    tk.Label(frame, text="Difficulty:").grid(row=1, column=0)
    global entry_difficulty
    entry_difficulty = tk.Entry(frame)
    entry_difficulty.grid(row=1, column=1)

    tk.Button(frame, text="Add Game", command=add_game).grid(
        row=2, columnspan=2, pady=5)


# Create database and table
conn = sqlite3.connect('games.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        name TEXT,
        difficulty TEXT
    );
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id INT NOT NULL,
        image_path TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (game_id) REFERENCES games(id)
    );
''')
conn.close()

# Tkinter GUI setup
root = tk.Tk()
root.title("Dobble Game Generator")
content = tk.Frame(root)
frame = tk.Frame(content, borderwidth=5, relief="ridge", width=200, height=100)

# Show the dashboard initially
show_dashboard()

root.mainloop()
