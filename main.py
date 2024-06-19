import os
import math
import shutil
import sqlite3
import webbrowser
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw


class Game:
    def __init__(self, id, name, difficulty):
        self.id = id
        self.name = name
        self.difficulty = difficulty

    def pdf_file(self):
        base_path = 'documents'
        # folder should exist
        os.makedirs(base_path, exist_ok=True)
        filename = f"{self.name.replace(' ', '-').lower()}.pdf"
        path = os.path.join(base_path, filename)
        return path

    def pdf_file_exists(self):
        return os.path.isfile(self.pdf_file())


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

    tk.Label(root, text=f"Game: {game.name}").pack(pady=10)
    tk.Label(root, text=f"Difficulty: {game.difficulty}").pack(pady=10)
    tk.Button(root, text="Add Photos (Unimplemented)", command=lambda: messagebox.showinfo(
        "Info", "Feature not implemented")).pack(pady=5)
    tk.Button(root, text="Generate PDF",
              command=generate_pdf(game)).pack(pady=5)

    file = game.pdf_file()
    if file:
        tk.Button(root, text="View PDF",
                  command=lambda: view_pdf(game)).pack(pady=5)

    tk.Button(root, text="Back to Dashboard",
              command=show_dashboard).pack(pady=5)

    frame = tk.Frame(root)
    frame.pack()

    # image grid
    col = 0
    row = 0
    for image in images:
        image_path = os.path.join(subfolder_path, image)
        resized_image = resize_image(image_path, 50)
        img = ImageTk.PhotoImage(image=resized_image)
        label = tk.Label(frame, image=img)
        label.image = img
        label.grid(column=col, row=row, ipadx=5, pady=5)

        if col == 5:
            col = 0
            row += 1
        else:
            col += 1


def generate_pdf(game):
    create_pdf(os.path.join('images', str(game.id)), game.pdf_file())


def view_pdf(game):
    webbrowser.open_new(game.pdf_file())


def create_circular_mask(size):
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255, outline=(0,))
    return mask


def create_circle_with_images(image_paths, circle_diameter):
    circle_image = Image.new(
        "RGBA", (circle_diameter, circle_diameter), (255, 255, 255, 255))
    mask = create_circular_mask((circle_diameter, circle_diameter))

    num_images = len(image_paths)
    angle_step = 360 / num_images
    radius = circle_diameter // 2  # adjust radius for distance to center
    radius = radius - 30

    for i, image_path in enumerate(image_paths):
        image = Image.open(image_path).convert("RGBA")
        max_image_size = circle_diameter // 3  # Adjust this size if needed
        image.thumbnail((max_image_size, max_image_size))

        angle = i * angle_step
        x = radius + int(radius * math.cos(math.radians(angle)))
        y = radius + int(radius * math.sin(math.radians(angle)))
        circle_image.paste(image, (x, y), image)

    circle_image = Image.composite(circle_image, Image.new(
        "RGBA", (circle_diameter, circle_diameter), (255, 255, 255, 0)), mask)
    draw = ImageDraw.Draw(circle_image)

    # todo: add outline to circle for easy cutting
    # if possible dashed line
    draw.ellipse((-5, -5, circle_diameter + 5, circle_diameter + 5), outline='black')

    return circle_image


def create_pdf(image_folder, output_pdf):
    pdf_width, pdf_height = 595, 842  # A4 size in points (1 point = 1/72 inch)
    padding = 15
    # Adjust number of circles per row if needed
    circle_diameter = (pdf_width - 3 * padding) // 3

    image_files = [os.path.join(image_folder, f) for f in os.listdir(
        image_folder) if f.endswith(('jpg', 'png', 'jpeg'))]

    circles_per_row = int(pdf_width // (circle_diameter + padding))
    rows_per_page = int(pdf_height // (circle_diameter + padding))
    total_circles_per_page = circles_per_row * rows_per_page

    # Group images into sets for each circle
    num_images_per_circle = 5  # Adjust number of images per circle if needed
    total_images_per_page = total_circles_per_page * num_images_per_circle

    # Duplicate images if needed without exceeding the total number of images
    while len(image_files) < total_images_per_page:
        num_missing_images = total_images_per_page - len(image_files)
        num_to_add = min(num_missing_images, len(image_files))
        image_files += image_files[:num_to_add]

    image_groups = [image_files[i:i + num_images_per_circle]
                    for i in range(0, len(image_files), num_images_per_circle)]

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
                    circle_image
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
    frame = tk.Frame(root, borderwidth=5, width=100, height=100, bg="lightgrey")
    frame.pack(pady=10)

    tk.Label(frame, text="Create Game").grid(row=0, column=0, columnspan=2, pady=5)
    tk.Label(frame, text="Game Name:").grid(row=1, column=0)
    global entry_name
    entry_name = tk.Entry(frame)
    entry_name.grid(row=1, column=1)

    tk.Label(frame, text="Difficulty:").grid(row=2, column=0)
    global entry_difficulty
    entry_difficulty = tk.Entry(frame)
    entry_difficulty.grid(row=2, column=1)

    tk.Button(frame, text="Add images and create game", command=add_game).grid(
        row=3, columnspan=2, pady=5)


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
root.geometry("800x600")

# Show the dashboard initially
show_dashboard()

root.mainloop()
