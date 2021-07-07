from main.views.index import Index
from main.views.user import Login, User, GetTrojanUrl, Subscribe, DelUser
from main.views.node import Node, GetNodeStatus, DelNode


def init_url(app):
    app.add_url_rule('/', view_func=Index.as_view('index'))
    app.add_url_rule('/login', view_func=Login.as_view('login'))
    app.add_url_rule('/user/user', view_func=User.as_view('user'))
    app.add_url_rule('/user/del', view_func=DelUser.as_view('del_user'))
    app.add_url_rule('/user/subscribe', view_func=Subscribe.as_view('subscribe'))
    app.add_url_rule('/user/get_trojan_url',
                     view_func=GetTrojanUrl.as_view('get_trojan_url'))

    app.add_url_rule('/node/node', view_func=Node.as_view('node'))
    app.add_url_rule('/node/del', view_func=DelNode.as_view('del_node'))
    app.add_url_rule('/node/get_node_status',
                     view_func=GetNodeStatus.as_view('get_node_status'))
