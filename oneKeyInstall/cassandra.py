# -*- coding: utf-8 -*-
import os
import socket
import urllib
import logging
import signal
import time
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    )

# !!! remember to change this attr
# jdk download URl
jdk_download_url = "http://download.oracle.com/otn-pub/java/jdk/8u102-b14/jdk-8u102-linux-x64.tar.gz"
# C* download Url
c_download_url = "http://mirror.bit.edu.cn/apache/cassandra/3.7/apache-cassandra-3.7-bin.tar.gz"
# C* name with version,refrence from the download url
CASSANDRA_FULL_NAME = "apache-cassandra-3.7"
# input the cluster name,every node in one cluster have to be same
CLUSTER_NAME = "Demo Cluster v3.1"
# set the seed server ip here
SEED_IP = "10.206.132.76"



def jdk_setup():
    """
	download and setup JDK first
	"""
    logging.info("downloading jdk...")
	# config the jdk download link
    jdk_url = jdk_download_url
    jdk_path = "/usr/lib/java/"
    # jdk_path = "/home/calvin/java_test/"
    if not os.path.exists(jdk_path):
        os.makedirs(jdk_path)
    dest_path = os.path.join(jdk_path, "jdk.tar.gz")
    urllib.urlretrieve(jdk_url, dest_path)
    if os.path.isfile(dest_path):
        logging.info("jdk download success，unzip...")
        os.system("cd " + jdk_path + " && " + "tar -xzf " + dest_path)
        os.system("cd " + jdk_path + " && " + "mv jdk1* jdk")
        logging.info("unzip finished")

    # if never set up the java env
    if os.getenv("JAVA_HOME") != None :
        with open("/etc/profile", 'a') as f:
            lines = ("export JAVA_HOME=/usr/lib/java/jdk\n",
                     "export PATH=$JAVA_HOME/bin:$JAVA_HOME/jre/bin:$PATH\n",
                     "export CLASSPATH=$CLASSPATH:.:$JAVA_HOME/lib:$JAVA_HOME/jre/lib\n")
            f.writelines(lines)
    os.system('''sudo update-alternatives --install "/usr/bin/java" "java" "/usr/lib/java/jdk/bin/java" 1 ''')
    os.system('''sudo update-alternatives --install "/usr/bin/javac" "javac" "/usr/lib/java/jdk/bin/javac" 1''')
    os.system('''sudo update-alternatives --set java /usr/lib/java/jdk/bin/java ''')
    os.system('''sudo update-alternatives --set javac /usr/lib/java/jdk/bin/javac''')
    logging.info("jdk env deploy success")


def cassandra_setup():
    """
    download the tar package and decompression
    """
    # setup Cassandra
    logging.info("downloading Cassandra...")
    c_url = c_download_url
    c_path = "/Project/"
    if not os.path.exists(c_path):
        os.makedirs(c_path)
    cassandra_dest_path = os.path.join(c_path, "cassandra.tar.gz")
    urllib.urlretrieve(c_url, cassandra_dest_path)
    if os.path.isfile(cassandra_dest_path):
        logging.info("cassandra download success，unzip...")
        os.system("cd " + c_path + " && " + "tar -xzf " + cassandra_dest_path)
        # os.system("cd " + c_path + " && " + "mv apache* " + CASSANDRA_FULL_NAME + "")
        # os.system("mv ./resources/*.jar /Project/" + CASSANDRA_FULL_NAME + "/lib/")
        logging.info("cassandra setup finished")


