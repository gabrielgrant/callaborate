
_Call-aborate_ lets volunteers sign in to call potential supporters. It presents callers with a script and embedded questions, then calls their phone and connects them to the next call recipient. When the call is complete, the caller records the outcome and they are connected to the next number. All info is logged in Redis, and completed call info is stored in a Google Spreadsheet via a Form for easy access.

Demo: http://call.mayday.us

Script
------

You'll need to write a call script, and probably want to change the questions asked. The script (and all of the markup...ew) is in `static/index.html`. Questions' answers should be bound into properties on the scope's `callInfo` object in order to be saved to the server.


Google Form
-----------

You'll need to create a Google form configured to accept public responses. This acts as the backend for collecting the call data.

First, add fields for the caller, callee and call question responses.

For the caller: phone number, email address, first name, last name and zip code.
For the callee: first name, middle name and last name.

You'll also add fields for any additional questions you want callers to ask during the call.


Callee Data
-----------

The app expects to find a CSV file in the `data` directory with the list of people to call.

Required fields:

`first_name`, `middle_name`, `last_name`, `residential_city`, `residential_zip5` & `phone`



Tropo
-----

The outbound calling uses [Tropo](https://www.tropo.com), so you'll need to create an account there.

Create a new app. We want our call script to run on Tropo's server, so for "type of application", select "Scripting API". Press "New Script" to open their in-browser editor, copy the contents of the `tropo_call_script.py` file (in this directory), and paste it into Tropo. Give it some file name and save.

Add a phone number in whichever area you want (likely the area in which you're going to be calling), then click "Create App"

Once the app is created, Tropo will redirect you to your App Details page. At the bottom of the page, you'll find your voice API key.


Testing with Tropo is free, but if you're doing any significant volume, you'll likely want to move your Tropo app into "Production" mode before starting the call campaign. Once in production, calls will cost $0.03/minute.


Config
------

You'll likely want to edit the included `config.json.example` (and save it as `config.json`) to include some config info. Note that all this info can optionally be passed as env vars instead of hard coding it.

`TIMEZONE_UTC_OFFSET`: Offset of local timezone from UTC (eg. -4 for Eastern Time)

`CALL_TIME_START`: The hour at which calling should open for the day

`CALL_TIME_END`: The hour at which calling should close for the day

`SECRET`: a random string; doesn't much matter what (used to generate client tokens)

`TEST_CALLEE`: The number that will be dialed when running your app in non-production mode

`TROPO_VOICE_API_KEY`: as the name implies, the API key from your Tropo app

`TEST_CALL_FROM`: a phone number (as a string) to call first for testing the call code

`TEST_CALL_TO`: a phone number (as a string) to call connect to for testing the call code

`CALL_DATA_FORM`: JSON object containing info about the Google Spreadsheet/Form:

- `url` is the `formResponse` URL (ie the page that the form `POST`s to)
- `fields` is a set of mappings describing which Google form fields should be filled with what info. Info can come from the `caller`, `callee`, and `call` fields. Generally only the `call` fields should change to reflect the specific questions asked in the survey.


Redis
-----

All call info is logged to Redis, so you'll need to run a redis server locally while testing.

The app will look for the REDISCLOUD_URL env var (as supplied by the RedisCloud Heroku add-on). If this isn't found, it will fall back to the Redis server in the default location ("redis://localhost:6379/0"; useful for local dev).



Install
-------

To run locally, install requirements with PIP

    pip install -r requirements.txt

Run
---

Once set up, running the app is simple:

Run redis in one terminal:

    redis-server

And the webapp in another:

    python app.py

Deploy
------

The app is designed to be deployed on Heroku. You'll likely want to install [Heroku's command-line client (CLI)](https://toolbelt.heroku.com/) (note that you can create the app through Heroku's control panel and add the `heroku` git remote manually if you don't want to bother installing the Heroku CLI).

First commit any changes you've made (likely to the config file):

    git add config.json
    git commit -m "config changes"

Then create the Heroku app and deploy:

    heroku create mycallerapp
    git push heroku master

This should install and start running the app on Heroku, then show you it's public URL. Test it out to make sure everything is working, then, when you're ready, set the app into "production mode" to start making calls to real people on your list:

    heroku config:set PRODUCTION=true

Happy calling!
