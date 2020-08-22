"""
FTP 服务器客户端
env python 3.6
多线程 tcp 并发
"""
from socket import *
from threading import *
import sys, os
import time

# 全局变量
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)
FTP = "/home/tarena/PycharmProjects/hannah/"  # 文件库位置，后面加一个/是为了方便后面拼接直接+就可以了


# 客户端处理类  查看服务器  上传、下载
class FTPSever(Thread):
    def __init__(self, connfd):
        super().__init__()  # 调用父类构造函数
        # 因为后面很多地方用到connfd所以干脆写到类里面
        self.connfd = connfd



    def do_list(self):
        # 获取文件列表
        file_list = os.listdir(FTP)
        if not file_list:
            self.connfd.send("文件库为空".encode())
            #n=connfd.send(data)流式套接字发送消息，
            # 发送的内容要求是bytes格式
            return
        else:
            self.connfd.send(b"OK")
            time.sleep(0.1)  # 这里加是为了防止“OK”与后面粘包 最好加上

        # files = ''
        # for file in file_list :
        #    files += file +'\n'
        # 发送文件??? √
        files = "\n".join(file_list)  # \n直接拼接列表中的字符串
        self.connfd.send(files.encode())

    # 先判断文件是否存在，用try尝试打开
    def do_get(self, filename):
        try:
            f = open(FTP + filename, 'rb')  # 根指定的路径用rb打开
        except Exception as e:
            self.connfd.send('文件不存在'.encode())
            return  # 跳出
        else:
            self.connfd.send(b"OK")  # 表示文件存在批准get请求
            time.sleep(0.1)
        while True:  # 循环读取+循环发送文件
            # 循环读取到文件结尾时会读到空
            data = f.read(1024)
            if not data:
                # 读到空时就发送结束标志"##"
                time.sleep(0.1)
                self.connfd.send(b'##')
                break
            self.connfd.send(data)  # 打开的时候是rb方式打开的，
            # 所以直接发送就可以了
            # self.connfd.send(b"hhhnnnhh")
        f.close()  # 关闭文件

    ##文件上传
    def do_put(self, filename):
        if os.path.exists(FTP + filename):
            self.connfd.send('文件已存在'.encode())
            return
        else:
            self.connfd.send(b'OK')
            #接收文件
        f = open(FTP + filename, 'wb')
        while True:
            data = self.connfd.recv(1024)
            if data == b'##':
                break
            f.write(data)
        f.close()
    # def do_put(self, filename):
    #     pass
    def run(self):
        # 接收所有客户端请求
        while True:
            data = self.connfd.recv(1024).decode()
            # print(data)
            if not data or data == "Q":
                # 考虑到客户端有可能的因为日输入有误等其他情况退出
                # 所以放到前面写
                return  # return后就是run()退出了，
                # run()退出对应的线程就结束了
            elif data == 'L':
                self.do_list()
            elif data[0] == "G":  # 第一个字母是G
                filename = data.split(' ')[-1]
                self.do_get(filename)
            elif data[0] == "P":
                filename = data.split(' ')[-1]
                self.do_put(filename)

# 搭建网络模型
def main():
    # 创建tcp套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)#绑定地址，包括IP和端口号
    s.listen(3)#3是监听队列的大小，比如说有3个客户端想同时连接，
    # 处理第一个客户端的时候其他的就先在队列里面等
    #讲套接字设置成一个监听套接字才能被客户端连接
    #注意，在Windows和MacOS里面是管用的但是在Linux里面默认使用系统的监听队列
    print('listen the port 8889')
    # 循环等待客户端连接
    while True:
        try:
            c,addr = s.accept()#accept()为阻塞函数，s是处理客户端连接的套接字
            # 程序执行到这个位置的时候会暂停执行
            #等到满足一定条件的时候再继续执行
            #返回值c:这是个新的套接字，负责和客户端交互通信
            #创建新的套接字就是每个客户端都有一个新的套接字（管家）
            #返回值addr:
            print("connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务端退出")
        except Exception as e:
            print(e)
            continue

        # 有一个客户端进来就创建一个线程
        t = FTPSever(c)
        t.setDaemon(True)
        t.start()


if __name__ == '__main__':
    main()
