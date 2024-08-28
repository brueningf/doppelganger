# Card game generator
This is a simple and collaborative project focused on generating PDFs with rendered cards. Each page of the PDF contains cards that can be printed and cut out for children coordination games. The cards include icons or images of characters, which are randomly positioned and rotated to create unique cards.

The current code is a rough prototype—functioning but far from polished. Contributions in the form of ideas, refactoring, and improvements are highly encouraged! This project is meant as a desktop application written in Python, initially created to explore PyInstaller and can serve as a learning resource for others.

<img src="https://github.com/user-attachments/assets/ac826b1c-6cd3-49c8-b929-63f53968521d" width=35%>
<img src="https://github.com/user-attachments/assets/15a3948c-a2ff-4e7c-98e1-d9978762778a" width=25%>

<img src="https://github.com/user-attachments/assets/be95351b-6f90-4d03-bcdf-4bdad37a3fec" width=15%>


## Development

Create a virtual environment for dependencies (recommended)
`python -m venv venv`

Install dependencies
`python -m pip install -r requirements.txt`

Run
`python main.py`

Build
`pyinstaller -F main.py`
