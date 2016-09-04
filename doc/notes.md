Title:   Infos
Summary: General informations
Authors: Pierre GINDRAUD
Date:    2016-06-20

# Informations

## Feature

* Build a cache of command object by using a dict() instance
    * the name of the command is used as dict key
    * load the command handler during his execution and place it into the dict
    * provide a command to flush the dict cache
* Users Sessions : when a user send a message, a session is automatically associated.
    * If there is no current session a new one is created
    * If there is a existing session with a valid session time, the message content is provided to the command handler system. The session time is refresh with the now value
    * If there is a existing session with a invalid (expired) session time, a new empty session if created and then, the message is parsed.
* Each command handler have access to a the session's public interface
    * They can update the status
    * They can store, retrieve and delete value in the "key,value" session storage space.
    * The key is automatically prefixed by the name of the current command to prevent command to access each other values.

* Command
    * Each command inform the parser of the type of all of its parameters and the number of input parameters
    * Each command is accessible from a restricted set of session state (ex: only AUTH)
    * They throw a common Exception Type (which can be extended) to handle there error. The exception message is send to user a a SMS reply
    * They produce a small output which consist of a unique string that will be sended to the user by SMS. This string can be small as just 'OK' or bigger as a small text which contains informations.
    * They have access to the main logging handler

* Authentification
    * several method of authentification : otp by sending sms, code by mail, static password

### Modes

* oneshot
    * Parse SMS
    * Load command
    * Execute command
    * Return the result
* multi shot
    * Load the daemon
    * Open a listening socket
    * Wait for a message
    * --
    * Parse the SMS
    * Load the command into the dict (if it is not)
    * Execute command
    * Return result


