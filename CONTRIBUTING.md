# Contributing to Getting Unstuck Web

Here are some guidelines to contribute to Getting Unstuck Web.

## Getting set up

Clone the repo and follow the instructions in README.md to get set up properly.

If planning to write code and you're not part of the GSE-CCL organization, fork the repository first.

If planning to write code, you'll also want to install a style checker, as by running `pip install yapf`.

### Windows and Celery

Celery sometimes has problems with Windows. In the past, running `set FORKED_BY_MULTIPROCESSING=1`
in the command prompt from which the Celery process will run, before running Celery, has proved useful.

## Catching up

When other people make changes to the repository, you'll want to keep your local
repository up to date (particularly if you push changes and switch back to master).
To do this, run `git fetch`, `git pull` if you're in the changed branch (usually master).

Since many changes may have occurred since your last pull, you'll want to do three
things to make sure your local copy will still work:

1. Check `secure/db.json` and `secure/celery.json` to make sure they still have the correct credentials.
2. Check `lib/settings.py` for changed fields, and to update as necessary.
3. When running the software, login as normal. Resave any schemas you've created (literally by opening and saving them). Redownload any studios you've downloaded. Schemas and studios are the most frequently changed database structures, so resaving these records will prevent most problems caused by those updates.

## Writing code

Check out a branch. Make your changes.

### Before your pull request

Check that your code meets our style requirements (basically a slightly modified pep8). Two ways to do this:

- Get a diff of what you need to change: run `yapf -rd .` from the root repository directory. Then make the changes.
- Automatically change your code to meet our style: run `yapf -ri .` from the root repository directory.

Check that your code passes the tests.

- Run `python -m pytest tests`.

### Pull request

We'll review your pull request, make any requests for changes, and possibly merge into the main codebase if all is good.

