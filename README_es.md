# **notify-telegram.py**
 **notify-telegram.py** - script python para enviar notificaciones de Nagios/Centreon usando un bot de Telegram. 

Este script enviará una notificación a Telegram.

Este script puede funcionar en Python 3.6 y superior.

## Requisitos:

### 1. Su propio BOT de Telegram
Por favor, consulte BotFather para obtener más información acerca de los [Bots de Telegram](https://core.telegram.org/bots)
    
1.1. Primer paso, cree su bot de Telegram:

- [x] Abrir *Telegram* --> buscar el contacto: @BotFather
- [x] Envíe el siguiente mensaje a **@BotFather**
  - [ ] /newbot
  - Responda a todas las preguntas de **@BotFather**
    
1.2. Siguiente paso, obtener su identificación de usuario o de grupo del telegram:

- [x] Abrir *Telegram* -> buscar el contacto: @IDbot
- [x] Envíe el siguiente mensaje a *@IDBot*
  - [ ] /getid para recuperar su identificación de usuario

En caso de un grupo:
- [x] Abrir *Telegram* -> Añada el contacto: @IDbot a su grupo
- [x] Envíe el siguiente mensaje a *@IDBot*
  - [ ] /getgroupid para recuperar la identificación de grupo del chat actual

**Nota**: obtendrá un número positivo para la identificación de usuario y número negativo para la identificación de grupo.

### 2. Descargar desde GitHub:
Descargue este script y todo el material relacionado de GitHub:
```bash
git clone https://github.com/outon/notify-telegram.git
```

### 3. Dependencias de Python
Instale las dependencias que necesita este script:

```bash
cd notify-telegram
pip install -r requeriments.txt
```

## Configuración
Una vez que tengas un **Bot de Telegram** y todos los requisitos estén instalados puede ejecutar el script sin ninguna configuración adicional.

Es necesario pasar algunos argumentos en la línea de comandos

```bash
python3 notify-telegram.py -h
```

#### Uso:

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

Como puede ver, necesitará varios parámetros para ejecutar este script.

Los siguientes parámetros son obligatorios: `token` y `contacto`.

Estos parámetros pueden estar en un archivo de configuración o ser pasados como parámetros de la línea de comandos.

Puede almacenar algunos valores en un archivo de configuración, normalmente `notify-telegram.conf` que por defecto se ubicará en el mismo directorio que este script. También puede utilizar su propio archivo de configuración, pero debe especificar la ruta donde está almacendado cuando ejecute el script.

Con este script se proporciona archivo de configuración de ejemplo [notify-telegram.conf](./notify-telegram.conf) 

| Parámetro  | Descripción |
| :---         |     :---     |
| token   | Clave privada de la API de Telegram para el Bot.   |
| contact | identificación de Grupo/Usuario por defecto a donde enviar las notificaciones en caso de que no se proporcione ninguna |   
| proxy_url | Address of proxy server used to connect to internet |
| monitoring_engine | Este valor se utiliza en algunas cadenas de texto para mostrar qué motor de supervisión se está utilizando (Centreon o Nagios) |
| monitoring_system_name | Nombre de su sistema de monitorización |
| monitoring_url | URL de su sistema de monitorización |
| message_length | Indique cuál de las tres plantillas existentes se utilizará: larga, media, corta

Recuerde que los *parámetros de la línea de comandos* **tienen precedencia** sobre los valores almacenados en el *fichero de configuración*.

Es decir, si decide almacenar su _token API de Telegram_ en el archivo de configuración e incluir su _Token_ como parámetro de línea de comandos, se utilizará este último valor.

#### Notificar un evento tipo host:
Si se quiere notificar un evento *`host`* se deben incluir, al menos, los siguientes parámetros: `hoststate` y bien `hostname` o `hostaddress`:

    ./notify-telegram.py --token <bot token> --contact <user id|group id> \ 
        --object_type host --hoststate <UP|DOWN|UNREACHABLE> \ 
        --hostname <hostname> --hostaddress <ipaddress> \ 
        --output <event message>
    
#### Notificar un evento tipo servicio:
Si se quiere notificar un evento *`service`* se deben incluir, al menos, los siguientes parámetros: `servicestate`, `servicedesc` y `hostname`:

    ./notify-telegram.py --token <bot token> --contact <user id|group_id> \ 
        --object_type service --servicestate <'OK|WARNING|CRITICAL"UNKOWN> \ 
        --servicedesc <service descriptoin> --hostname <hostname> \ 
        --output <event message>

## Configuración de Nagios

Finalmente tendrá que configurar su Nagios:

Tiene dos opciones: Reutilizar una variable, normalmente `pager`, o crear su propia [custom variable macro](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/4/en/customobjectvars.html).
 
#### Actualice sus contactos
Deberá incluir en la información de los contactos el ID de usuario/grupo.

Si decidió utilizar el campo existente "pager" para almacenar su ID de usuario/grupo:
    
    define contact {
        contact_name                    nagios telegram bot
        pager                           <user_id|group_id>
        service_notification_commands   notify-service-by-telegram
        host_notification_commands      notify-host-by-telegram
    }

Si decidió usar [custom variable macro]:
    
    define contact {
        contact_name                    nagios telegram bot
        _telegram                       <user_id|group_id>
        service_notification_commands   notify-service-by-telegram
        host_notification_commands      notify-host-by-telegram
    }


#### Defina nuevos comandos
Debe definir nuevos comandos para enviar la notificación por telegrama.

Si está reutilizando la variable `PAGER` debe utilizar la macro **\$CONTACTPAGER\$**. Sin embargo, si decidió crear su variable personalizada, entonces debe usar el macro **\$_CONTACTTELEGRAM\$**.
 
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


## ¡Disfruta!

## Licencia
Este script y el material relacionado se distribuye bajo [Licencia MIT](./LICENSE.txt)