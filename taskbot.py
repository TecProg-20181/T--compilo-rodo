#!/usr/bin/env python3
# Python modules
from time import sleep

# Customized modules
from updates_handler import handle_updates
from url_handler import get_last_update_id, get_updates


def main():
    last_update_id = None

    while True:
        print("Updates")
        updates = get_updates(last_update_id)

        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)

        sleep(0.5)


if __name__ == '__main__':
    main()
