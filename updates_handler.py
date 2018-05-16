#!/usr/bin/env python3
# Customized modules
from url_handler import send_message
from command_handler import (new_task,\
                            rename_task,\
                            duplicate_task,\
                            delete_task,\
                            todo_task,\
                            doing_task,\
                            done_task,\
                            list_task,\
                            dependson_task,\
                            priority_task,\
                            start_task,\
                            help_task,)

# Public Methods
def handle_updates(updates):
    for update in updates["result"]:
        if 'message' in update:
            message = update['message']
        elif 'edited_message' in update:
            message = update['edited_message']
        else:
            print('Can\'t process! {}'.format(update))
            return

        command = message["text"].split(" ", 1)[0]
        msg = ''
        if len(message["text"].split(" ", 1)) > 1:
            msg = message["text"].split(" ", 1)[1].strip()

        chat = message["chat"]["id"]

        print(command, msg, chat)

        if command == '/new':
            new_task(chat, msg)

        elif command == '/rename':
            rename_task(chat, msg)

        elif command == '/duplicate':
            duplicate_task(chat, msg)

        elif command == '/delete':
            delete_task(chat, msg)

        elif command == '/todo':
            todo_task(chat, msg)

        elif command == '/doing':
            doing_task(chat, msg)

        elif command == '/done':
            done_task(chat, msg)

        elif command == '/list':
            list_task(chat, msg)
        elif command == '/dependson':
            dependson_task(chat, msg)
        elif command == '/priority':
            priority_task(chat, msg)
        elif command == '/start':
            start_task(chat)
        elif command == '/help':
            help_task(chat)
        else:
            send_message("I'm sorry dave. I'm afraid I can't do that.", chat)

