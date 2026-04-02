# Fractal Jr.

# To build from source for your machine, download the source code then set up a python3 virtual
# environment in the folder, download the requirements and build with auto-py-to-exe

# Alternatively, there's a version written to just be run in Python with the minimum requirements
# (just pygame-ce and numpy) in the "venv-build" branch

# These instructions are written on MacOS so they should probably work for Linux!
# I'll get around to writing Windows instructions eventually.

# Originally built with Python 3.14.2
# If it doesn't work in a newer Python version, try this one!

# To open a virtual environment, go to the folder and open a terminal
#   python3 -m venv .venv
#   source .venv/bin/activate
# If that doesn't work you probably don't have Python installed yet, easy fix.
# Once you have (.venv) showing in the terminal, type: 
#   pip install -r build-requirements.txt
#   auto-py-to-exe

# A UI window should pop up. Go down to the "Settings" category and open it. All the way
# at the bottom you'll see a button like "Import Config From JSON File", click that
# and navigate to "auto py to exe settings.json" in the source code folder.

# Scroll back up to the top and make sure the "Console Window" option now has
# 'Window Based' selected to confirm the import worked.

# It should have a lot of the settings ready to go but you'll need to point the program
# to your machine's path:
#   - for Script Location, the main script: 'fractal_junior.py'
#   - for Additional Files, point it to the following folders in the downloaded
#           source folder: src, assets, exports
#   - for Output (back down in Settings) choose a location to put the data folder and the
#           built application
#   - for Icon, on Mac specifically, I've had trouble with .ico and Pillow so you may need to
#           point it to the .icns file included in src/assets. It will say it's not a valid
#           .ico file, ignore it.
# Click the big blue button to convert! It says .exe but it will make the appropriate
# type for your machine.