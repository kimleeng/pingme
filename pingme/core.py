# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_core.ipynb.

# %% auto 0
__all__ = ['get_config', 'Card', 'PingMe', 'cli']

# %% ../00_core.ipynb 9
# Inlcuded libraries, other libraries are included with the methods that use them.
# FIXME: Currently this is not showing in the docs, currently it seems no librs are
from fastcore.utils import patch # decorator to patch in new methods to a class

# %% ../00_core.ipynb 14
from dotenv import dotenv_values # for loading config from .env files
import os

def get_config(config_path) -> dict:
    # Order of precedence: environment variables > .env file > default values
    if config_path is None:
        return {
            **dotenv_values("./config/config.default.env"),       # load global default vars
            **os.environ,                                         # override loaded values with ENV variables
            'PROJECT_PATH': os.getcwd()                           # set the project path relative to notebook
        }
    else:
        return {
            **dotenv_values("./config/config.default.env"),       # load global default vars
            **dotenv_values(config_path),                         # g is stored in ENV variable DEMUX_ILLUM_CONFIG_PATH
            **os.environ,                                         # override loaded values with ENV variables
            'PROJECT_PATH': os.getcwd()                           # set the project path relative to notebook
        }

# %% ../00_core.ipynb 22
from pydantic import BaseModel
class Card(BaseModel):
    name: str
    context: dict

# %% ../00_core.ipynb 24
import json # to manage json payloads
from pathlib import Path # for type hinting and file checking
import os
class PingMe:
    """
    PingMe class which notifies via either a webhook or email
    """
    def __init__(self,
                 card: Card, # Card object
                 card_dir: Path, # Path to card directory
                 card_ext: str): # Extension of card file
        self.card = card
        self.card_path = os.path.join(card_dir, f"{self.card.name+card_ext}") # built here to limit user options on api
        self.payload:json = None # Stores the unresolved payload contents
        self.title = self.card.context.get('title', None)
        self.text = self.card.context.get('text', None)

        #Check if payload_file is a valid path
        if not Path(self.card_path).is_file():
            raise ValueError(f"Payload file does not exist {self}")

        with open(self.card_path, 'r+') as f:
            content = f.read()
            self.payload = json.loads(content)

    def __str__(self) -> str:
        return (
        f"""PingMe object with:
    card: {self.card}
    card_path: {self.card_path}
    payload:
{json.dumps(self.payload, indent=4, sort_keys=True)}"""
     )
    def __repr__(self) -> str:
        return self.__str__()

# %% ../00_core.ipynb 28
import re # regular expression for parsing

@patch
def resolved_payload(self:PingMe) -> str:
    """
    Resolves the payload by substituting variables in the `self.payload` with values from the `self.payload_context` and ensures all variables are accounted for
    """
    if self.payload is None:
        # Ensure there is a payload
        raise ValueError("Payload is None")
    str_temp = json.dumps(self.payload) # convert payload to string
    for key in self.card.context.keys():
        # Substitute all variables in payload with values from payload_context, it can also be set up that their are no variables in the payload
        str_temp = str_temp.replace("${"+key+"}", self.card.context[key])
    if re.search("\${.*}", str_temp):
        # Check if there are any variables left, this is not allowed
        raise ValueError("Unresolved variables in payload")
    return str_temp

# %% ../00_core.ipynb 31
import requests # to send requests to webhooks

@patch
def send_to_webhook(self:PingMe, url:str) -> dict:
    """
    Send the payload to a provided webhook `url` and returns response info when possible
    """
    webhook_header = {'Content-Type': 'application/json'}
    if url is None:
        raise Exception("Webhook URL not set")
    # Send message to webhook
    try:
        response = requests.post(url, data=self.resolved_payload(), headers=webhook_header)
    except Exception as e:
        raise Exception(f"Error sending message to webhook: {e}")
    return {"status_code": response.status_code, "response": response.text}

# %% ../00_core.ipynb 37
import smtplib # to send emails
import email.mime.text # to format emails

@patch
def send_to_email(self:PingMe, email_from:str, email_to:str, smtp_host:str, smtp_port:int=25, smtp_username=None, smtp_password=None) -> bool:
    email_status = False
    html_content = f"""
    <html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=us-ascii">
        <script type="application/adaptivecard+json">
            {self.resolved_payload()}
        </script>
    </head>
        <body>
            This is a sample body
        </body>
    </html>
    """
    msg = email.mime.text.MIMEText(html_content, 'html')
    msg['Subject'] = self.title
    msg['From'] = email_from
    msg['To'] = email_to
    email_connection = smtplib.SMTP(smtp_host, smtp_port)
    try:
        email_connection.ehlo()
        email_connection.starttls()
        email_connection.ehlo()
        email_connection.login(smtp_username, smtp_password)
        email_connection.sendmail(email_from, email_to, msg.as_string())
        email_status = True
    finally:
        email_connection.quit()
        return email_status


