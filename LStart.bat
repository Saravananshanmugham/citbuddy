@echo off
IF EXIST IR40.db (
	echo Database Already Exist, Starting Application >&2
	set FLASK_APP=app.py
	set FLASK_ENV=development
	flask run
) ELSE (
	echo Database Does Not Exist, Creating Database >&2
	python backend_setup.py
	set FLASK_APP=app.py
	set FLASK_ENV=development
	flask run

)