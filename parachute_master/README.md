# Installation Guide

## Create parent Project folder
```bash
# Create a base directory for all your projects
$ mkdir company_projects

# Enter into that code directory
$ cd company_projects
```

## Clone Parachute (previously called MICHAEL) Engine 
Open CMD
```bash
# Create a directory for this project
$ git clone "\\ant\dept-na\SWF2\Public\MICHAEL"

# Enter into that project directory
$ cd MICHAEL
```

## Create a Virtual Environment
```bash
$ python -m venv .venv
```

## Check the Virtual Environment is Active
```bash
# Linux, macOS, Windows Bash
$ which python
/home/user/code/awesome-project/.venv/bin/python

# Windows PowerShell
$ Get-Command python
C:\Users\user\code\awesome-project\.venv\Scripts\python
```

## Upgrade pip
Make sure the virtual environment is active (with the command above) and then run:
```bash
$ python -m pip install --upgrade pip
```

## Add .gitignore
If you are using Git (you should), add a .gitignore file to exclude everything in your .venv from Git. Do this once, right after you create the virtual environment. Create a file .venv/.gitignore with:
```python
# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Configs
config.py
.config

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
```

## Add .env

Open up File Explorer and trace the following path structure to your specific Mozilla profile directory name. Replace the following command with your particular path.
```bash
$ echo "FIREFOX_PROFILE_DIR=c:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\xxxxxx.default-esr" > .env
```

## Add config.py
Create a file ./config/config.py with:
```python
#config.py
import os
OWNER = '' #Login. Replace with Admin's Amazon id.
BADGE = '' #badge id for fcmenu. Replace with Admin's Amazon badge id.
FCMPASS = '' #password for fcmenu secure mode. Replace with Admin's Amazon password.
FC = '' #Facility id. Replace with target facility. ex: SWF2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
UTILS_DIR = os.path.join(BASE_DIR, 'utils')
TEST_MODE = True
TEST_EMAIL = OWNER + '@amazon.com'
DUMMY_CONTAINER = 'tsX0xbgyjsb'
HOURLY = "TRUE"
```

## Install Parachute Dependencies
```bash
# Install Parachute dependencies
$ pip install -r requirements.txt
```

## Activate the Virtual Environment 
Do this whenever a new terminal is initiated.
```bash
# Linux, macOS
$ source .venv/bin/activate

# Windows PowerShell
$ .venv\Scripts\Activate.ps1

# Windows Bash
$ source .venv/Scripts/activate
```


## Start Parachute Subroutines
Make sure to activate the Virtual Environment when opening a new terminal. See steps above. 
### Linux, macOS
```bash
# Open new Terminal for subroutine [jiggle].
$ source .venv/bin/activate && cd ./scripts/jiggle/ && python main.py

# Open new Terminal for subroutine [turbo_ps]
$ source .venv/bin/activate && cd ./scripts/turbo_ps/ && python main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ source .venv/bin/activate && cd ./scripts/dwelling_inventory/ && python main.py

# Open new Terminal for subroutine [ti]
$ .venv\Scripts\Activate.ps1 && cd ./scripts/ti/ && python main.py
``` 

### Windows PowerShell
```bash
# Open new Terminal for subroutine [jiggle].
$ .venv\Scripts\Activate.ps1 && cd ./scripts/jiggle/ && python main.py

# Open new Terminal for subroutine [turbo_ps]
$ .venv\Scripts\Activate.ps1 && cd ./scripts/turbo_ps/ && python main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ .venv\Scripts\Activate.ps1 && cd ./scripts/dwelling_inventory/ && python main.py

# Open new Terminal for subroutine [ti]
$ .venv\Scripts\Activate.ps1 && cd ./scripts/ti/ && python main.py
```

### Windows Bash
```bash 
# Open new Terminal for subroutine [jiggle].
$ source .venv/Scripts/activate && cd ./scripts/jiggle/ && python main.py

# Open new Terminal for subroutine [turbo_ps]
$ source .venv/Scripts/activate && cd ./scripts/turbo_ps/ && python main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ source .venv/Scripts/activate && cd ./scripts/dwelling_inventory/ && python main.py

# Open new Terminal for subroutine [ti]
$ source .venv/Scripts/activate && cd ./scripts/ti/ && python main.py
```