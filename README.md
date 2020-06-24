[![Build Status](https://travis-ci.com/GSE-CCL/getting-unstuck-web.svg?branch=master)](https://travis-ci.com/GSE-CCL/getting-unstuck-web)

# Getting Unstuck Web

This is the web app for Getting Unstuck, a Scratch learning experience developed by the Creative Computing Lab at the Harvard Graduate School of Education.

## Requirements

- OS: tested on Windows 10, Mac, and Linux
- [Python](https://www.python.org/) 3.7 or higher
- [MongoDB](https://www.mongodb.com/) 4.0 or higher
- [RabbitMQ](https://www.rabbitmq.com/download.html) 3.8 or higher
- (*Production*) Server software, like Apache or Nginx

## Setup

Assuming all the dependencies above are met, you'll need to do the following to get the web app running:

1. Clone this directory.
2. In the `secure` subdirectory, copy `celery.json.example` to `celery.json`. In `celery.json`, change `name` to be the app name. The `broker_url` is the [Celery broker](https://docs.celeryproject.org/en/stable/getting-started/brokers/index.html) URL for task management. The `result_backend` is the [Celery result backend](https://docs.celeryproject.org/en/latest/userguide/configuration.html#conf-result-backend) URL for task management.
3. In the `secure` subdirectory, copy `db.json.example` to `db.json`. In `db.json`, type in your database credentials. If you have a database URI, copy that into the `host` field.
4. Open `lib/settings.py` in a text editor. Change the fields as necessary.
5. In the repository directory, create a Python virtual environment of your choice. Activate the virtual environment and run `pip install -r requirements.txt` to install the Python dependencies.

## Running the server

In a development environment, running the server is simple.

1. Make sure the MongoDB and RabbitMQ servers are running.
2. Navigate to the repo directory and activate the virtual environment in two terminal windows/tabs.
3. In the first terminal window, run `flask run`.
4. In the second terminal window, run `celery -A app.celery worker --pool=solo -l info --loglevel=warning`.
5. Navigate to `http://localhost:5000` in your browser to start using the web app. When first setting up the server, go to `http://localhost:5000/setup` to set up the first admin user.
