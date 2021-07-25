# 配置基础镜像
FROM alpine:3.8

# 添加标签说明
LABEL author="ermaozi" email="admin@ermao.net"  purpose="nginx+uwsgi+Python3基础镜像"

# 配置清华镜像地址
RUN echo "https://mirror.tuna.tsinghua.edu.cn/alpine/v3.8/main/" > /etc/apk/repositories

# 更新升级软件
RUN apk add --update --upgrade

# 安装软件
RUN apk update && apk upgrade && apk add gcc musl-dev libc-dev libc6-compat linux-headers build-base git libffi-dev openssl-dev nginx python3 uwsgi uwsgi-python3 python3-dev

# 升级pip，这一步同时会在/usr/bin/目录下生成pip可执行文件
RUN pip3 install --no-cache-dir --upgrade pip

# 建立软链接
RUN ln -s /usr/bin/python3 /usr/bin/python
