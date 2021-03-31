# Capstone project Full Stack Nanodegree 

## Introduction
This is the last project of the Full stack nanodegree program covering several technincal areas of web and API development. In particular this will cover areas such as:

1.  Database modelling in Postgres and SQLAlchemy libraries to abstract interaction with the database
2. API development using Flask and CRUD operations
3. 3rd party autherization, and permission setup through Auth0
4. Cloud deployment through Heroku

## Getting Started

Clone the repo and `cd` into the starter folder. You'll need `python3` and `postgres` running on your local machine

create a virtual environment and activate using the command
```
virtualenv -p python3 venv/
source venv/bin/activate
```

then the next step is to install libraries
```
pip install -r requirements.txt
```
Since we are running the project locally we will need to setup all the env variables inside the `config.py` file.

Change the postgres database config variables to reflect the databse running locally.


in order to startup the Flask server run the following
```
export FLASK_ENV=development
export FLASK_APP=app.py
flask run --rerun
```

the --rerun flag is used for the server to auto update whenever a change in the code is detected. It is optional

## API Documentation

The API has two endpoints 
- `/actors`
- `/movies`

each of these endpoints has the following methods
- GET
- POST
- DELETE
- PATCH

Certain methods are only accessible with the right role which has specific permission to access the underlying resource.

#### [GET] /actors

