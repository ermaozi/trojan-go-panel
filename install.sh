#!/bin/bash

if [ ! -f /.dockerenv ]; then
    #Centos 临时取消别名
    [[ -f /etc/redhat-release && -z $(echo $SHELL | grep zsh) ]] && unalias -a

    RED="31m"
    GREEN="32m"
    YELLOW="33m"
    BLUE="36m"
    FUCHSIA="35m"

    # 项目地址 用户名/仓库名
    project="ermaozi/trojan-go-panel"
    branch="main_1.0.0"
fi

colorEcho() {
    COLOR=$1
    echo -e "\033[${COLOR}${@:2}\033[0m"
}

checkSys() {

    # 修改时区
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

    # 安装前系统检查
    [ $(id -u) != "0" ] && {
        colorEcho ${RED} "错误：您必须使用 root 用户来运行此脚本\nError: You must be root to run this script"
        return 1
    }
    if [[ $(uname -m 2>/dev/null) != x86_64 ]]; then
        colorEcho $YELLOW "请在 x86_64 架构的机器上运行此脚本\nPlease run this script on x86_64 machine"
        return 1
    fi

    if [[ $(command -v apt-get) ]]; then
        PACKAGE_MANAGER='apt-get'
    elif [[ $(command -v dnf) ]]; then
        PACKAGE_MANAGER='dnf'
    elif [[ $(command -v yum) ]]; then
        PACKAGE_MANAGER='yum'
    else
        colorEcho $RED "不支持当前的操作系统！\nNot support OS! "
        return 1
    fi

    if [[ $worknode != 1 ]]; then
        # 检查域名
        read -p "请输入您解析到本机的域名: " input
        if [ ! $(echo "$input" | grep -E "[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?") ]; then
            colorEcho $YELLOW "域名不合法"
            return 1
        fi
        host_ip=$(curl "ipinfo.io/ip" 2>/dev/null)
        domain_ip=$(ping -c 2 $input | head -2 | tail -1 | awk '{print $5}' | sed 's/[(:)]//g')
        if [ x"$host_ip" != x"$domain_ip" ]; then
            colorEcho $YELLOW "域名解析ip($domain_ip)与本机ip($host_ip)不同! 如果该域名曾配置CND, 请将其关闭"
            return 1
        fi
        DOMAIN=$input
        read -p "请输入您预设的数据库密码(自己设置, 自己记住): " input
        mysql_password=$input

        read -p "是否启用主节点trojan?(默认启用, 若需管控多个子节点, 则建议不启用主节点trojan)[Y/N]" input
        if [[ x"$input" == x"" ]]; then
            is_local_trojan="Y"
        else
            is_local_trojan=$input
        fi

        mysql_server_addr=127.0.0.1
        mysql_database=local_trojan
    fi
}

initEvn() {
    # 缺失/usr/local/bin路径时自动添加
    [[ -z $(echo $PATH | grep /usr/local/bin) ]] && {
        echo 'export PATH=$PATH:/usr/local/bin' >>/etc/bashrc
        source /etc/bashrc
    }

    # 安装依赖

    echo "开始安装依赖, 若本系统是初次更新, 将会花费更长的时间. 请耐心等候..."

    ${PACKAGE_MANAGER} install -y socat
    ${PACKAGE_MANAGER} install -y lsof
    ${PACKAGE_MANAGER} install -y tar
    ${PACKAGE_MANAGER} install -y net-tools
    ${PACKAGE_MANAGER} install -y unzip
    ${PACKAGE_MANAGER} install -y git
    ${PACKAGE_MANAGER} install -y openssl
    ${PACKAGE_MANAGER} install -y nginx

    colorEcho $GREEN "依赖安装完成!"

    colorEcho $GREEN "安装并启动 docker"
    docker -v 2>/dev/null || curl -sSL https://get.daocloud.io/docker | sh
    systemctl start docker
    systemctl enable docker.service
    docker --version || colorEcho $RED "docker 安装失败" && return 1
    colorEcho $GREEN "docker 安装成功!"

    # 初始化路径变量
    PLANEL_DIR="/root/trojan-go-panel/"

    CONFIG_DIR="$PLANEL_DIR/conf/"

    SERVERJSON="$CONFIG_DIR/trojan-go/server.json"
    TROJANSERVICE="$CONFIG_DIR/trojan-go/trojan-go.service"
    TROJANSQL="$CONFIG_DIR/sql/trojan-user.sql"

    TROJANCONF="/etc/trojan-go/config.json"
    SYSTEMDPREFIX="/etc/systemd/system"
    SYSTEMDPATH="$SYSTEMDPREFIX/trojan-go.service"

    CERT_PATH="/root/.acme.sh/${DOMAIN}_ecc/fullchain.cer"
    KEY_PATH="/root/.acme.sh/${DOMAIN}_ecc/${DOMAIN}.key"

}

