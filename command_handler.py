import db
import sqlalchemy
from db import Task
from url_handler import send_message


def new_task(chat_id, name):
    task = Task(chat=chat_id, name=name, status='TODO', dependencies='', parents='', priority='')
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
        query = db.session.query(Task).filter_by(id=task_id, chat=chat_id)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat_id)
            return

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
        query = db.session.query(Task).filter_by(id=task_id, chat=chat_id)
        try:
            task = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            send_message("_404_ Task {} not found x.x".format(task_id), chat_id)
            return

        dtask = Task(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                        parents=task.parents, priority=task.priority, duedate=task.duedate)
        db.session.add(dtask)

        for t in task.dependencies.split(',')[:-1]:
            qy = db.session.query(Task).filter_by(id=int(t), chat=chat_id)
            t = qy.one()
            t.parents += '{},'.format(dtask.id)

        db.session.commit()
        send_message("New task *TODO* [[{}]] {}".format(dtask.id, dtask.name), chat_id)