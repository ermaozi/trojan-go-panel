# 使用基础镜像库
FROM ermaozi/nup

LABEL author="ermaozi" email="admin@ermao.net"  purpose="trojan-go面板"

# 创建工作路径
RUN mkdir -p /trojan-go-panel/

# 指定容器启动时执行的命令都在app目录下执行
WORKDIR /trojan-go-panel

COPY . /trojan-go-panel

RUN pip install -r /trojan-go-panel/requirements_manage.txt -i  https://pypi.tuna.tsinghua.edu.cn/simple some-package --no-cache-dir

RUN cp /trojan-go-panel/conf/nginx/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT sed -i "s#BASE_URL#${BASE_URL}#" /trojan-go-panel/web/static/config.js && nginx -g "daemon on;" && uwsgi --ini /trojan-go-panel/conf/uwsgi/uwsgi-manage.ini