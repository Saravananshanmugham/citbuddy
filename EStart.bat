@echo off
IF EXIST IR40.db (
	echo Database Already Exist, Starting Application >&2
	set FLASK_APP=Project_IR40.py
	set FLASK_ENV=development
	flask run --host=0.0.0.0
) ELSE (
	echo Database Does Not Exist, Creating Database >&2
	python backend_setup.py
	set FLASK_APP=Project_IR40.py
	set FLASK_ENV=development
	flask run --host=0.0.0.0
)