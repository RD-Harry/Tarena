"""
ftp文件服务器 客户端
"""
from socket import *
import sys,time

# 服务器地址
ADDR = ("127.0.0.1", 8888)


# 请求功能
class FTPClient:
    def __init__(self, sockfd):
        self.sockfd = sockfd

    # 将下面s 这个套接字变成 这个类的属性

    def do_list(self):

        self.sockfd.send(b'L')  # 发送请求
        data = self.sockfd.recv(1024).decode()
        #1024一次最多接收的最大消息 字节
        #data接收到的实际上就是字节串，可以用decode()转换为字符串
        if data == 'OK':
            # 发送请求后如果可以客户端就发送OK
            # 不可以就告知为什么不可以
            """
        收到OK后准备接收数据，但是要考虑粘包问题
        解决粘包问题有两个:
                        ①加时间间隔（比较费时）
                        ②加消息边界
            """
            # 一次接收所有文件 ；-->例如 'file1/nfille/nfile/n...'
            # /n就相当于消息间隔避免粘包
            data = self.sockfd.recv(1024 * 1024)  # 假设1024*1024够用的
            print(data.decode())
        else:
            print(data)

    def do_quit(self):
        self.sockfd.send(b"Q")  # 给服务端发送Q请求退出

        self.sockfd.close()  # 关闭套接字
        sys.exit("thank you very much")  # 程序退出

    def do_get(self, filename):
        # 发送请求
        self.sockfd.send(("G " + filename).encode())
        # 等待回复
        data = self.sockfd.recv(128).decode()
        if data == "OK":
            f = open(filename,'wb')
            while True:
                data = self.sockfd.recv(1024)
                if data == b"##":  # 用“##”作为接收结束的标志
                    break
                f.write(data)
            f.close()  # 最后别忘了关闭文件
        else:
            print(data)
            # 文件上传

    def do_put(self, filename):
        try:
            f = open(filename, 'rb')
        except Exception:
            print('null')
            return
        # 获取文件名 ../../..ss
        # 文件路径最后就是文件的名字
        filename = filename.split('/')[-1]
        # 发送请求
        self.sockfd.send(('P ' + filename).encode())
        # 接收反馈
        data = self.sockfd.recv(128).decode()
        if data == 'OK':
            while True:
                data = f.read(1024)
                if not data:
                    time.sleep(0.1)
                    self.sockfd.send(b"##")
                    break
                self.sockfd.send(data)
            f.close()
        else:
            print(data)


# 搭建网络
def main():
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print(e)
        return

    ftp = FTPClient(s)  # 将ftp变成套接字的属性

    while True:
        print("\n=========hello========")
        print("*         list       *")
        print("*        get file    *")
        print("*        put file    *")
        print("*         quit       *")
        print("*====================*")

        cmd = input(">>")
        # s.send(cmd.encode())
        if cmd.strip() == 'list':
            # 每次发请求的时候都需要关键字-->重复需要关键字
            # 已经将ftp作为了属性，再次调用函数的时候就不需要再传参数了
            # 在类中他的属性变量 他所有的方法都可以使用
            ftp.do_list()
        elif cmd.strip() == 'quit':
            ftp.do_quit()
        elif cmd[:3] == 'get':  # 收到的前三个字母是get,而get后面直接就是文件的名字
            filename = cmd.split(' ')[-1]  # 以空格拆分，最后一个就是名字

            ftp.do_get(filename)
        elif cmd[:3] == 'put':
            filename = cmd.strip().split(' ')[-1]
            ftp.do_put(filename)
        else:
            print('please enter the correct commend')


"""
在一个类中当所有的方法都要用到一个变量时，
就可以考虑将这个变量变成属性
"""

if __name__ == "__main__":
    main()
