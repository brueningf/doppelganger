import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import os

class Game:
    def __init__(self, name, difficulty, images):
        self.name = name
        self.difficulty = difficulty
        self.images = images

# Function to handle adding a new game
def add_game():
    try:
        name = entry_name.get()
        difficulty = entry_difficulty.get()
        if not name or not difficulty:
            messagebox.showwarning("Input Error", "Please enter a valid name and difficulty.")
            return

        # Prompt user to select images
        image_files = filedialog.askopenfilenames(title="Select Images", filetypes=(("Image Files", "*.png;*.jpg;*.jpeg"),))
        if not image_files:
            messagebox.showwarning("No Images Selected", "Please select at least one image.")
            return

        # Store images in a list
        images = [os.path.basename(image) for image in image_files]

        # Insert the game into the database
        conn = sqlite3.connect('games.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (name, difficulty, images) VALUES (?, ?, ?)
        ''', (name, difficulty, ';'.join(images)))
        conn.commit()
        conn.close()

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
        show_game_detail(Game(game[1], game[2], game[3].split(";")))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to show the game detail page
def show_game_detail(game):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Game: {game.name}").pack(pady=10)
    tk.Button(root, text="Add Photos (Unimplemented)", command=lambda: messagebox.showinfo("Info", "Feature not implemented")).pack(pady=5)
    tk.Button(root, text="Back to Dashboard", command=show_dashboard).pack(pady=5)

# Function to show the dashboard
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
    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Game Name:").grid(row=0, column=0)
    global entry_name
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)

    tk.Label(frame, text="Difficulty:").grid(row=1, column=0)
    global entry_difficulty
    entry_difficulty = tk.Entry(frame)
    entry_difficulty.grid(row=1, column=1)

    tk.Button(frame, text="Add Game", command=add_game).grid(row=2, columnspan=2, pady=5)

# Create database and table
conn = sqlite3.connect('games.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY,
        name TEXT,
        difficulty TEXT,
        images TEXT
    )
''')
conn.close()

# Tkinter GUI setup
root = tk.Tk()
root.title("Game Manager")

# Show the dashboard initially
show_dashboard()

root.mainloop()

