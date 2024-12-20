### Run Docker

```bash
docker-compose up --build
```

---

### Run the Development Server (deprecated see install.md)

<details>
Start the Django development server.

```bash
python manage.py runserver
```
</details>

### Access the Django API

Open your web browser and go to http://127.0.0.1:8000/ to see your Django project running.

---

# Start Up UI

## Start venv environment

### On Windows

```cmd
venv\Scripts\activate
```

### On macOS/Linux

```bash
source venv/bin/activate
```

## Add PYTHONPATH

---

### On Windows

Option 1)

(power shell)
```bash
  $env:PYTHONPATH = "$env:PYTHONPATH;.\app;.\app\src"
```
(cmd)
```bash
  set PYTHONPATH=%PYTHONPATH%;.\app;.\app\src
```

### On Linux
```bash
  export PYTHONPATH=$PYTHONPATH:/app/:/app/src/
```

---

Option 2)
````bash
python setup.sh
````

---

## Start the enviroment
set PYTHONPATH=%PYTHONPATH%;C:\path\to\your\venv


Run the UI application with:

```bash
python ui/appDemoAsync.py
```

---

# Notes
Please don't hesitate to ask questions in the discussion tab :)