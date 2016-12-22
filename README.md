# HostSysnc 项目介绍

### 功能

HostSync是基于zookeeper的hosts文件分布式同步应用，可以通过hostsysnc将指定的hosts文件内容一次性同步到所有运行
hostsync的服务上

### 使用手册
Hostsync 有两种运行模式

  * 命令模式: 用于查看和推送目前同步的hosts文件内容
  * 守护进程模式 监听zookeeper并更新服务器上的hosts 文件

使用方式:

  * hostsync.py show : 查看zookpee服务上目前同步的hosts项
  * hostsync.py push <文件名>: 推送需要同步的hosts内容
  * hostsync.py help 查看帮助
  * hostsync.py daemon 守护进行运行


### 目前完成进度
  已经实现正常的hosts推送、查看已经自动更新, 下一步将完善异常处理，以及在守护进程模式下日志的相关记录
