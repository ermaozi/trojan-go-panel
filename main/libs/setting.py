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

    def update(self):
        """
        更新配置文件
        """
        old_setting = self.get()
        setting_path = os.path.realpath(
            __file__ + "/../../../conf/flask/private/setting_template.yaml")
        with open(setting_path, "rb") as yaml_file:
            setting_template = yaml.load(yaml_file, Loader=yaml.FullLoader)

        new_setting = dict(old_setting, **setting_template)
        for key in new_setting.keys():      # 找回dict1中关键字对应的value
            if key in old_setting:
                new_setting[key] = dict(new_setting[key], **old_setting[key])

        with open(self.setting_path, "wb") as yaml_file:
            yaml_file.write(yaml.dump(new_setting).encode("utf-8"))


setting = Setting()

if __name__ == "__main__":
    setting.update()
