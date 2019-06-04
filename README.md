# Dashboard for Dyninst and its Testsuite

## Local install for testing/debugging (dashboard developers only)

Before running the server locally, you need to create a test database. Before proceding, ensure that SQLite3 and its Python3 bindings are installed. From the source repository directory, run the following commands.

	> sqlite3 results.sqlite3
	>  .read sql/setup.sql
	>  .exit
 
### Testing with Bottle's built-in server

To run the server, you just execute the main Python file.

	> python3 dashboard.py

The site is then accessible as `http://localhost`.

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

Finally, restart the Apache server: `sudo service apache2 restart`.

The site is then accessible as `http://localhost/dashboard`.

## Creating a distribution tarball

To create the distribution tarball (`dashboard.tar.gz`), run `make_dist.sh` in the source directory. When creating a brand new website, pass the `--init` option to `make_dist.sh`. This will include the `results.sqlite3` database file in the distribution. Of course, you will want to ensure that the database is empty (see instructions above for how to create an empty database).

Once complete, send this file to your web admin for installation.
