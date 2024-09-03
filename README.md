# Card game generator
This is a simple and collaborative project focused on generating PDFs with rendered cards. Each page of the PDF contains cards that can be printed and cut out for children coordination games. The cards include icons or images of characters, which are randomly positioned and rotated to create unique cards.

The current code is a rough prototype—functioning but far from polished. Contributions in the form of ideas, refactoring, and improvements are highly encouraged! This project is meant as a desktop application written in Python, initially created to explore PyInstaller and can serve as a learning resource for others.

<img src="https://github.com/user-attachments/assets/ac826b1c-6cd3-49c8-b929-63f53968521d" width=35%>
<img src="https://github.com/user-attachments/assets/15a3948c-a2ff-4e7c-98e1-d9978762778a" width=25%>

<img src="https://github.com/user-attachments/assets/be95351b-6f90-4d03-bcdf-4bdad37a3fec" width=15%>

## To-Do List

- [ ] **Game-Specific Icon Sets**
  - [ ] Custom Icon Upload: Allow users to upload their own icons for each game.
  - [ ] Icon Library: Preload a library of common icons for popular games.
  - [ ] Icon Set Preview: Provide a preview of the selected icon set before generating the cards.

- [ ] **Card Shape Variations**
  - [ ] Standard Rectangular Cards: Generate cards in the traditional rectangular shape.
  - [ ] Round Cards: Option to generate circular-shaped cards.
  - [ ] Custom Shapes: Support for custom card shapes, e.g., hexagons or ovals.

- [ ] **Icon Placement Options**
  - [ ] Random Placement: Icons are randomly placed on the card.
  - [ ] Grid Placement: Icons are arranged in a grid pattern on the card.
  - [ ] Custom Placement: Users can manually place icons on the card using a drag-and-drop interface.

- [ ] **Icon Orientation**
  - [ ] Random Angles: Icons are placed at random angles on the card.
  - [ ] Fixed Angles: Icons are placed at fixed, user-defined angles.
  - [ ] Dynamic Rotation: Icons rotate dynamically based on user-defined rules (e.g., align with card edges).

- [ ] **Card Design Customization**
  - [ ] Background Customization: Change background colors or add textures.
  - [ ] Border Customization: Add or remove borders, and choose border styles and colors.
  - [ ] Text Overlays: Add customizable text overlays (e.g., game title or card numbers).

- [ ] **Multiple Card Generation Modes**
  - [ ] Single Card Generation: Generate a single card at a time with custom settings.
  - [ ] Batch Generation: Generate multiple cards in one go with consistent or varied settings.
  - [ ] Template-Based Generation: Use predefined templates for rapid card generation.

- [ ] **Export and Sharing Options**
  - [ ] PDF Export: Export generated cards as a high-quality PDF.
  - [ ] Image Export: Save cards as image files (PNG, JPG).
  - [ ] Direct Sharing: Share cards directly via email or social media.

- [ ] **Database Integration**
  - [ ] Card Database: Save generated cards to a database for future use.
  - [ ] Game-Specific Collections: Organize cards into collections based on games.
  - [ ] Version History: Track changes and versions of card designs.

- [ ] **User Interface**
  - [ ] Responsive Design: Ensure the card generator works on various devices, including desktops, tablets, and smartphones.
  - [ ] Drag-and-Drop Editor: A user-friendly interface to arrange icons and customize cards interactively.
  - [ ] Preview Mode: Live preview of card designs before final generation.

- [ ] **Advanced Customization**
  - [ ] Icon Size Adjustments: Customize the size of individual icons.
  - [ ] Layering Options: Control the layering of icons and other elements on the card.
  - [ ] Conditional Rules: Set rules for icon placement and design based on game-specific logic.



## Development

Create a virtual environment for dependencies (recommended)
`python -m venv venv`

Install dependencies
`python -m pip install -r requirements.txt`

Run
`python main.py`

Build
`pyinstaller -F main.py`
