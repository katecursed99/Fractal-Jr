# Fractal Jr.

# These instructions are written on MacOS but also worked on my Ubuntu (Linux Mint) machine with a few very minor tweaks (a few extra dependencies that didn't ship with Linux Python, just installed them when terminal said so). Windows users may need to seek additional resources. If you build for Windows before I get to it, please consider contributing documentation! <3

# * If you just want to run the program in a Python3 environment, you can install min-requirements to a venv (instead of build-requirements) and fire up fractal_junior.py from the terminal. The rest of the requirements are for when building it to an app.

# To build from source for your machine, download the source code then set up a python3 virtual environment in the folder, download the requirements and build with auto-py-to-exe

# To open a virtual environment, go to the folder and open a terminal
#   python3 -m venv .venv
#   source .venv/bin/activate
#  If that doesn't work you probably don't have Python installed yet, easy fix.
#  Once you have (.venv) showing in the terminal, type: 
#   pip install -r build-requirements.txt
#   auto-py-to-exe

# A UI window should pop up. Go down to the "Settings" category and open it. All the way at the bottom you'll see a button like "Import Config From JSON File", click that and navigate to "auto py to exe settings.json" in the source code folder.

# Scroll back up to the top and make sure the "Console Window" option now has 'Window Based' selected to confirm the import worked. (Leave it as 'Window Based' unless you're on your 2nd or 3rd attempt and need debugging messages)

# It should have a lot of the settings ready to go but you'll need to point the program to your machine's path:
#   - for Script Location, the main script: 'fractal_junior.py'
#   - for Additional Files, point it to the following folders in the downloaded source folder: src, assets, exports
#   - for Output (back down in Settings) choose a location to put the data folder and the built application. It defaults to inside the folder, but I like to put it somewhere separate so the source code can be deleted after building
#   - for Icon, you will need to point it to either the .icns icon or the .ico icon. .ico worked on Linux
# Click the big blue button to convert! It says .exe but it will make the appropriate type for your machine.