# %% ../00_core.ipynb 43
import datetime # to get current date and time which is used in logging

@patch
def send_to_log_file(self:PingMe, log_file:str) -> bool:
    """
    Send message to log_file
    TODO: The log file only lods title and text right now (not payload), while payload can be included it is not good for parsing. Need to think of a solution for this. Could be to save each payload as a seperate file and the log is a list of files.
    """
    if log_file is None:
        raise Exception("Log file not set")
    with open(log_file, "a") as f:
        # Write the current time
        f.write(f"{datetime.datetime.now()}\t{self.title}\t{self.text}\n")
        f.write("\n")
    return True

# %% ../00_core.ipynb 46
# Make a CLI function using `call_parse` to handle arguments
from sys import stderr
from fastcore.script import call_parse
import distutils.util # to convert string to bool
import json
import sys
# Ensure settings.ini contains `console_scripts = pingme=pingme.pingme:cli`, this makes the call as `pingme` and calls the cli function found in package pingme.pingme
@call_parse
def cli(
    # webhook_url:str = None, # URL of the teams/slack webhook
    # email_from:str = None, # Email address to send from
    # email_to:str = None, # Email address to send to
    # smtp_host:str = None, # SMTP host to use
    # smtp_port:int = None, # SMTP port to use
    # smtp_user:str = None, # SMTP username to use
    # smtp_password:str = None, # SMTP password to use
    # log_file:str = "./output/log.txt", # Log file to use
    # title:str = None, # Title of the message
    # text:str = None, # Text of the message
    # payload_file:str = "./cards/default_card.json", # Path to a file containing the payload
    # payload_context:str = None, # Context to use for the payload (variable replacement)
    # webhook:bool = False, # Send to webhook
    # email:bool = False, # Send to email
    # log:bool = False, # Send to log
    config_file:str # Path to a config file
    ):
    """
    The Command Line Interface (CLI) for the pingme package. This is the main entry point for the package. Currently only allows for a config file to be provided, but can be extended to allow for args. Command line passing is handled with @call_parse decorator.
    """
    config = get_config(config_file)

    WEBHOOK_URL = config['PINGME_WEBHOOK_URL']
    EMAIL_FROM = config['PINGME_EMAIL_FROM']
    EMAIL_TO = config['PINGME_EMAIL_TO']
    SMTP_HOST = config['PINGME_SMTP_HOST']
    SMTP_PORT = config['PINGME_SMTP_PORT']
    SMTP_USER = config['PINGME_SMTP_USER']
    SMTP_PASSWORD = config['PINGME_SMTP_PASSWORD']
    LOG_FILE = config['PINGME_LOG_FILE']
    TITLE = config['PINGME_TITLE']
    TEXT = config['PINGME_TEXT']
    CARD_DIR = config['PINGME_CARD_DIR']
    CARD_FILE = config['PINGME_CARD_FILE']
    CARD_EXT = config['PINGME_CARD_EXT']
    CARD_CONTEXT = json.loads(config['PINGME_CARD_CONTEXT'])
    SEND_EMAIL = distutils.util.strtobool(config['PINGME_SEND_EMAIL'])
    SEND_WEBHOOK = distutils.util.strtobool(config['PINGME_SEND_WEBHOOK'])
    SEND_LOG_FILE = distutils.util.strtobool(config['PINGME_SEND_LOG_FILE'])

    card = Card(name=CARD_FILE, context=CARD_CONTEXT, title=TITLE, text=TEXT)
    notification = PingMe(card=card, card_dir=CARD_DIR, card_ext=CARD_EXT)

    if SEND_WEBHOOK:
        notification.send_to_webhook(WEBHOOK_URL)
        print("Sent to webhook", file=sys.stderr)
    if SEND_EMAIL:
        notification.send_to_email(EMAIL_FROM, EMAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)
        print("Sent to email", file=sys.stderr)
    if SEND_LOG_FILE:
        notification.send_to_log_file(LOG_FILE)
        print("Sent to logfile", file=sys.stderr)

    return True
