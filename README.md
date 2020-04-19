# **notify-telegram.py**
 **notify-telegram.py** - script python para enviar notificaciones de Nagios/Centreon usando un bot de Telegram.
 
 * Para instrucciones en español consulte [README_es.md](./README_es.md)
 
  **notify-telegram.py** - python script for sending Nagios/Centreon notifications using a Telegram
    bot. 

This script will send a notification to Telegram

This script can run on Python 3.6 and above.

## Requeriments:

### 1. Your own Telegram BOT
Please see BotFather for more info about [telegram bots](https://core.telegram.org/bots)
    
3.1. First step, create your Telegram bot:

- [x] Open *Telegram* --> search for contact: @BotFather
- [x] Send the following message to **@BotFather**
  - [ ] /newbot
  - [ ] Answer all the questions of **@BotFather**
    
3.2. Next step, getting your telegram user-id or group id:

- [x] Open *Telegram* -> search for contacts: @IDbot
- [x] Send the following message to *@IDBot*
  - [ ] /getid to retrieve your user-id
  - [ ] /getgroupid to retrieve the group-id of current chat

**Hint**: positive number for user-id and negative numbers for group-id.

### 2. Download from GitHub:
Download this script and all related material from GitHub:
```bash
git clone https://github.com/outon/notify-telegram.git
```

### 3. Python dependencies
Install the dependencies needed by this script:

```bash
cd notify-telegram
pip install -r requeriments.txt
```

## Setup
Once you have a **Telegram Bot** and all the requirements are installed  you can run the script without any additional configuration.

You will need to pass some arguments in command line 

```bash
python3 notify-telegram.py -h
```

#### usage:

    usage: notify-telegram.py [-h] [--config CONFIG] [-t TOKEN] [--contact CONTACT] [--notificationtype NOTIFICATIONTYPE] -o
                              {host,service} [--hostname HOSTNAME] [--hostaddress HOSTADDRESS]
                              [--hoststate {UP,DOWN,UNREACHABLE}] [--servicestate {OK,WARNING,CRITICAL,UNKNOWN}]
                              [--servicedesc SERVICEDESC] [--output [OUTPUT]]
    
    Notificaciones de Nagios con Telegram
    
    optional arguments:
      -h, --help                                       show this help message and exit
      --config CONFIG                                  Configuration file
      -t TOKEN, --token TOKEN                          Unique Telegram API token
      --contact CONTACT                                Telegram User/Group ID of the contact being notified
      --notificationtype NOTIFICATIONTYPE              Type of notification that is being sent
      -o {host,service}, --object_type {host,service}  Nagios Object Type
      --hostname HOSTNAME                              Name of the host
      --hostaddress HOSTADDRESS                        Address of the host
      --hoststate {UP,DOWN,UNREACHABLE}                Current state of the host
      --servicestate {OK,WARNING,CRITICAL,UNKNOWN}     Current state of service
      --servicedesc SERVICEDESC                        Description of the service
      --output [OUTPUT]

As you can see, you will need several parameters to run this script.

The following parameters are mandatory: `token` and `contact`.

These parameters must either be in a configuration file or passed as a command line parameter.

You can store some values in a configuration file, usually `notify-telegram.conf` which by default will be stored in the same directory as this script. You can also use your own configuration file but you must specify the path where it is saved when you run the script.

A sample configuration file [notify-telegram.conf](./notify-telegram.conf) is provided with this script.

| Parameter  | Description|
| :---         |     :---     |
| token   | Private API key for Telegram Bot.   |
| contact | Default Group/User ID where to send notifications in case no one is provided |   
| proxy_url | Address of proxy server used to connect to internet |
| monitoring_engine | Value is used in some text strings to show which monitoring engine is being used (Centreon or Nagios) |
| monitoring_system_name | Name of your monitoring system |
| monitoring_url | URL of your monitoring system |
| message_length | Indicate which of three existing template will be used: long, medium, short

Remember that *command line parameters* **take precedence** over values stored in the *configuration file*.

That is, if you decide to store your _Telegram API token_ in the configuration file and include your _Token_ as a command line parameter, the latter value will be used.

If you prefer, you can specify your own configuration file or use the default configuration file `notify-telegram.py`

#### Notify a host event:
If you want to notify a *`host`* event you should include, at least the following parameters: `hoststate` and either `hostname` or `hostaddress`:

    ./notify-telegram.py --token <bot token> --contact <user id|group id> \ 
        --object_type host --hoststate <UP|DOWN|UNREACHABLE> \ 
        --hostname <hostname> --hostaddress <ipaddress> \ 
        --output <event message>
    
#### Notify a service event:
If you want to notify a *`service`* event you should include, at least the following parameters: `servicestate`, `servicedesc` and `hostname`:

    ./notify-telegram.py --token <bot token> --contact <user id|group_id> \ 
        --object_type service --servicestate <'OK|WARNING|CRITICAL"UNKOWN> \ 
        --servicedesc <service descriptoin> --hostname <hostname> \ 
        --output <event message>

## Nagios configuration

Finally you have to configure your Nagios:

You have two options: Reuse a variable, usually `pager`, or create your [custom variable macro](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/customobjectvars.html).

#### Update your contacts
You must include in your contact information the User/Group ID.

If you decided to user the existing `pager` field to store you User/Group ID or create your *custom object variable*
    
    define contact {
        contact_name                    nagios telegram bot
        pager                           <user_id|group_id>
        service_notification_commands   notify-service-by-telegram
        host_notification_commands      notify-host-by-telegram
    }

If you decided to create your custom variable macro:
    
    define contact {
        contact_name                    nagios telegram bot
        _telegram                       <user_id|group_id>
        service_notification_commands   notify-service-by-telegram
        host_notification_commands      notify-host-by-telegram
    }


#### Define new commands
You must define new commands to send notification by Telegram.

If you are reusing the `PAGER` variable you should use the macro **\$CONTACTPAGER\$**.

If you decided to create your custom variable then you should use the macro **\$_CONTACTTELEGRAM\$**.
 
    define command {
        command_name    notify-host-by-telegram
        command_line    /usr/local/bin/notify-telegram.py --token <token> \ 
            --object_type host --contact "$CONTACTPAGER$" --notificationtype "$NOTIFICATIONTYPE$" \ 
            --hoststate "$HOSTSTATE$" --hostname "$HOSTNAME$" --hostaddress "$HOSTADDRESS$" --output "$HOSTOUTPUT$"
    }
    
    define command {
        command_name    notify-service-by-telegram
        command_line    /usr/local/bin/notify-telegram.py --token <token> \
            --object_type service --contact "$CONTACTPAGER$" --notificationtype "$NOTIFICATIONTYPE$" \ 
            --servicestate "$SERVICESTATE$" --hostname "$HOSTNAME$" --servicedesc "$SERVICEDESC$" --output "$SERVICEOUTPUT$"


## Enjoy!

## License
This scripts and related material is distributed under [MIT License](./LICENSE.txt)