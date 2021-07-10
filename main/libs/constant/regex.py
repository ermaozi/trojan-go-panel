import re

re_user = re.compile(r"^[a-zA-Z0-9_-]{4,16}$")

re_mail = re.compile(r"^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$")

re_domain = re.compile(r"[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(/.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+/.?")

re_password = re.compile(r"^[a-zA-Z]\w{5,17}$")