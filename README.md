# COVID Dashboard <img src="static/images/fish.gif" width="50" height="50">

### What _COVID_DASHBOARD_ does...

* Provides a web-based dashboard for viewing COVID-19 statistics and news, all in one place.
* Highly configurable, choose your own title, images, favicon and more!
* Can be quickly setup to work for any location within the UK.
* Easily extendible, with well structured and clearly documented code .
* Get up and running in under two minutes!

### What you need...

| Dependency | Version |
| :--------- | ------: |
| Python     |   3.8.9 |
| Flask      |   2.0.2 |
| pytest     |   6.2.5 |
| requests   |  2.26.0 |
| uk-covid19 |   1.2.2 |

**Note.** everything but python can be automatically installed using `venv`.

### How to get started...

1. Open the folder you would like install the dashboard into in your terminal/command prompt and run

```console
    python -m venv .venv
```

to create a virutal environment. If you're on MacOS use `python3` instead

```console
    python3 -m venv .venv
```

2. Enter the python virtual environment

```console
    source .venv/bin/activate
```

on MacOS, or the following on Windows

```console
    .venv\bin\activate.bat
```

3. Now, in the virtual environment, run

```console
    pip install -e .
    pip install -r requirements.txt
```

to install the dashboard and its dependencies.

4. Run the dashboard for the first time with

```console
    python app.py
```

to generate a new `config.json` file.

5. Modify `config.json` with your location, nation, and API key from NewsAPI.org.

6. Restart the dashboard then visit <http://127.0.0.1:5000/> to view your local COVID data and news!

### Development
The dashboard was written with the idea of modification and tweaking in mind, so it should be fairly easy to extend it however you please.

Format the code with
```console
    black filename.py
```

And make sure to run the tests with
```console
    pytest .
```
in the projects root directory.

### License
[The MIT License](LICENSE)