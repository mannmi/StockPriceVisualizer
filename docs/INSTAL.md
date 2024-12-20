# Needed Setup Steps

## Preparation:

- Setting up Docker Containers
- Setting up Django Server (deprecated)

## Run:

- Start Docker Containers
- Start Django Server (deprecated)
- Start UI

---

# Install Docker

Install docker = https://docs.docker.com/engine/install/

---

# Install Django Project venv (deprecated)

<Details>
There is a docker container you can use (django_app)

## 1. Install Python and Pip

Make sure you have Python and Pip installed on your system. You can download Python from python.org.

## 2. Set Up a Virtual Environment

It's a good practice to use a virtual environment to manage dependencies.

```bash
# Install virtualenv if you don't have it
pip install virtualenv

# Create a virtual environment
python -m venv venv
```

### Activate the Virtual Environment

#### On Windows

```cmd
venv\Scripts\activate
```

#### On macOS/Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Install Django

Install Django using pip.

```bash
pip install django
```

## 5. Run Django Server

Modify the database information in \`docker-compose.yml\`.

Change into the project directory:

```bash
cd django_project
```

### Apply Migrations

Apply initial migrations to set up the database.

```bash
python manage.py migrate
```

</Details>

---

# Installing Ui enviroment

Install Python and Pip

Make sure you have Python and Pip installed on your system. You can download Python from python.org.


## Install manually
<Details>

## 1. Set Up a Virtual Environment


```bash
# Install virtualenv if you don't have it
pip install virtualenv

# Create a virtual environment
python -m venv venv
```

## 3. Activate the Virtual Environment

#### On Windows

```cmd
venv\Scripts\activate
```

#### On macOS/Linux

```bash
source venv/bin/activate
```

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Add PYTHONPATH

---

### 4.1 On Windows

(power shell)
```bash
  $env:PYTHONPATH = "$env:PYTHONPATH;.\app;.\app\src"
```
(cmd)
```bash
  set PYTHONPATH=%PYTHONPATH%;.\app;.\app\src
```

### 4.2 On Linux
```bash
  export PYTHONPATH=$PYTHONPATH:/app/:/app/src/
```

---

</Details>

## Install using setup.py (Recommended)
<Details>

### Run setup
```bash
python ./setup.py
```



</Details>

---

# Notes

Please don't hesitate to ask questions in the discussion tab :)
On how to run the Applications See [run.md](./RUN.md)