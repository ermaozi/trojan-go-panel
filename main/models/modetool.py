from main.models.mode import db

__all__ = ["create_db", "Database"]


def create_db():
    db.create_all()


class Database(object):
    def __init__(self, db_obj) -> None:
        self.db_obj = db_obj()

    def check_password_for_name(self, username, password) -> bool:
        """
        检查密码
        """
        tag = self.db_obj.query.filter_by(username=username).first()
        return tag.check_password(password)

    def insert(self, data_dict: dict):
        """
        向表中插入数据
        """
        self.db_obj.__dict__.update(data_dict)
        pwd = data_dict.get("password")
        if pwd:
            self.db_obj.password = pwd
        db.session.add(self.db_obj)
        db.session.commit()

    def insert_list(self, obj, data_list: list):
        """
        向表中插入多行数据
        """
        obj_list = []
        for data in data_list:
            obj_list.append(obj(**data))
        db.session.add_all(obj_list)
        db.session.commit()

    def delete(self, condition):
        """
        删除表中数据
        """
        if not condition:
            raise Exception("必须给定条件")
        obj_list = self.db_obj.query.filter_by(**condition).all()
        for obj in obj_list:
            db.session.delete(obj)
        db.session.commit()

    def update(self, condition, data_dict):
        """
        更新表中数据
        """
        if not condition:
            raise Exception("必须给定条件")
        self.db_obj.query.filter_by(**condition).update(data_dict)
        db.session.commit()

    def select(self, condition={}, result=[]):
        """
        查询表中数据
        """
        db_data = self.db_obj.query.filter_by(**condition)
        try:
            result = result if result else db_data[0].__dict__.keys()
        except:
            return []

        ret_list = []
        for i in db_data:
            data_dict = i.__dict__
            tmp_dict = {}
            for key in result:
                if key.startswith("_"):
                    continue
                tmp_dict[key] = data_dict.get(key)
            ret_list.append(tmp_dict)
        return ret_list

    def ad_select(self, condition: str, result: list) -> list:
        """
        高级查找, 非常不安全
        condition:

        result: [
            "result_key1",
            "result_key2",
            ...
        ]

        return: {
            "result_key1": value1,
            "result_key2": value2,
            ...
        }
        """
        condition = condition.replace("=", "==")
        condition = condition.replace("&", " and ")
        condition = condition.replace("|", " or ")

        ret_list = []
        for i in self.db_obj.query.all():
            data_dict = i.__dict__
            if not eval(condition.format(**data_dict)):
                continue
            tmp_dict = {}
            for key in result:
                tmp_dict[key] = data_dict.get(key)
            ret_list.append(tmp_dict)
        return ret_list
