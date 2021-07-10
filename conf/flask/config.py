import os

try:
    from conf.flask.__private__ import PriProduction, PriTesting, PriDevelopment
except ModuleNotFoundError:
    private_dir = os.path.realpath(os.path.join(__file__ + "/../private/"))
    conf_dir = os.path.realpath(os.path.join(__file__ + "/../"))
    msg = f"\n为了安全起见, 本项目需要自行创建 __private__.py 文件\n"\
          f"\n请手动将\n  {private_dir+'private_template.py'}\n复制到\n"\
          f"  {conf_dir+'__private__.py'}\n\n"\
          f"复制完成后在 __private__.py 中填写正确信息, 并重新启动本项目\n"\
          f"__private__.py 文件中内容均为安全相关的重要信息, 请不要将 __private__.py 文件暴露于公开环境\n"\
          f"private_template.py 极易误传至代码托管平台, 请不要修改 private_template.py 中的任何内容\n"
    raise ModuleNotFoundError(msg)


class ProductionConfig(PriProduction):
    DEBUG = False


class TestingConfig(PriTesting):
    DEBUG = True
    TESTING = True


class DevelopmentConfig(PriDevelopment):
    DEBUG = True
