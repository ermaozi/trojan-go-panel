from main.models.exts import scheduler
from main.libs.db_api import UserNodesTable, UserTable, check_user


def cron_check_user():
    with scheduler.app.app_context():
        user_api = UserTable()
        user_node_api = UserNodesTable()

        check_user(user_api, user_node_api)


jobs = [{
    'id': 'check_user',
    'func': cron_check_user,
    'trigger': 'cron',
    'hour': 0,
    'minute': 30
}]
