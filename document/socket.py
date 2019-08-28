import socket

def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('127.0.0.1', 8001))
        socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket.listen(5)
    except Exception as e:
        print(e)
        return
    else:
        print("server running....")

    # 等待访问
    while True:
        conn, addr = socket.accept()    # 此时会进入 waiting 状态
        data = str(conn.recv(1024))
        print(data)
        header_dict = {}
