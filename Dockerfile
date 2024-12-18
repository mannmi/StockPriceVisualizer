# Use an official Python runtime as a parent image
FROM python:3.9

ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app
#RUN python data/mongoDB/generatSetupMongo.py

# Run a Python script to modify the docker-compose.yml as well as other configs


#virtul env
#RUN python3 -m venv /opt/venv
 #ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

RUN apt-get update && apt-get upgrade -y
# Upgrade pip and install required python packages
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install dependencies

# Set environment variables for Qt
ENV QT_X11_NO_MITSHM=1

# Copy the current directory contents into the container at /app
COPY . /app

#bind in read only mode :)
#docker run -v ./data/mongoDB/setup.js:/docker-entrypoint-initdb.d/init-mongo.js:ro mongo-init

#lets see if this fixes my issue with the conf not bein there :)
COPY docker-compose.yml .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run appDemoAsync.py when the container launches
CMD ["python","-u", "src/server/main.py"]
# (could a way to create unit config.yml CMD ["sh", "-c", "if [ \"$RUN_TESTS\" = \"true\" ]; then python -m unittest discover; else python appDemoAsync.py; fi"]