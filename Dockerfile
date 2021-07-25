# 使用基础镜像库
FROM ermaozi/nginx_uwsgi_py3:alpine3.8

# 创建工作路径
RUN mkdir -p /trojan-go-panel/

# 指定容器启动时执行的命令都在app目录下执行
WORKDIR /trojan-go-panel

COPY . /trojan-go-panel

RUN pip install -r /trojan-go-panel/requirements_manage.txt -i  https://pypi.tuna.tsinghua.edu.cn/simple some-package --no-cache-dir

RUN cp /trojan-go-panel/conf/nginx/nginx.conf /etc/nginx/nginx.conf

ENTRYPOINT nginx -g "daemon on;" && uwsgi --ini /trojan-go-panel/conf/uwsgi/uwsgi-manage.ini