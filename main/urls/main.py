from main.views.index import Index
from main.views.user import Login, Register, GetAllUser, SetUser, DelUser, GetTrojanUrl, Subscribe
from main.views.node import AddNode, GetNodeStatus, GetNodeInfo


def init_url(app):
    app.add_url_rule('/', view_func=Index.as_view('index'))
    app.add_url_rule('/user/login', view_func=Login.as_view('login'))
    app.add_url_rule('/login', view_func=Login.as_view('login'))
    app.add_url_rule('/user/register', view_func=Register.as_view('register'))
    app.add_url_rule('/user/get_all_user',
                     view_func=GetAllUser.as_view('get_all_user'))
    app.add_url_rule('/user/set_user', view_func=SetUser.as_view('set_user'))
    app.add_url_rule('/user/del_user', view_func=DelUser.as_view('del_user'))
    app.add_url_rule('/user/subscribe', view_func=Subscribe.as_view('subscribe'))
    app.add_url_rule('/user/get_trojan_url',
                     view_func=GetTrojanUrl.as_view('get_trojan_url'))

    app.add_url_rule('/node/add_node', view_func=AddNode.as_view('add_node'))
    app.add_url_rule('/node/get_node_info',
                     view_func=GetNodeInfo.as_view('get_node_info'))
    app.add_url_rule('/node/get_node_status',
                     view_func=GetNodeStatus.as_view('get_node_status'))
