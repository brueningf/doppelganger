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
    try:
        print(f"Opening image: {filename}")
        original_image = Image.open(filename)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if original_image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', original_image.size, (255, 255, 255))
            if original_image.mode == 'P':
                original_image = original_image.convert('RGBA')
            background.paste(original_image, mask=original_image.split()[-1] if original_image.mode == 'RGBA' else None)
            original_image = background
        elif original_image.mode != 'RGB':
            original_image = original_image.convert('RGB')
        
        original_width, original_height = original_image.size
        new_height = int((new_width / original_width) * original_height)
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Resized image from {original_width}x{original_height} to {new_width}x{new_height}")
        return resized_image
    except Exception as e:
        print(f"Error in resize_image: {str(e)}")
        # Return a placeholder image if loading fails
        placeholder = Image.new('RGB', (new_width, new_width), color='lightgray')
        return placeholder


def add_game():
    try:
        name = entry_name.get()
        difficulty = difficulty_var.get()
        if not name or not difficulty:
            messagebox.showwarning(
                "Input Error", "Please enter a valid name and difficulty.")
            return

        # Insert the game into the database
        conn = sqlite3.connect('games.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO games (name, difficulty) VALUES (?, ?)
        ''', (name, difficulty,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Game added successfully!")
        entry_name.delete(0, tk.END)
        difficulty_var.set('Easy')

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

    # Main container
    main_container = tk.Frame(root, bg="#f5f5f5")
    main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Header section with game info and navigation
    header_frame = tk.Frame(main_container, bg="#2c3e50", height=100)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    header_frame.pack_propagate(False)

    # Back button and title
    header_content = tk.Frame(header_frame, bg="#2c3e50")
    header_content.pack(expand=True, padx=20)

    back_btn = tk.Button(header_content, text="← Back to Dashboard", 
                        command=show_dashboard, font=("Arial", 12, "bold"),
                        bg="#34495e", fg="#2c3e50", relief=tk.FLAT, padx=15, pady=5)
    back_btn.pack(side=tk.LEFT)

    title_label = tk.Label(header_content, text=f"🎮 {game.name}", 
                          font=("Arial", 24, "bold"), fg="white", bg="#2c3e50")
    title_label.pack(side=tk.LEFT, padx=20)

    difficulty_label = tk.Label(header_content, text=f"Difficulty: {game.difficulty}", 
                               font=("Arial", 14), fg="#ecf0f1", bg="#2c3e50")
    difficulty_label.pack(side=tk.RIGHT)

    # Content area with three sections
    content_frame = tk.Frame(main_container, bg="#f5f5f5")
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Left section - Actions
    actions_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
    actions_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    # Actions header
    actions_header = tk.Frame(actions_frame, bg="#3498db", height=40)
    actions_header.pack(fill=tk.X)
    actions_header.pack_propagate(False)
    
    tk.Label(actions_header, text="⚙️ Actions", font=("Arial", 14, "bold"), 
            fg="white", bg="#3498db").pack(expand=True)

    # Action buttons
    actions_content = tk.Frame(actions_frame, bg="white")
    actions_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    add_photos_btn = tk.Button(actions_content, text="📷 Add Photos", 
                              command=lambda: add_images_to_game(game),
                              font=("Arial", 12, "bold"), bg="#27ae60", fg="#1e8449",
                              relief=tk.FLAT, padx=20, pady=10, width=15)
    add_photos_btn.pack(fill=tk.X, pady=(0, 10))

    generate_pdf_btn = tk.Button(actions_content, text="📄 Generate PDF", 
                                command=lambda: generate_pdf(game),
                                font=("Arial", 12, "bold"), bg="#f39c12", fg="#d68910",
                                relief=tk.FLAT, padx=20, pady=10, width=15)
    generate_pdf_btn.pack(fill=tk.X, pady=(0, 10))

    file = game.pdf_file()
    if os.path.isfile(file):
        view_pdf_btn = tk.Button(actions_content, text="👁️ View PDF", 
                                command=lambda: view_pdf(game),
                                font=("Arial", 12, "bold"), bg="#9b59b6", fg="#8e44ad",
                                relief=tk.FLAT, padx=20, pady=10, width=15)
        view_pdf_btn.pack(fill=tk.X, pady=(0, 10))

    # Game stats
    stats_frame = tk.Frame(actions_content, bg="#f8f9fa", relief=tk.SUNKEN, bd=1)
    stats_frame.pack(fill=tk.X, pady=(20, 0))
    
    tk.Label(stats_frame, text="📊 Game Stats", font=("Arial", 12, "bold"), 
            bg="#f8f9fa", fg="black").pack(anchor=tk.W, padx=10, pady=(10, 5))

    # Count images
    subfolder_path = os.path.join('images', str(game.id))
    os.makedirs(subfolder_path, exist_ok=True)
    images = [f for f in os.listdir(subfolder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    tk.Label(stats_frame, text=f"Images: {len(images)}", font=("Arial", 10), 
            bg="#f8f9fa", fg="black").pack(anchor=tk.W, padx=10, pady=2)
    
    tk.Label(stats_frame, text=f"PDF: {'✅ Generated' if os.path.isfile(file) else '❌ Not generated'}", 
            font=("Arial", 10), bg="#f8f9fa", fg="black").pack(anchor=tk.W, padx=10, pady=(2, 10))

    # Right section - Image Gallery
    gallery_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
    gallery_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    # Gallery header
    gallery_header = tk.Frame(gallery_frame, bg="#e74c3c", height=40)
    gallery_header.pack(fill=tk.X)
    gallery_header.pack_propagate(False)
    
    tk.Label(gallery_header, text=f"🖼️ Image Gallery ({len(images)} images)", 
            font=("Arial", 14, "bold"), fg="white", bg="#e74c3c").pack(expand=True)

    # Gallery content with scrollbar
    gallery_content = tk.Frame(gallery_frame, bg="white")
    gallery_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create canvas for scrollable gallery
    canvas = tk.Canvas(gallery_content, bg="white")
    scrollbar = tk.Scrollbar(gallery_content, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Display images in a grid
    if images:
        # Keep a list to maintain references to images
        image_references = []
        
        # Calculate grid layout
        images_per_row = 3  # Reduced to make room for remove buttons
        for i, image in enumerate(images):
            try:
                image_path = os.path.join(subfolder_path, image)
                print(f"Loading image: {image_path}")  # Debug print
                
                # Check if file exists
                if not os.path.exists(image_path):
                    print(f"File does not exist: {image_path}")
                    raise FileNotFoundError(f"Image file not found: {image_path}")
                
                # Load and resize image
                resized_image = resize_image(image_path, 100)  # Larger thumbnails
                print(f"Image resized successfully: {resized_image.size}")
                
                # Convert to PhotoImage
                img = ImageTk.PhotoImage(image=resized_image)
                image_references.append(img)  # Keep reference to prevent garbage collection
                print(f"PhotoImage created successfully")
                
                # Create image container
                img_container = tk.Frame(scrollable_frame, bg="white", relief=tk.RAISED, bd=1)
                img_container.grid(row=i // images_per_row, column=i % images_per_row, 
                                 padx=5, pady=5, sticky="nsew")
                
                # Image label with explicit size
                img_label = tk.Label(img_container, image=img, bg="white", width=100, height=100)
                img_label.pack(padx=5, pady=(5, 0))
                
                # Image name label with black text
                name_label = tk.Label(img_container, text=image[:15] + "..." if len(image) > 15 else image,
                                    font=("Arial", 9), bg="white", fg="black")
                name_label.pack(pady=(2, 0))
                
                # Remove button
                remove_btn = tk.Button(img_container, text="🗑️ Remove", 
                                     command=lambda g=game, img=image: remove_image_from_game(g, img),
                                     font=("Arial", 8, "bold"), bg="#e74c3c", fg="#c0392b",
                                     relief=tk.FLAT, padx=8, pady=2)
                remove_btn.pack(pady=(2, 5))
                
            except Exception as e:
                print(f"Error loading image {image}: {str(e)}")  # Debug print
                # Handle image loading errors
                error_container = tk.Frame(scrollable_frame, bg="#ffebee", relief=tk.RAISED, bd=1)
                error_container.grid(row=i // images_per_row, column=i % images_per_row, 
                                   padx=5, pady=5, sticky="nsew")
                
                tk.Label(error_container, text="❌ Error", font=("Arial", 12, "bold"),
                        bg="#ffebee", fg="#c62828").pack(expand=True)
                tk.Label(error_container, text=f"Could not load:\n{image}", 
                        font=("Arial", 8), bg="#ffebee", fg="#c62828").pack(pady=(0, 5))
                
                # Remove button for error images too
                remove_btn = tk.Button(error_container, text="🗑️ Remove", 
                                     command=lambda g=game, img=image: remove_image_from_game(g, img),
                                     font=("Arial", 8, "bold"), bg="#e74c3c", fg="#c0392b",
                                     relief=tk.FLAT, padx=8, pady=2)
                remove_btn.pack(pady=(0, 5))
    else:
        # No images message
        no_images_frame = tk.Frame(scrollable_frame, bg="white")
        no_images_frame.pack(expand=True, pady=50)
        
        tk.Label(no_images_frame, text="📷 No Images Yet", font=("Arial", 16, "bold"),
                bg="white", fg="black").pack()
        tk.Label(no_images_frame, text="Click 'Add Photos' to get started!", 
                font=("Arial", 12), bg="white", fg="black").pack(pady=10)

    # Pack canvas and scrollbar
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


def generate_pdf(game):
    create_pdf(os.path.join('images', str(game.id)), game.pdf_file())


def view_pdf(game):
    pdf_path = game.pdf_file()
    if not os.path.exists(pdf_path):
        messagebox.showerror("Error", f"PDF file not found: {pdf_path}")
        return
    
    try:
        # Try to open with the default system PDF viewer
        import subprocess
        import platform
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", pdf_path], check=True)
        elif system == "Windows":
            os.startfile(pdf_path)
        else:  # Linux
            subprocess.run(["xdg-open", pdf_path], check=True)
            
    except subprocess.CalledProcessError:
        # Fallback to webbrowser if subprocess fails
        try:
            # Convert to file:// URL for webbrowser
            import urllib.parse
            file_url = "file://" + urllib.parse.quote(os.path.abspath(pdf_path))
            webbrowser.open_new(file_url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not open PDF: {str(e)}")


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


def add_images_to_game(game):
    # Prompt user to select images
    filetypes = [
        ("PNG Images", "*.png"),
        ("JPG Images", "*.jpg"),
        ("JPEG Images", "*.jpeg"),
        ("All Files", "*.*")
    ]
    image_files = filedialog.askopenfilenames(
        title="Select Images", filetypes=filetypes
    )
    if not image_files:
        messagebox.showwarning("No Images Selected",
                               "Please select at least one image.")
        return
    try:
        images_dir = 'images'
        subfolder_path = os.path.join(images_dir, str(game.id))
        os.makedirs(subfolder_path, exist_ok=True)
        for file_path in image_files:
            shutil.copy(file_path, subfolder_path)
        messagebox.showinfo("Success", "Images added successfully!")
        show_game_detail(game)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def remove_image_from_game(game, image_filename):
    """Remove a specific image from a game"""
    try:
        subfolder_path = os.path.join('images', str(game.id))
        image_path = os.path.join(subfolder_path, image_filename)
        
        if os.path.exists(image_path):
            os.remove(image_path)
            messagebox.showinfo("Success", f"Image '{image_filename}' removed successfully!")
            # Refresh the game detail view
            show_game_detail(game)
        else:
            messagebox.showerror("Error", f"Image file not found: {image_filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not remove image: {str(e)}")


# A dashboard where games can be added, and listed
def show_dashboard():
    for widget in root.winfo_children():
        widget.destroy()

    # Main container with padding
    main_container = tk.Frame(root, bg="#f5f5f5")
    main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Header section
    header_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="🎮 Dobble Game Generator", 
                          font=("Arial", 24, "bold"), fg="white", bg="#2c3e50")
    title_label.pack(expand=True)

    # Content area with two columns
    content_frame = tk.Frame(main_container, bg="#f5f5f5")
    content_frame.pack(fill=tk.BOTH, expand=True)

    # Left column - Game List
    left_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    # Game list header
    list_header = tk.Frame(left_frame, bg="#34495e", height=40)
    list_header.pack(fill=tk.X)
    list_header.pack_propagate(False)
    
    tk.Label(list_header, text="📋 Your Games", font=("Arial", 14, "bold"), 
            fg="white", bg="#34495e").pack(expand=True)

    # Game list with scrollbar
    list_frame = tk.Frame(left_frame)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    global game_listbox
    game_listbox = tk.Listbox(list_frame, font=("Arial", 12), 
                             selectmode=tk.SINGLE, bg="white", 
                             selectbackground="#3498db", selectforeground="white")
    game_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    game_listbox.bind('<<ListboxSelect>>', select_game)

    # Scrollbar for game list
    scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=game_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    game_listbox.config(yscrollcommand=scrollbar.set)

    load_games()

    # Right column - Create Game Form
    right_frame = tk.Frame(content_frame, bg="white", relief=tk.RAISED, bd=2)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

    # Form header
    form_header = tk.Frame(right_frame, bg="#27ae60", height=40)
    form_header.pack(fill=tk.X)
    form_header.pack_propagate(False)
    
    tk.Label(form_header, text="➕ Create New Game", font=("Arial", 14, "bold"), 
            fg="white", bg="#27ae60").pack(expand=True)

    # Form content
    form_frame = tk.Frame(right_frame, bg="white")
    form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Game name input
    tk.Label(form_frame, text="Game Name:", font=("Arial", 12, "bold"), 
            bg="white", fg="black").pack(anchor=tk.W, pady=(0, 5))
    global entry_name
    entry_name = tk.Entry(form_frame, font=("Arial", 12), 
                         relief=tk.SOLID, bd=1, bg="#ecf0f1")
    entry_name.pack(fill=tk.X, pady=(0, 15))

    # Difficulty selection
    tk.Label(form_frame, text="Difficulty Level:", font=("Arial", 12, "bold"), 
            bg="white", fg="black").pack(anchor=tk.W, pady=(0, 5))
    global difficulty_var
    difficulty_var = tk.StringVar()
    difficulty_var.set('Easy')
    difficulty_options = ['Easy', 'Medium', 'Hard']
    difficulty_menu = tk.OptionMenu(form_frame, difficulty_var, *difficulty_options)
    difficulty_menu.config(font=("Arial", 12), bg="#ecf0f1", relief=tk.SOLID, bd=1)
    difficulty_menu.pack(fill=tk.X, pady=(0, 20))

    # Create button
    create_btn = tk.Button(form_frame, text="🎯 Create Game", command=add_game,
                          font=("Arial", 14, "bold"), bg="#3498db", fg="#2980b9",
                          relief=tk.FLAT, padx=20, pady=10)
    create_btn.pack(pady=10)

    # Instructions section
    instructions_frame = tk.Frame(right_frame, bg="#f8f9fa", relief=tk.SUNKEN, bd=1)
    instructions_frame.pack(fill=tk.X, padx=10, pady=10)
    
    tk.Label(instructions_frame, text="💡 Instructions:", font=("Arial", 12, "bold"), 
            bg="#f8f9fa", fg="black").pack(anchor=tk.W, padx=10, pady=(10, 5))
    
    instructions_text = """1. Create a new game with a name and difficulty
2. Select a game from the list to manage it
3. Add images to your game
4. Generate and view the PDF cards"""
    
    tk.Label(instructions_frame, text=instructions_text, font=("Arial", 10), 
            bg="#f8f9fa", fg="black", justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=(0, 10))


def initialize_database():
    """Initialize the database with required tables"""
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


def main():
    """Main function to run the application"""
    # Initialize database
    initialize_database()
    
    # Tkinter GUI setup
    global root
    root = tk.Tk()
    root.title("🎮 Dobble Game Generator")
    root.geometry("1200x800")
    root.minsize(1000, 700)  # Set minimum window size
    
    # Configure window icon (if available)
    try:
        root.iconbitmap('public/favicon.svg')
    except:
        pass  # Icon not available, continue without it

    # Show the dashboard initially
    show_dashboard()

    root.mainloop()


if __name__ == '__main__':
    main()
