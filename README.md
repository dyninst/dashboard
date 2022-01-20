# Dyninst Dashboard

This dashboard shows Dyninst Testsuite results. 

## Usage

### 1. Install

You'll need to create a virtual environment and install dependencies there:

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install -e .
```

Note that the above does a local, development install. It is setup as a Python package to make
this easy, but is not intended to be installed to system python as it relies on [manage.py] and
other assets to run.

### 2. Development

If you want to run a development server, you should first make migrations:

```bash
$ python manage.py collectstatic
$ python manage.py makemigrations main
$ python manage.py makemigrations users
$ python manage.py migrate

$ python manage.py runserver
Performing system checks...

System check identified no issues (0 silenced).
January 15, 2022 - 19:03:26
Django version 4.0.1, using settings 'ddash.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

This means that the application is running on port 8000. You can adjust this:

```bash
$ python manage.py runserver 127.0.0.1:5000
```

## Development 

These are development notes. @hainest and @vsoch design discussion is in [docs/models.md](docs/models.md)

## Refactor

To refactor, we need to still be able to support running in the current place of deployment.
This likely means we won't have access to containers, and so we will use a virtual environment
and start with sqlite.

### Technology to try

 - Django
 - virtual environment setup
 - sqlite
 - Python 3.6x

We only really need to keep results from December 2021 forward. 
Token on the command line.

### Discussion and Questions 

 - Does the server allow containers?
 - Data format for new logs?
 - Front end UI
 - Search Feature (across fields)
 - Collaborator Account?
 
## Local install for testing/debugging (dashboard developers only)

Before running the server locally, you need to create a test database. Before proceding, ensure that SQLite3 and its Python3 bindings are installed. From the source repository directory, run the following commands.

	> sqlite3 results.sqlite3
	>  .read sql/setup.sql
	>  .exit
 
### Testing with a local Apache server

It is a good idea to test any changes with a local Apache server before handing off the distribution to a web administrator. To do that, you first need to install Apache2 and the Python3 version of the mod_wsgi package. Under Ubuntu, you can do this with

	> sudo apt-get install apache2 libapache2-mod-wsgi-py3

Next, add the source directory (hereafter assumed to be `/home/user/paradyn/dashboard`) to Apache's known directories. This is done by adding the following lines to `/etc/apache2/apache2.conf`.

	<Directory /home/user/paradyn/dashboard>
		Options Indexes FollowSymLinks
		AllowOverride None
		Require all granted
	</Directory>

Next, create a virtual host by copying (as root) the `dashboard.conf` file to `/etc/apache2/sites-available/`. Edit the configuration file to point to your installation by changing all instances of `/var/www` to `/home/user/paradyn`. DO NOT COMMIT ANY EDITS TO THIS FILE.

Next, activate the virtual host: `sudo a2ensite dashboard`.

Next, set the file permissions to the Apache web user group (usually `www-data`).

	> sudo chgrp www-data .
	> sudo chgrp www-data logs
	> sudo chgrp www-data results.sqlite3
	> chmod 0664 results.sqlite3

Finally, restart the Apache server: `sudo service apache2 restart`.

The site is then accessible as `http://localhost/dashboard`.

## License

 * Free software: Apache License 2.0 or MIT.
