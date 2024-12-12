# Doker Installation Guide
install docker modifie the docker-compose.yml to suite your use :)

```bash
docker-compose up --build
```


# Django Project Installation Guide

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

# Activate the virtual environment
## On Windows
```cmd
venv\Scripts\activate
```
## On macOS/Linux

```bash
source venv/bin/activate
```


## 3. Install Django
Install Django using pip.
```
pip install django
```

## 4. Run Django Server
Modifie The Database Information in docker-compose.yml

7. Apply Migrations
Apply initial migrations to set up the database.
```bash
python manage.py migrate
```

8. Run the Development Server

Start the Django development server.
```bash
python manage.py runserver
```
9. Access the Project
Open your web browser and go to http://127.0.0.1:8000/ to see your Django project running.

# Start up ui 
Run the ui application with 
```bash
python ui/appDemoAsync.py
```

# Notes
Please dont mind asking question in the :) discussion tab