# 获取ip
def get_my_ip():
    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('223.5.5.5', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def cassandra_deploy():
    """
    change the cassandra.yaml,config the cluster name,seed ip and so on
    will replace the default yaml by the yaml template,so please check the template if you want to change more configs
    """
    logging.info("deploying cassandra...")
    os.system("cd /Project/" + CASSANDRA_FULL_NAME + "/conf" + " && " + "sudo mv cassandra.yaml cassandra.yaml.backup")
    os.system("sudo cp ./resources/cassandra_template_3.yaml /Project/" + CASSANDRA_FULL_NAME + "/conf/cassandra.yaml")
    f = open("/Project/" + CASSANDRA_FULL_NAME + "/conf/cassandra.yaml")
    content = f.read()
    f.close()
    ip = get_my_ip()
    logging.info("local ip: " + ip)
    content = content.replace("{name}", CLUSTER_NAME)
    content = content.replace("{local_ip}", ip)

    # seed ip
    content = content.replace("{seed_ip}", SEED_IP)

    # if has '/data' dir ,then change the cache to the '/data' dir ,recommend to set to another disk
    if os.path.exists("/data"):
        if not os.path.exists("/data/cassandra/data"):
            os.makedirs("/data/cassandra/data")
        if not os.path.exists("/data/cassandra/saved_caches"):
            os.makedirs("/data/cassandra/saved_caches")
        content = content.replace("#{data_file_directories}", "data_file_directories:\n      - /data/cassandra/data")
        content = content.replace("#{saved_caches_directory}",
                                  "saved_caches_directory: /data/cassandra/saved_caches")
        # 权限设置
        os.system("sudo chown -R user:user /data")

    f = open("/Project/" + CASSANDRA_FULL_NAME + "/conf/cassandra.yaml", "w")
    f.write(content)
    f.close()
    # 权限设置
    os.system("sudo chown -R user:user /Project")
    logging.info("cassandra deploy finished")


def system_conf():
    """
    change other system config ,like hostname,hosts,timezone ....
    """
    ip_list = get_my_ip().split('.')
    hostname = "cassandra-cluster-" + ip_list[2] + "-" + ip_list[3]
    with open("/etc/hostname", "r") as f:
        old_hostname = f.read().strip()
    with open("/etc/hostname", "w") as f:
        f.write(hostname)
    with open("/etc/hosts", "r") as f:
        content = f.read()
    with open("/etc/hosts", "w") as f:
        content = content.replace(old_hostname, hostname)
        f.write(content)
    #with open("/etc/resolv.conf", "a") as f:
    #    f.write("nameserver 10.64.1.55")
    # timezone
    os.system("sudo timedatectl set-timezone Asia/Shanghai")
    logging.info("system info modify finished")


def soft_setup():
    """
    install helper software ,like supervisor and libjna
    also copy the conf file to set up the supervisor
    """
    # apt-get source update
    # os.system("mv /etc/apt/sources.list /etc/apt/sources.list.backup")
    # os.system("cp ./resources/sources.list /etc/apt/sources.list")
    # os.system("sudo apt-get update")
    
    # supervisor安装
    if not os.path.exists("/var/log/cassandra/"):
        os.makedirs("/var/log/cassandra/")
    os.system("sudo apt-get install supervisor -y")
    os.system("sudo cp ./resources/cassandra_supervisor.conf /etc/supervisor/conf.d/cassandra_supervisor.conf")
    os.system("sudo supervisorctl reload")
    logging.info("supervisor OK!")

    # libjna
    os.system("sudo apt-get install libjna-java -y")
    logging.info("libjna-java OK")


def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)


def reboot_cassandra(timespan=0):
    """
    reboot the cassandra
    """
    time.sleep(timespan * 60)
    check_kill_process('cassandra')
    time.sleep(20)
    ret = os.system("/Project/" + CASSANDRA_FULL_NAME + "/bin/cassandra")
    if ret != 0:
        # todo sendmail
        pass


def reboot_timespan_baseIP():
    ip_str = get_my_ip()
    lastnum_ip = (int)(ip_str.split('.')[-1])
    if lastnum_ip == 1:
        return 0
    elif lastnum_ip >= 4:
        return 2 * (lastnum_ip - 3)


def reboot(i=None):
    print '!!!Need reboot to make all your jobs update!'
    if i is None:
        num = raw_input(" reboot now? 1:yes 2:no ")
    else:
        num = i
    if num == '1':
        os.system("sudo reboot")


def welcome():
    print '''

    1 :install and config jdk
    2 :install cassandra
    3 :config cassandra(modify the template first!)
    4 :modify system info(hostname,hosts,resolv.conf)
    5 :install and config supervisor and libjna-java
    6 :reboot
    7 :exit
    0 :all operation above
    '''
    num = raw_input("please select one item:\n")
    return num


def main(i=None):
    if i is None:
        num = welcome()
    else:
        num = i

    if num == '1':
        jdk_setup()
    elif num == '2':
        cassandra_setup()
    elif num == '3':
        cassandra_deploy()
    elif num == '4':
        system_conf()
    elif num == '5':
        soft_setup()
    elif num == '6':
        reboot()
    elif num == '0':
        jdk_setup()
        cassandra_setup()
        cassandra_deploy()
        system_conf()
        soft_setup()
        reboot('1')
    elif num == 'update':
        cassandra_setup()
        cassandra_deploy()
        soft_setup()
        reboot('1')
    else :
        return
        # print reboot_timespan_baseIP()


if __name__ == '__main__':
    params = sys.argv
    if len(params) == 2:
        main(params[1])
    else:
        main()