# 安装证书
installTls() {

    echo "开始安装证书"
    # CentOS 需要放开端口
    if [[ ${PACKAGE_MANAGER} != 'apt-get' ]]; then
        firewall-cmd --add-port=80/tcp --permanent
        firewall-cmd --add-port=443/tcp --permanent
        firewall-cmd --reload
    fi
    echo "关闭 80 与 443 端口"
    kill -9 $(lsof -i:80 -t)
    kill -9 $(lsof -i:443 -t)

    rm -rf "/root/.acme.sh/${DOMAIN}_ecc/"
    [ -f ~/.acme.sh/acme.sh ] || curl https://get.acme.sh | sh
    ~/.acme.sh/acme.sh --set-default-ca --server letsencrypt
    bash /root/.acme.sh/acme.sh --issue -d $DOMAIN --debug --standalone --keylength ec-256
    if [[ -d $CERT_PATH ]] && [[ -d $KEY_PATH ]]; then
        colorEcho $GREEN "证书安装成功!"
    else
        colorEcho $RED "证书安装失败！"
        return 1
    fi
}

installMaria() {
    # 检查是否存在 mariadb 容器
    if [[ !$(docker ps --format "{{.Names}}" | grep mariadb) ]]; then
        echo "开始安装 mariadb"
        docker pull mariadb         # 拉取超时可多试几次, 镜像拉取成功后可以通过 docker images 命令进行查看
        mkdir -p /data/mariadb/data # 创建数据存储目录
        kill -9 $(lsof -i:3306 -t)  # 杀死 3306 端口
        docker run --name mariadb -p 3306:3306 -e MYSQL_ROOT_PASSWORD=$mysql_password -v /data/mariadb/data:/var/lib/mysql -d mariadb
        docker container update --restart=always mariadb # 设置容器自启动
        docker restart mariadb -t 20                     # 部分场景 mariadb 容器不会自启动, 这里重启一下
        sleep 10s
    fi
    docker exec mariadb mysql -uroot -p$mysql_password -e "create database main;"
    docker exec mariadb mysql -uroot -p$mysql_password -e "create database $mysql_database;"
    cp $TROJANSQL /data/mariadb/data/
    docker exec mariadb mysql -uroot -p$mysql_password -D $mysql_database -e "source /var/lib/mysql/trojan-user.sql;"
}

# 安装面板与配置文件
installPanel() {
    echo "开始安装面板与配置文件"

    git clone "https://github.com/${project}.git" -b $branch

    cd $PLANEL_DIR

    if [[ $worknode != 1 ]]; then
        docker pull ermaozi/trojan-go-panel
        docker run --name panel -p 80:8080 -e PRO-PASSWORD=$mysql_password -e DOMAIN=$DOMAIN -e BASE_URL="http://${DOMAIN}" -d trojan-go-panel
        if [[ "Nn" =~ "$is_local_trojan" ]]; then
            sed -i "s#is_local_trojan: true#is_local_trojan: false#" $CONFIG_DIR/flask/__setting__.yaml
        fi
    else
        pip install -r requirements_worknode.txt
        uwsgi --ini ./conf/uwsgi/uwsgi-worknode.ini
    fi
}

