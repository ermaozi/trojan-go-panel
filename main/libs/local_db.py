import pymysql
from hashlib import sha224
from flask import current_app


class DBApi():
    def __init__(self, database="") -> None:
        if not database:
            database = current_app.config["DATABASE"]
        port = int(current_app.config["PORT"])
        self.db = pymysql.connect(host=current_app.config["HOST"],
                                  user=current_app.config["USERNAME"],
                                  password=current_app.config["PASSWORD"],
                                  db=database,
                                  port=port)
        self.cur = self.db.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def create_db(self, db_name):
        cur = self.db.cursor()
        sql = f"create database {db_name}"
        cur.execute(sql)

    def create_tb(self):
        cur = self.db.cursor()
        sql = """CREATE TABLE users (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                    username VARCHAR(64) NOT NULL,
                    password CHAR(56) NOT NULL,
                    quota BIGINT NOT NULL DEFAULT 0,
                    download BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    upload BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    PRIMARY KEY (id),
                    INDEX (password)
                );
               """
        cur.execute(sql)

    def select(self):

        # 使用cursor()方法获取操作游标
        cur = self.db.cursor()

        # 1.查询操作
        # 编写sql 查询语句  user 对应我的表名
        sql = "select * from users"
        cur.execute(sql)  # 执行sql语句

        results = cur.fetchall()  # 获取查询的所有记录
        # 遍历结果
        print(results)

    def insert_user(self, username, password):

        # 1.查询操作
        password = sha224(password.encode()).hexdigest()
        sql = "select password from users"
        self.cur.execute(sql)  # 执行sql语句

        results = [i[0] for i in self.cur.fetchall() if i]
        if password in results:
            print("错误")
            return "错误"
        sql = f'insert into users (username,password,quota) value ("{username}","{password}",-1);'
        self.cur.execute(sql)  # 执行sql语句
        self.db.commit()

    def close(self):
        if self.db:
            self.db.close()
        if self.cur:
            self.cur.close()
