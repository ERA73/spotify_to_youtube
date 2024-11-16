# spotify_to_youtube

## Seting up Spotify
You must to set up Spotify Developers using **http://localhost:8888/callback/** as redirect url and get the ***client*** and ***secret***

## Seting up Youtube
You must to activate ***YouTube Data API v3*** service, create an ***OAuth 2.0*** user and download the ***credentials.json*** file, it has a structure as follows:
``` json
{
    "installed": {
        "client_id": "",
        "project_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "",
        "client_secret": "",
        "redirect_uris": [
            "http://localhost"
        ]
    }
}
```

Each query of a song spend 100 points of your youtube quota (10.000)

## create **.env** file
Create this file to load the Spotify credentials as environment variables.
```
SPOTIFY_CLIENT=your_client
SPOTIFY_SECRET=your_secret
```