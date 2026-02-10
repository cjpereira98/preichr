# Startup Guide
## Create a Virtual Environment (First Time Running after cloing from repository)
```bash
$ python -m venv .venv
```

## Activate the Virtual Environment (if not yet activated yet)
Do this whenever a new terminal is initiated.
```bash
# Linux, macOS
$ source .venv/bin/activate

# Windows PowerShell
$ .venv\Scripts\Activate.ps1

# Windows Bash
$ source .venv/Scripts/activate
```

## Upgrade pip
Make sure the virtual environment is active (with the command above) and then run:
```bash
$ python -m pip install --upgrade pip
```


## Quickstart FastAPI Server
```bash
$ ./run_main.sh
```



# Complete Installation Guide

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
$ git clone -b master "\\ant\dept-na\SWF2\Public\Parachute" parachute_master

# Enter into that project directory
$ cd parachute_master
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

## Activate the Virtual Environment (if not yet activated yet)
Do this whenever a new terminal is initiated.
```bash
# Linux, macOS
$ source .venv/bin/activate

# Windows PowerShell
$ .venv\Scripts\Activate.ps1

# Windows Bash
$ source .venv/Scripts/activate
```

## Upgrade pip
Make sure the virtual environment is active (with the command above) and then run:
```bash
$ python -m pip install --upgrade pip
```

## Install Dependencies
```bash
# Install dependencies
$ pip install -r requirements.txt
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
MODEL_DIR = os.path.join(BASE_DIR, 'src')
VIEW_DIR = os.path.join(BASE_DIR, 'app')
CONTROLLER_DIR = os.path.join(BASE_DIR, 'modules')
UTILS_DIR = os.path.join(BASE_DIR, 'utils')
TEST_MODE = True
TEST_EMAIL = OWNER + '@amazon.com'
DUMMY_CONTAINER = 'tsX0xbgyjsb'
HOURLY = "TRUE"
```

### Start API Server
Run Server with:
```bash
$ ./run_main.sh
```

 ╭────────── FastAPI CLI - Development mode ───────────╮
 │                                                     │
 │  Serving at: http://127.0.0.1:8000                  │
 │                                                     │
 │  API docs: http://127.0.0.1:8000/docs               │
 │                                                     │
 │  Running in development mode, for production use:   │
 │                                                     │
 │  fastapi run                                        │
 │                                                     │
 ╰─────────────────────────────────────────────────────╯

INFO:     Will watch for changes in these directories: ['/home/user/code/awesomeapp']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [2248755] using WatchFiles
INFO:     Started server process [2248757]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Test API
Open your browser at http://127.0.0.1:8000/items/5?q=somequery.

### Interactive API docs
**Swagger UI:** go to http://127.0.0.1:8000/docs.
**ReDoc:** go to http://127.0.0.1:8000/redoc.

## Static Pages
Static pages could be found under ./static/
Open your browser at http://127.0.0.1:8000/static/index.html

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
$ source .venv/bin/activate && cd ./modules/jiggle/ && python main.py

# Open new Terminal for subroutine [turbo_ps]
$ source .venv/bin/activate && cd ./modules/turbo_ps/ && python main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ source .venv/bin/activate && cd ./modules/dwelling_inventory/ && python main.py

# Open new Terminal for subroutine [ti]
$ .venv\Scripts\Activate.ps1 && cd ./modules/ti/ && python main.py

# Open new Terminal for subroutine [flex_on_prem]
$ .venv\Scripts\Activate.ps1 && cd ./modules/flex_on_prem/ && python main.py
``` 

### Windows PowerShell
```bash
# Open new Terminal for subroutine [jiggle].
$ .venv\Scripts\Activate.ps1 && python ./modules/jiggle/main.py

# Open new Terminal for subroutine [turbo_ps]
$ .venv\Scripts\Activate.ps1 && python ./modules/turbo_ps/main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ .venv\Scripts\Activate.ps1 && python ./modules/dwelling_inventory/main.py

# Open new Terminal for subroutine [ti]
$ .venv\Scripts\Activate.ps1 && python ./modules/ti/main.py

# Open new Terminal for subroutine [flex_on_prem]
$ .venv\Scripts\Activate.ps1 && python ./modules/flex_on_prem/main.py
```

### Windows Bash
```bash 
# Open new Terminal for subroutine [jiggle].
$ source .venv/Scripts/activate && cd ./modules/jiggle/ && python main.py

# Open new Terminal for subroutine [turbo_ps]
$ source .venv/Scripts/activate && cd ./modules/turbo_ps/ && python main.py

# Open new Terminal for subroutine [dwelling_inventory]
$ source .venv/Scripts/activate && cd ./modules/dwelling_inventory/ && python main.py

# Open new Terminal for subroutine [ti]
$ source .venv/Scripts/activate && cd ./modules/ti/ && python main.py

# Open new Terminal for subroutine [flex_on_prem]
$ source .venv/Scripts/activate && cd ./modules/flex_on_prem/ && python main.py
```

## Optional Packages
### GraphQL - [Strawberry](https://strawberry.rocks/docs/integrations/fastapi)
```bash
$ pip install 'strawberry-graphql[fastapi]'
```

See the example below for integrating FastAPI with Strawberry: 
```python
import strawberry

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


schema = strawberry.Schema(Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

### GUI - [PyQt](https://doc.qt.io/)
* [About PyQt](https://wiki.python.org/moin/PyQt)
* [Handling SQL Databases With PyQt: The Basics](https://realpython.com/python-pyqt-database/)
* [Get and Install Qt](https://doc.qt.io/qt-6/get-and-install-qt.html)

### GUI - [pygame](https://www.pygame.org/)
* [Get Started in Pygame in 10 minutes!](https://www.youtube.com/watch?v=y9VG3Pztok8)

## Creating New Branch
```bash
# Switch to the Master Branch
$ git checkout master          # Switch to the master branch
$ git pull origin master       # Update the local master branch with any remote changes

# Create a New Branch 
$ git checkout -b feature-branch   # Create and switch to the new branch

# Push the New Branch to the Remote Repository (Optional)
$ git push -u origin feature-branch   # Push the branch and set the upstream tracking

# Verify the Branch
$ git branch         # List all local branches
$ git branch -r      # List all remote branches

```

## Create Virtual Environment 
```bash
$ deactivate # Deactivate currenting virtual environment if it's active
$ rm -rf .venv # Remove existing virtual environment folder

# Reinstall environment dependencies
$ python -m venv .venv
```

## Activate the Virtual Environment 
```bash
# Linux, macOS
$ source .venv/bin/activate

# Windows PowerShell
$ .venv\Scripts\Activate.ps1

# Windows Bash
$ source .venv/Scripts/activate
```

## Reinstall Python Modules
``` bash
$ pip install -r requirements.txt
```

## Testing
```bash
$ set PYTHONPATH=.
$ pytest

```