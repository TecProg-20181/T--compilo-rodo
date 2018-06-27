import db
import sqlalchemy
from db import Task
from url_handler import send_message

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

# Public methods
def start_task(chat_id):
    send_message("Welcome! Here is a list of things you can do.", chat_id)
    send_message(__HELP, chat_id)

def help_task(chat_id):
    send_message("Here is a list of things you can do.", chat_id)
    send_message(__HELP, chat_id)
def new_task(chat_id, name):
    task = Task(chat=chat_id, name=name, status='TODO', dependencies='', parents='', priority='')
    if(name != ''):
        db.session.add(task)
        db.session.commit()
        send_message("New task *TODO* [[{}]] {}".format(task.id, task.name), chat_id)

def rename_task(chat_id, msg):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)

        if text == '':
            send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat_id)
            return

        old_text = task.name
        task.name = text
        db.session.commit()
        send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat_id)

def duplicate_task(chat_id, msg):
    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)

        dtask = Task(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                        parents=task.parents, priority=task.priority, duedate=task.duedate)
        db.session.add(dtask)

        for t in task.dependencies.split(',')[:-1]:
            t = db.search_Task(int(t), chat_id)
            t.parents += '{},'.format(dtask.id)

        db.session.commit()
        send_message("New task *TODO* [[{}]] {}".format(dtask.id, dtask.name), chat_id)

def delete_task(chat_id, msg):
    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)
        for t in task.dependencies.split(',')[:-1]:
            t = db.search_Task(int(t), chat_id)
            t.parents = t.parents.replace('{},'.format(task.id), '')
        db.session.delete(task)
        db.session.commit()
        send_message("Task [[{}]] deleted".format(task_id), chat_id)

def todo_task(chat_id, msg):
    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)
        task.status = 'TODO'
        db.session.commit()
        send_message("*TODO* task [[{}]] {}".format(task.id, task.name), chat_id)

def doing_task(chat_id, msg):
    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)
        task.status = 'DOING'
        db.session.commit()
        send_message("*DOING* task [[{}]] {}".format(task.id, task.name), chat_id)

def done_task(chat_id, msg):
    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)
        task.status = 'DONE'
        db.session.commit()
        send_message("*DONE* task [[{}]] {}".format(task.id, task.name), chat_id)

def list_task(chat_id, msg):
    a = ''

    a += '\U0001F4CB Task List\n'
    query = db.session.query(Task).filter_by(parents='', chat=chat_id).order_by(Task.id)
    for task in query.all():
        icon = '\U0001F195'
        if task.status == 'DOING':
            icon = '\U000023FA'
        elif task.status == 'DONE':
            icon = '\U00002611'

        a += __priority_message(task)
        a += __deps_text(task, chat_id)

    send_message(a, chat_id)
    a = ''

    a += '\U0001F4DD _Status_\n'
    query = db.session.query(Task).filter_by(status='TODO', chat=chat_id).order_by(Task.id)
    a += '\n\U0001F195 *TODO*\n'
    for task in query.all():
        a += __priority_message(task)
    query = db.session.query(Task).filter_by(status='DOING', chat=chat_id).order_by(Task.id)
    a += '\n\U000023FA *DOING*\n'
    for task in query.all():
        a += __priority_message(task)
    query = db.session.query(Task).filter_by(status='DONE', chat=chat_id).order_by(Task.id)
    a += '\n\U00002611 *DONE*\n'
    for task in query.all():
        a += __priority_message(task) 

    send_message(a, chat_id)

def dependson_task(chat_id, msg):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)

        if text == '':
            for i in task.dependencies.split(',')[:-1]:
                i = int(i)
                t = db.search_Task(i, chat_id)
                t.parents = t.parents.replace('{},'.format(task.id), '')

            task.dependencies = ''
            send_message("Dependencies removed from task {}".format(task_id), chat_id)
        else:
            for depid in text.split(' '):
                if not depid.isdigit():
                    send_message("All dependencies ids must be numeric, and not {}".format(depid), chat_id)
                else:
                    if __verify_circular_dependency_in_list(msg, text, chat_id):
                        send_message('Can not has circular dependency', chat_id)
                    else:
                        depid = int(depid)
                        taskdep = db.search_Task(task_id, chat_id)
                        taskdep.parents += str(task.id) + ','
                        
                        deplist = task.dependencies.split(',')
                        if str(depid) not in deplist:
                            task.dependencies += str(depid) + ','

        db.session.commit()
        send_message("Task {} dependencies up to date".format(task_id), chat_id)
def priority_task(chat_id, msg):
    text = ''
    if msg != '':
        if len(msg.split(' ', 1)) > 1:
            text = msg.split(' ', 1)[1]
        msg = msg.split(' ', 1)[0]

    if not msg.isdigit():
        send_message("You must inform the task id", chat_id)
    else:
        task_id = int(msg)
        task = db.search_Task(task_id, chat_id)

        if text == '':
            task.priority = ''
            send_message("_Cleared_ all priorities from task {}".format(task_id), chat_id)
        else:
            if text.lower() not in ['high', 'medium', 'low']:
                send_message("The priority *must be* one of the following: high, medium, low", chat_id)
            else:
                task.priority = text.lower()
                send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat_id)
        db.session.commit()


# Private methods
def __deps_text(task, chat_id, preceed=''):
    text = ''

    for i in range(len(task.dependencies.split(',')[:-1])):
        line = preceed
        task = db.search_Task(int(task.dependencies.split(',')[:-1][i]), chat_id)
        dep = query.one()

        icon = '\U0001F195'
        if dep.status == 'DOING':
            icon = '\U000023FA'
        elif dep.status == 'DONE':
            icon = '\U00002611'

        if i + 1 == len(task.dependencies.split(',')[:-1]):
            line += '└── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += __deps_text(dep, chat_id, preceed + '    ')
        else:
            line += '├── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
            line += __deps_text(dep, chat_id, preceed + '│   ')

        text += line

    return text

def __verify_circular_dependency_in_list(task_id, dependency_id, chat_id):
    """
    return True means that are circular dependency
    return False means that aren't circular dependency
    """

    dependency = db.search_Task(dependency_id, chat_id)

    if dependency.dependencies == '':
        return False
    else :
        total_result = False
        list_of_dependencies = dependency.dependencies.split(',')

        for i in list_of_dependencies:
            if i == '':
                continue
            task = db.search_Task(i, chat_id)
            another_dependency = dependency.dependencies.split(',')
            if task_id in another_dependency:
                return True
            else:
                parcial_result = __verify_circular_dependency_in_list(task_id, task.id, chat_id)
                total_result = total_result | parcial_result

        return total_result
def __priority_message(task):
    a = ''
    a += '[[{}]] {}'.format(task.id, task.name)
    if task.priority != '':
        a += ' with priority [[{}]]'.format(task.priority)    
    a += '\n'
    return a
