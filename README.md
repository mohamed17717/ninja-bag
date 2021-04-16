# Django boilerplate (2.2)

to work faster i make this boilerplate according to my needs.

## steps

> ### Commands assume that u are in app root folder

### create virtual env

```bash
virtualenv -p=python3.9 .
source bin/activate
```

### clone this repo

```bash
git clone https://github.com/mohamed17717/django-poilerplate.git src/
cd src
pip install -r requirements.txt
```

then start creating your apps like normal
look in app created to use things like signals and stuff whenever you need

## contain

- [x] settings file handle static vars and templates
- [x] urls to static files
- [x] helper classes (jwt, mail)
- [x] .gitignore
- [x] signals
- [x] decorators
- [ ] most used models & views (authentication, profile, ...)
- [ ] forms
- [ ] add features to admin panel
- [x] app that collect data from every request
- [ ] enable cors
