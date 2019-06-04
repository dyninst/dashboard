#!/bin/bash

cleanup () {
	rm -rf dist/
}

init=0

if test "$1" = "--init"; then
	init=1
fi

base_files="bottle.py dashboard.py dashboard.wsgi log_files.py"
sql_files="sql/__init__.py sql/bottle_sqlite.py sql/inserts.py sql/views.py"
views_files="views/regressions.tpl views/runs.tpl views/upload.tpl"


mkdir -p dist dist/sql dist/views dist/logs
cp $base_files dist/
cp $sql_files dist/sql
cp $views_files dist/views

if test "$init" = "1"; then
	if test ! -f results.sqlite3; then
		echo ERROR missing 'results.sqlite3'. See README for instructions.
		cleanup
		exit
	fi
	cp results.sqlite3 dist/
	echo !!! WARNING: Copying this distribution to the web server will DESTROY the existing database there. !!!
fi

tar -C dist -zcf dashboard.tar.gz .

cleanup
