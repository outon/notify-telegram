# -*- coding: utf-8 -*-

# Copyright 2017-2020 by José Ramón Casal
# All rights reserved.
# This file is part of the notify-telegram.py, and is released
# under the "MIT License Agreement". Please see the LICENSE.txt
# file that should have been included as part of this package.

# Version:
#    1.0.1   Add proxy
#    1.0.2   Add default values
#    1.0.3   Add config file


import argparse
import configparser
import inspect
import sys
from datetime import datetime
from types import SimpleNamespace

import telegram

# Default values.
# These values are overridden by the values defined in the configuration file
default_engine = "Centreon"
default_system_name = "My Monitoring System"
default_url = "https://host:port/centreon/"
default_message_template = "long"  # long, medium, short
default_proxy_url = ""  # http://username:password@host:port

# Global variables
object_type = {
    "host": "",
    "service": "",
}
notification_types = {
    "PROBLEM": "\U0001F4A1",  # Light bulb
    "RECOVERY": "\U0001F6C8",  # Information
    "ACKNOWLEDGEMENT": "",
    "FLAPPINGSTART": "",
    "FLAPPINGSTOP": "",
    "FLAPPINGDISABLED": "",
    "DOWNTIMESTART": "\U0001F515",  # Bell with cancellation stroke
    "DOWNTIMEEND": "\U0001F514",  # Bell
    "DOWNTIMECANCELLED": "\U0001F514",  # Bell
}
hoststate_type = {
    "SOFT": "",
    "HARD": "",
}

host_states = {
    "UP": "\U00002705",  # Green Check
    "DOWN": "\U0001F534",  # Large Red Circle
    "UNREACHABLE": "\U00002753",  # heavy question mark
}
service_states = {
    "OK": "\U00002705",  # Green Check
    "WARNING": "\U000026A0",  # Warning Triangle
    "CRITICAL": "\U0000274C",  # Heavy red cross
    "UNKNOWN": "\U00002753",  # Heavy question mark
}

host_notification_template = {
    "long": """\
            \\*\\*\\*\\*\\* {Engine_name} - {Engine_type} Notification \\*\\*\\*\\*\\*

            *Notification Type*:{Notification_type}

            *Host*: {Host_name}
            *State*: {Severity} {Icon}
            *Address*: {Host_address}

            *Date/Time*: {Date}
            *Additional Info*: `{Output}`
            """,
    "medium": """\
            Host {Host_name} is {Severity} {icon}
            *Time*: {Date}
            *Info*: `{Output}`
            """,
    "short": """\
            Host "{Host_name}" is {Severity} {icon} - *Info*: `{Output}`
            """,
}
service_notification_template = {
    "long": """\
            \\*\\*\\*\\*\\* {Engine_name} - {Engine_type} Notification \\*\\*\\*\\*\\*

            *Notification Type*: {Notification_type}

            *Service*: {Service_name}
            *State*: {Severity} {Icon}
            *Host*: {Host_name}
            *Address*: {Host_address}

            *Time*: {Date}
            *Additional Info*: `{Output}`
            """,
    "medium": """\
            *Service*: {Service_name}
            *State*: {Severity} {icon}
            *Host*: {Host_name}
            *Address*: {Host_address}
            *Date*: {Date}
            *Info*: `{Output}`
            """,
    "short": """\
            {Notification_type} {Host_name}/{Service_name}: {Severity} {icon}  - *Info*: `{Output}`
            """,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Notificaciones de Nagios con Telegram",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, width=120, max_help_position=60
        ),
    )

    parser.add_argument(
        "--config",
        type=argparse.FileType("r", encoding="UTF-8"),
        help="Configuration file",
    )
    parser.add_argument("-t", "--token", help="Unique Telegram API token")
    parser.add_argument(
        "--contact", help="Telegram User/Group ID of the contact being notified",
    )
    parser.add_argument(
        "--notificationtype", help="Type of notification that is being sent",
    )
    parser.add_argument(
        "-o",
        "--object_type",
        required=True,
        choices=object_type.keys(),
        help="Nagios Object Type",
    )
    parser.add_argument("--hostname", help="Name of the host")
    parser.add_argument("--hostaddress", help="Address of the host")
    parser.add_argument(
        "--hoststate", choices=host_states.keys(), help="Current state of the host",
    )
    parser.add_argument(
        "--servicestate",
        choices=service_states.keys(),
        help="Current state of service",
    )
    parser.add_argument("--servicedesc", help="Description of the  service")

    parser.add_argument("--output", nargs="?")
    args = parser.parse_args()
    return args


