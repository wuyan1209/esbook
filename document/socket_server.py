# -*- coding:utf-8 -*-
# 加载WebsocketServer模块

from websocket_server import WebsocketServer
import urllib
from urllib.parse import parse_qs
import json


# 获取连接是调用
def new_client(client, server):
    print("New client connected and was given id %d" % client['id'])
    # 发送给所有的连接
    # server.send_message_to_all("有新人进来了")


# 客户端关闭是调用
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])


# 客户端发送消息时调用
def message_received(client, server, send_message):
    # print((message.encode('utf-8')).decode())
    send_message = json.loads(send_message)
    content = send_message['doc_content']
    if content == "":
        team_name = send_message['team_name']
        team_name = urllib.parse.unquote(team_name)
        send_message['team_name'] = team_name
    else:
        content = urllib.parse.unquote(content)
        send_message['doc_content'] = content
    # print(type(send_message))
    # print(send_message)
    # message = urllib.parse.unquote()
    # print("Client(%d) said: %s" % (client['id'], message))
    # print("teamId:", teamId)

    # 发送给所有的连接
    send_message = str(send_message)
    server.send_message_to_all(send_message)


# Server Port
PORT = 9001
# 创建Websocket Server
server = WebsocketServer(PORT, host="0.0.0.0")
# 有设备连接上了
server.set_fn_new_client(new_client)
# 断开连接
server.set_fn_client_left(client_left)
# 接收到信息
server.set_fn_message_received(message_received)
# 开始监听
server.run_forever()
