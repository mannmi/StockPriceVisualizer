#!/usr/bin/bash

# List of required files
REQUIRED_FILES=(
  "/app/requirements.txt"
  "/app/django_project/manage.py"
  "/app/src"
)

# Function to check if all required files exist
check_files_exist() {
  for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -e "$file" ]; then
      return 1
    fi
  done
  return 0
}

# Wait for all required files to exist
echo "Waiting for required files to be available..."
while ! check_files_exist; do
  echo "Required files not found. Retrying in 5 seconds..."
  sleep 5
done
echo "All required files are available."

# Install Django using pip (if not already installed)
pip install django

# Change directory to the Django project
cd /app/django_project

# Run the Django migration command and display the output in real-time
python manage.py migrate

# Start the Django server
python manage.py runserver 0.0.0.0:8000