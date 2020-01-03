# Dumb price tracker

## Table of contents

1. [Project summary](#project-summary)
2. [Technical summary](#technical-summary)
3. [Possible improvements](#possible-improvements)
4. [Usage](#usage)

## Project summary

I was in need of keeping tabs on the prices of a couple of items I needed. Scarcity was an issue, so I couldn't just check the websites and buy when the price was low; so I had to resort to automation to not miss the price slash!

This is something I hacked this together in very little time (like an hour total? not flexing tho, it's just very simple software) and was particularly targeted at two websites that luckily exposed the item price via schema.org `itemprop price` for easy parsing.

This is not good software in the sense of being amazingly written, masterfully planned and being commented and documented, but it's good software in the sense that does one thing and does it well. Or at least it did it well for my use case.

I decided to share the code for two main reasons:

- to document the systems part of it (service file mainly, which I always forget and need to find around),
- in case some **very** junior dev passes here and takes a quick glance at something that might inspire him/her.

In any case, again: this is not good or production ready or complete in any form software. It's just a simple utility that did something useful for me without a lot of setup and tons of libraries.

If you decide to use it, remember to check your parsing logic by running it manually.

## Technical summary

The project is composed of two parts: the first is a Python website scraper that uses [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/) and [Requests](https://requests.readthedocs.io/en/master/) to get data from a list of websites, and sends an email with [Yagmail](https://github.com/kootenpv/yagmail) when the condition in the logic is verified (price increase/decrease). I used fake user agents but requested at a very slow rate (once every 30 minutes), to respect other people bandwidth and work. This might be not ethical, but I think a single request every 30 minutes is fair.

The other part is just a [Flask](https://www.palletsprojects.com/p/flask/) route that reads the data and outputs HTML, served via [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/). This is not essential but was just a failsafe, another way of reading the parsed data.

As I'm not familiar with Flask and Django was way too much config and setup for something this simple, I just avoided to configure a DB or Celery jobs and choose to record everything in an INI file. This is totally a bad choice, but `configparser` from the Python standard library makes it pretty easy to use INIs for simple data recording.

## Possible improvements

Well, add a DB! Even just a SQLite one would be useful and pose little to none performance problems at low usage, to track history and output it with something like [D3.js](https://d3js.org/).

The price parsing is VERY targeted, with castings to `float` that may fail in some cases and obviously not every site uses schema.org attributes.

In general, everything is too coupled.

Well, it can be improved a lot. I might take a stab at it whenever I have some free time, which might be _never_.

## Usage

This section is valid for an Ubuntu 18.04 server.

Clone the project or download it and put it in any directory you want.

### Setup the Scraper

Edit your sites in the `SITES` const in `scraper.py`. The slug is for saving them in INI sections.

```bash
# Create a virtualenv and source it
user@machine:~/projectdir$ python3 -m venv env
user@machine:~/projectdir$ source env/bin/activate
# Install requirements
(env) user@machine:~/projectdir$ pip install -r requirements.txt
# Put the scraper in your crontab (please don't hammer other people websites)
(env) user@machine:~/projectdir$ crontab -e
# Use something like this:
# */30 * * * * cd foo && foo/env/bin/python foo/scraper.py
# */30 * * * * = scrape every 30 minutes. Use crontab.guru to make your cronstring if you need another :)
# foo = Absolute path to your directory, something like /home/user/dumbtracker
# The absolute paths are needed for venv to work.
```

### Flask webapp

```bash
# Let's create a Systemd unit file to start everything.
# Use whatever you want for the .service filename.
# Just remember this is the name we will use to start/stop/enable/disable via systemctl.
(env) user@machine:~/projectdir$ sudo nano /etc/systemd/system/tracker.service
```

Copy this unit file and fill the blanks:

```ini
[Unit]
Description=Dumb Price Tracker
After=network.target

[Service]
User=
Group=
Restart=always
RestartSec=60
WorkingDirectory=
Environment=
ExecStart=

[Install]
WantedBy=multi-user.target
```

- `User, Group`: use your username for both;
- `WorkingDirectory`: use the absolute path to your project directory, the same that we used before as `foo`;
- `Environment`: use `"PATH=foo/env/bin"`;
- `ExecStart`: use `foo/env/bin/gunicorn --bind 127.0.0.1:5000 app:app`.

Now:

```bash
(env) user@machine:~/projectdir$ sudo systemctl daemon-reload
(env) user@machine:~/projectdir$ sudo systemctl start tracker
(env) user@machine:~/projectdir$ sudo systemctl enable tracker
```

### Nginx

To serve the Flask routes we need a reverse proxy to point at gunicorn. Nginx is ok. Please read some guides if you need help installing it.

This is the most basic server block needed to correctly proxy to gunicorn:

```nginx
server {
    location / {
        proxy_pass http://127.0.0.1:5000;
    }
}
```
