import datetime

from main.models.exts import scheduler
from main.libs.db_api import UserNodesTable, UserTable


def check_user():
    with scheduler.app.app_context():
        user_api = UserTable()
        user_node_api = UserNodesTable()

        for i in user_api.get_all_user():
            username = i["username"]
            quota = i.get("quota")
            expiry_date = i.get("expiry_date")
            nodes = user_node_api.get_node_for_user_name(username)
            user_node_api.restore_user_traffic(username, nodes)
            if expiry_date and expiry_date < datetime.datetime.now():
                if expiry_date < datetime.datetime.now():
                    user_node_api.limit_user_traffic(username, nodes)
            if quota > 0:
                total = user_api.get_user_use(username, nodes)
                if (quota * 1024 * 1024 * 1024) < total:
                    user_node_api.limit_user_traffic(username, nodes)


jobs = [{
    'id': 'check_user',
    'func': check_user,
    'trigger': 'cron',
    'hour': 21,
    'minute': 33
}]
