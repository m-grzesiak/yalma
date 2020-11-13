# yalma

## Usage

1. Install required dependencies by `pip install -r requirements.txt`
2. Run the application by `python yalma.py` ;)

Before you run the app, please create a `config.ini` file at `$HOME/.config/yalma/` path:

```ini
[luxmed]
username = 
password = 
language = en

[email_settings]
username = 
password = 
smtp_server = 
smtp_port = 
```

### Luxmed section
* you have to provide your `username` and `password` there;
* `language` position has 2 possible values: `en` or `pl` - this setting has not any influence on returned data 
(like specialization names) from the Luxmed system - it only defines the language of errors you can receive from that
 API. 
 
 ### Email settings section
 These are settings for sending email to you when any visits are available.
 * `username` and `password` is pretty obvious ;)
 * SMTP server and port depend on your mail server. For instance, for Gmail it will be `smtp.gmail.com` and `465` 
 as a port.