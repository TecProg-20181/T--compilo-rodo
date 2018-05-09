#!/usr/bin/env python3
# Python modules
import sqlalchemy

# Customized modules
import db
from db import Task
from url_handler import send_message
from command_handler import new_task, rename_task, duplicate_task

# Private Costants
__HELP = """
 /new NOME
 /todo ID
 /doing ID
 /done ID
 /delete ID
 /list
 /rename ID NOME
 /dependson ID ID...
 /duplicate ID
 /priority ID PRIORITY{low, medium, high}
 /help
"""

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
            rename_task(chat,msg)
            
        elif command == '/duplicate':
            duplicate_task(chat,msg)

        elif command == '/delete':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                for t in task.dependencies.split(',')[:-1]:
                    qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                    t = qy.one()
                    t.parents = t.parents.replace('{},'.format(task.id), '')
                db.session.delete(task)
                db.session.commit()
                send_message("Task [[{}]] deleted".format(task_id), chat)

        elif command == '/todo':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'TODO'
                db.session.commit()
                send_message("*TODO* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/doing':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'DOING'
                db.session.commit()
                send_message("*DOING* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/done':
            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                task.status = 'DONE'
                db.session.commit()
                send_message("*DONE* task [[{}]] {}".format(task.id, task.name), chat)

        elif command == '/list':
            a = ''

            a += '\U0001F4CB Task List\n'
            query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
            for task in query.all():
                icon = '\U0001F195'
                if task.status == 'DOING':
                    icon = '\U000023FA'
                elif task.status == 'DONE':
                    icon = '\U00002611'

                a += '[[{}]] {} {} with priority [[{}]]\n'.format(task.id, icon, task.name, task.priority)
                a += __deps_text(task, chat)

            send_message(a, chat)
            a = ''

            a += '\U0001F4DD _Status_\n'
            query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
            a += '\n\U0001F195 *TODO*\n'
            for task in query.all():
                a += '[[{}]] {} with priority [[{}]]\n'.format(task.id, task.name, task.priority)
            query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
            a += '\n\U000023FA *DOING*\n'
            for task in query.all():
                a += '[[{}]] {} with priority [[{}]]\n'.format(task.id, task.name, task.priority)
            query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
            a += '\n\U00002611 *DONE*\n'
            for task in query.all():
                a += '[[{}]] {} with priority [[{}]]\n'.format(task.id, task.name, task.priority)

            send_message(a, chat)
        elif command == '/dependson':
            text = ''
            if msg != '':
                if len(msg.split(' ', 1)) > 1:
                    text = msg.split(' ', 1)[1]
                msg = msg.split(' ', 1)[0]

            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                if text == '':
                    for i in task.dependencies.split(',')[:-1]:
                        i = int(i)
                        q = db.session.query(Task).filter_by(id=i, chat=chat)
                        t = q.one()
                        t.parents = t.parents.replace('{},'.format(task.id), '')

                    task.dependencies = ''
                    send_message("Dependencies removed from task {}".format(task_id), chat)
                else:
                    for depid in text.split(' '):
                        if not depid.isdigit():
                            send_message("All dependencies ids must be numeric, and not {}".format(depid), chat)
                        else:
                            if __verify_circular_dependency_in_list(msg, text, chat):
                                send_message('Can not has circular dependency', chat)
                            else:
                                depid = int(depid)
                                query = db.session.query(Task).filter_by(id=depid, chat=chat)
                                try:
                                    taskdep = query.one()
                                    taskdep.parents += str(task.id) + ','
                                except sqlalchemy.orm.exc.NoResultFound:
                                    send_message("_404_ Task {} not found x.x".format(depid), chat)
                                    continue

                                deplist = task.dependencies.split(',')
                                if str(depid) not in deplist:
                                    task.dependencies += str(depid) + ','

                db.session.commit()
                send_message("Task {} dependencies up to date".format(task_id), chat)
        elif command == '/priority':
            text = ''
            if msg != '':
                if len(msg.split(' ', 1)) > 1:
                    text = msg.split(' ', 1)[1]
                msg = msg.split(' ', 1)[0]

            if not msg.isdigit():
                send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return

                if text == '':
                    task.priority = ''
                    send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                else:
                    if text.lower() not in ['high', 'medium', 'low']:
                        send_message("The priority *must be* one of the following: high, medium, low", chat)
                    else:
                        task.priority = text.lower()
                        send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
                db.session.commit()

        elif command == '/start':
            send_message("Welcome! Here is a list of things you can do.", chat)
            send_message(__HELP, chat)
        elif command == '/help':
            send_message("Here is a list of things you can do.", chat)
            send_message(__HELP, chat)
        else:
            send_message("I'm sorry dave. I'm afraid I can't do that.", chat)

# Private methods
def __deps_text(task, chat, preceed=''):
    text = ''

    for i in range(len(task.dependencies.split(',')[:-1])):
        line = preceed
        query = db.session.query(Task).filter_by(id=int(task.dependencies.split(',')[:-1][i]), chat=chat)
        dep = query.one()

        icon = '\U0001F195'
        if dep.status == 'DOING':
            icon = '\U000023FA'
        elif dep.status == 'DONE':
            icon = '\U00002611'

        if i + 1 == len(task.dependencies.split(',')[:-1]):
            line += '└── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += __deps_text(dep, chat, preceed + '    ')
        else:
            line += '├── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += __deps_text(dep, chat, preceed + '│   ')

        text += line

    return text

def __verify_circular_dependency_in_list(task_id, dependency_id, chat):
    """
    return True means that are circular dependency
    return False means that aren't circular dependency
    """
    query = db.session.query(Task).filter_by(id=dependency_id, chat=chat)
    dependency = query.one()

    if dependency.dependencies == '':
        return False
    else :
        total_result = False
        list_of_dependencies = dependency.dependencies.split(',')

        for i in list_of_dependencies:
            if i == '':
                continue
            query = db.session.query(Task).filter_by(id=i, chat=chat)
            task = query.one()
            another_dependency = dependency.dependencies.split(',')
            if task_id in another_dependency:
                return True
            else:
                parcial_result = __verify_circular_dependency_in_list(task_id, task.id, chat)
                total_result = total_result | parcial_result

        return total_result
