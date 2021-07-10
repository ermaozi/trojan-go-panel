import yaml
import os


class Setting(object):
    def __init__(self) -> None:
        self.setting_path = os.path.realpath(
            __file__ + "/../../../conf/flask/__setting__.yaml")

    def get(self, main="", sub=""):
        try:
            with open(self.setting_path, "rb") as yaml_file:
                yaml_obj = yaml.load(yaml_file, Loader=yaml.FullLoader)

            if main:
                if sub:
                    return yaml_obj[main][sub]
                return yaml_obj[main]
            return yaml_obj
        except KeyError as e:
            raise Exception(f"查询配置失败, 传入的 key 有误: {str(e)}")

    def set(self):
        pass


setting = Setting()

if __name__ == "__main__":
    print(setting.get("trojan", "is_local_trojan"))