# 安装 trojan-go
installTrojanGo() {
    echo "开始安装trojan"
    mkdir trojan
    cd trojan

    CHECKVERSION="https://api.github.com/repos/p4gefau1t/trojan-go/releases"
    VERSION=$(curl -H 'Cache-Control: no-cache' -s "$CHECKVERSION" 2>/dev/null | grep 'tag_name' | cut -d\" -f4 | sed 's/v//g' | head -n 1)
    TARBALL="trojan-go-linux-amd64.zip"
    DOWNLOADURL="https://github.com/p4gefau1t/trojan-go/releases/download/v$VERSION/$TARBALL"

    curl -LO --progress-bar "$DOWNLOADURL"
    mkdir -p /etc/trojan-go/
    unzip "$TARBALL"
    if ! [[ -f "$TROJANCONF" ]] || prompt "The server config already exists in $TROJANCONF, overwrite?"; then
        cp "$SERVERJSON" "$TROJANCONF"
        sed -i "s#cert_path#$CERT_PATH#" "$TROJANCONF"
        sed -i "s#key_path#$KEY_PATH#" "$TROJANCONF"
        sed -i "s#mysql_server_addr#$mysql_server_addr#" "$TROJANCONF"
        sed -i "s#mysql_database#$mysql_database#" "$TROJANCONF"
        sed -i "s#mysql_password#$mysql_password#" "$TROJANCONF"
        sed -i "s#domain_name#$DB_DOMAIN#" "$TROJANCONF"
    fi
    if [[ -d "$SYSTEMDPREFIX" ]]; then
        cp "$TROJANSERVICE" "$SYSTEMDPATH"
    fi
    install -Dm755 "trojan-go" "/usr/bin/"
    systemctl daemon-reload
}

# check_flag=0
# check(){
#     netstat -nultp|grep $1 > /dev/null && colorEcho $GREEN $1运行正常 || colorEcho $RED $1未运行;check_flag=1
# }

# run(){
#     echo "启动服务"
#     setsebool -P httpd_can_network_connect 1
#     systemctl start nginx
#     systemctl enable nginx
#     systemctl start trojan-go
#     systemctl enable trojan-go
#     for my_service in trojan-go uwsgi nginx;do
#         check $my_service
#     done
#     if [[ $check_flag -eq 0 ]];then
#         colorEcho $GREEN "服务启动成功!"
#     else
#         colorEcho $RED "服务启动失败!"
#         return 1
#     fi
# }

install() {
    cd "/root"
    checkSys || return
    initEvn || return
    installTls || return
    if [[ $worknode != 1 ]]; then
        installMaria || return
    fi
    installPanel || return
    installTrojanGo || return
    # run || return

    colorEcho $GREEN "全部安装完成!"
    if [[ $worknode != 1 ]]; then
        echo ""
        echo "访问 http://${DOMAIN} 看看吧"
        echo "首次登录需要注册账号, 第一个账号视为管理员, 记得好好保存"
    fi

}

uninstall() {
    echo 111
}

update() {

    current_version=$(cat /root/trojan-go-panel/VERSION 2>/dev/null)
    latest_version=$(curl https://raw.githubusercontent.com/${project}/${branch}/VERSION 2>/dev/null)
    if [ "$(echo "$current_version $latest_version" | tr " " "\n" | sort -rV | head -n 1)" == "$current_version" ]; then
        colorEcho $GREEN "已是最新版: $latest_version"
        return
    fi

    colorEcho $GREEN "$current_version -> $latest_version"

    echo "拉取最新代码"
    cd /root/trojan-go-panel/
    git pull
    source ./venv/bin/activate

    echo "更新依赖"
    pip install -U -r requirements_manage.txt

    echo "更新数据库"
    if [[ ! -d ./migrations ]]; then
        python db_manage.py db init
    fi
    python db_manage.py db migrate
    python db_manage.py db upgrade

    echo "更新配置文件"
    python ./main/libs/setting.py

    echo "重启服务"
    pkill -9 -f uwsgi
    sleep 3s
    uwsgi --ini ./conf/uwsgi/uwsgi-manage.ini

    if [[ $(netstat -nultp | grep uwsgi) ]]; then
        echo "更新成功!"
    else
        echo "更新失败!"
    fi
}

while [[ $# > 0 ]]; do
    KEY="$1"
    case $KEY in
    --worknode)
        worknode=1
        DOMAIN=$2
        mysql_server_addr=$3
        mysql_database=$4
        mysql_password=$5
        if [[ $# != 5 ]]; then
            echo "参数数量错误"
            return 1
        fi
        shift
        ;;
    --uninstall)
        uninstall
        ;;
    --reinstall)
        uninstall
        install
        ;;
    -h | --help)
        HELP=1
        ;;
    *) ;;

    esac
    shift
done

if [[ -d /root/trojan-go-panel/ ]]; then
    update
else
    install
fi
