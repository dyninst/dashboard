# Migration

This is a quick script to download a previously existing database and then update the models here.
First, retrieve the database (fine to do this from the root):

```bash
$ wget https://ftp.cs.wisc.edu/paradyn/results.sqlite3
```

Then there is an internal commant to do the import.

```bash
$ python manage.py import_db results.sqlite3
sqlite3 database is: results.sqlite3
Adding TestMode
Adding Compiler
Adding TestRun
Adding Regressions
```

Note that it will take a while to add TestRun (there are quite a few).
