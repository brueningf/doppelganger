import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PIL import Image
import sqlite3

# Import the functions we want to test
# We'll need to refactor main.py to make it more testable
from main import Game, resize_image, create_circular_mask


class TestGame(unittest.TestCase):
    """Test cases for the Game class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.test_game = Game(1, "Test Game", "Easy")
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_game_initialization(self):
        """Test that Game object is initialized correctly"""
        self.assertEqual(self.test_game.id, 1)
        self.assertEqual(self.test_game.name, "Test Game")
        self.assertEqual(self.test_game.difficulty, "Easy")
        
    def test_pdf_file_path(self):
        """Test that pdf_file method returns correct path"""
        expected_path = os.path.join('documents', 'test-game.pdf')
        self.assertEqual(self.test_game.pdf_file(), expected_path)
        
    def test_pdf_file_exists_false(self):
        """Test pdf_file_exists returns False when file doesn't exist"""
        self.assertFalse(self.test_game.pdf_file_exists())
        
    def test_pdf_file_exists_true(self):
        """Test pdf_file_exists returns True when file exists"""
        # Create the documents directory and a fake PDF file
        os.makedirs('documents', exist_ok=True)
        pdf_path = self.test_game.pdf_file()
        with open(pdf_path, 'w') as f:
            f.write('fake pdf content')
            
        self.assertTrue(self.test_game.pdf_file_exists())
        
        # Clean up
        os.remove(pdf_path)


class TestImageProcessing(unittest.TestCase):
    """Test cases for image processing functions"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_resize_image(self):
        """Test that resize_image function works correctly"""
        # Create a test image
        test_image_path = os.path.join(self.temp_dir, 'test.png')
        original_image = Image.new('RGB', (100, 50), color='red')
        original_image.save(test_image_path)
        
        # Test resizing
        new_width = 50
        resized_image = resize_image(test_image_path, new_width)
        
        # Check dimensions
        self.assertEqual(resized_image.size[0], new_width)
        self.assertEqual(resized_image.size[1], 25)  # Should maintain aspect ratio
        
    def test_create_circular_mask(self):
        """Test that create_circular_mask creates a proper circular mask"""
        size = (100, 100)
        mask = create_circular_mask(size)
        
        # Check that mask has correct dimensions
        self.assertEqual(mask.size, size)
        
        # Check that mask is grayscale (mode 'L')
        self.assertEqual(mask.mode, 'L')
        
        # Check that center pixel is white (255) and corner is black (0)
        center_pixel = mask.getpixel((50, 50))
        corner_pixel = mask.getpixel((0, 0))
        
        self.assertEqual(center_pixel, 255)
        self.assertEqual(corner_pixel, 0)


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
    def tearDown(self):
        """Clean up after each test method"""
        os.unlink(self.temp_db.name)
        
    def test_database_connection(self):
        """Test that we can connect to database and create tables"""
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        
        # Create tables (same as in main.py)
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
        
        conn.commit()
        conn.close()
        
        # Verify tables were created
        conn = sqlite3.connect(self.temp_db.name)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('games', tables)
        self.assertIn('images', tables)
        conn.close()


if __name__ == '__main__':
    unittest.main() 