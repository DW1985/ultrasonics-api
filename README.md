![](.github/ultrasonics-api-logo.svg)

---

## The api proxy for ultrasonics.

This is the source code for the ultrasonics-api proxy server. It's purpose is to store private api keys for services such as Spotify, Deezer, and Last.fm, while providing an endpoint for ultrasonics to access those apis.

<br/>

## **Option 0:** Use the official hosted `ultrasonics-api`.

There is an official hosted version at [https://ultrasonics-api.herokuapp.com/api/](https://ultrasonics-api.herokuapp.com/api/).
Feel free to use that instead of hosting your own version. Therefore, no setup is required, and you can get started on curating your perfect playlistys. Or you can run it yourself, it's up to you 😊.

<br/>

## **Option 1:** Host your own Heroku instance.
Follow the [official instructions](https://devcenter.heroku.com/articles/git#creating-a-heroku-remote) after cloning this repo. You will need to use the environment variable `USE_REDIS=True` and also set up a [Heroku Redis instance](https://devcenter.heroku.com/articles/heroku-redis).

🌤️ This is actually a lot easier than those tutorials appear on first glance, you just need to create them both and get the correct URLs.

You can set up environment variables according to the [official documentation](https://devcenter.heroku.com/articles/config-vars). See [environment variables](#environment-variables).

<br/>

## **Option 2:** Host ultrasonics-api on your own hardware (or a virtual machine).
> Disclaimer: I have only tested this on Linux 🐧. It should work fine on macOS or Windows, but some steps might be different.
1. Clone the repo to your computer.
2. I would recommend creating a virtual environment (`python3 -m venv .venv` to create an environment in the folder `.venv`, then activate it with `source .venv/bin/activate`). 
3. Install the Python dependencies with `pip3 install -r requirements.txt`.
4a. Create a .env file, and fill it with the required environment variables. See [environment variables](#environment-variables).
4b. You can run your own Redis instance and connect to it, but if you're not threaded you might as well disable it with `USE_REDIS = False` for a cleaner install.
5. Run it with `flask run`. You may prefer to [run it as a service](https://blog.miguelgrinberg.com/post/running-a-flask-application-as-a-service-with-systemd).

<br/>

## **Environment Variables**
These environment variables can be applied to your Heroku instance, or saved in a `.env` file in this directory.

If you don't use a service, you can remove it's environment variables.

Most services require you to get an api key / secret by creating an account and setting up an application. Documentation for each service can be found below.

<br/>

### Finding API Keys
| App     | Link                                                                                                                  | Notes                                                           |
| ------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Spotify | [https://developer.spotify.com](https://developer.spotify.com/documentation/web-api/quick-start/#set-up-your-account) | Refer to "Set Up Your Account" and "Register Your Application". |
 
<br/>

### `.env` file
```
FLASK_APP=ultrasonics_api

USE_REDIS=False
REDIS_URL=[Only if USE_REDIS=True]

SPOTIFY_CLIENT_ID=abc
SPOTIFY_CLIENT_SECRET=xyz
```