def read_config(config_file=None):
    fichero_config = "notify-telegram.conf" if not config_file else config_file

    try:
        with open(fichero_config, "r") as f:
            config_string = "[notify-telegram]\n" + f.read()
        config = configparser.ConfigParser()
        config.read_string(config_string)
    except IOError:
        return None  # File does not exists

    return config["notify-telegram"]


def default_values(config_file=None):
    def get_value(value, default=None):
        if value is None:
            return default
        else:
            return value

    if not config_file:
        config_file = "notify-telegram.conf"

    properties = read_config(config_file)

    config = SimpleNamespace()
    config.token = properties.get("token")
    config.contact = properties.get("contact")
    config.monitoring_engine = get_value(
        properties.get("monitoring_engine"), default_engine
    )
    config.monitoring_system_name = get_value(
        properties.get("monitoring_system_name"), default_system_name
    )
    config.monitoring_url = get_value(properties.get("monitoring_url"), default_url)
    config.message_template = get_value(
        properties.get("message_length"), default_message_template
    )
    config.proxy_url = get_value(properties.get("proxy_url"), default_proxy_url)

    return config


def validate_args(args):
    if args.object_type == "service":
        if None in (args.servicedesc, args.servicestate):
            raise ValueError

    if args.object_type == "host":
        if None in (args.hoststate):
            raise ValueError

    if args.hostname is None and args.hostaddress is None:
        raise ValueError


def get_icon(object_type, state):
    if object_type == "NOTIFICATION":
        icon = notification_types.get(state)
    elif object_type == "host":
        icon = host_states.get(state)
    elif object_type == "service":
        icon = service_states.get(state)
    else:
        icon = ""

    return icon


def send_notification(bot, user_id, message):
    message = bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown", )
    return message


def notification_type_icon(args):
    icon = notification_types.get(args.notificationtype)
    return icon


def get_message(args, config):
    state = None
    template = None

    if args.object_type == "host":
        state = args.hoststate
        template = host_notification_template
    elif args.object_type == "service":
        state = args.servicestate
        template = service_notification_template

    icon = get_icon(args.object_type, state)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    message = template[config.message_template].format(
        Engine_type=config.monitoring_engine,
        Engine_name=config.monitoring_system_name,
        Engine_url=config.monitoring_url,
        Notification_type=args.notificationtype,
        Service_name=args.servicedesc,
        Host_name=args.hostname,
        Host_address=args.hostaddress,
        Severity=state,
        Icon=icon,
        Date=now,
        Output=args.output,
    )

    message = inspect.cleandoc(message)

    return message


def main():
    # Obtaining command line parameters and configuration
    args = parse_args()
    config = default_values(args.config)

    # Overwrite config values if they are passed as command line argument
    if args.token:
        config.token = args.token

    if args.contact:
        config.contact = args.contact

    print(f"Notificaciones de {config.monitoring_engine} con Telegram")

    # Config and parameters validation.
    if config.token is None:
        print("Error: Telegram API Token not defined")
        exit(1)

    try:
        user_id = int(config.contact)
    except ValueError:
        print("Error: User/Group ID not defined")
        exit(1)
    except:
        print("Error: Invalid User/Group ID")
        exit(1)

    validate_args(args)

    # Generate message to be sent
    message = get_message(args, config)

    # Create bot
    req = telegram.utils.request.Request(proxy_url=config.proxy_url)
    bot = telegram.Bot(token=config.token, request=req)

    # Send message using bot
    try:
        msg = send_notification(bot, user_id, message)
    except:
        print(f"Could not send notification")
        print("Unexpected error:", sys.exc_info()[0])
        exit(1)

    if msg is not None:
        print(f"Sent notification alert to {msg.chat.first_name} {msg.chat.last_name}")
        exit(0)


if __name__ == "__main__":
    main()
    exit(0)
