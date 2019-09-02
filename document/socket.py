# import websocket1
#
# try:
#     import thread
# except ImportError:
#     import _thread as thread
# import time
#
#
# def on_message(ws, message):
#     print(message)
#
#
# def on_error(ws, error):
#     print(error)
#
#
# def on_close(ws):
#     print("### closed ###")
#
#
# def on_open(ws):
#     def run(*args):
#         for i in range(3):
#             time.sleep(1)
#             ws.send("Hello %d" % i)
#         time.sleep(1)
#         ws.close()
#         print("thread terminating...")
#
#     thread.start_new_thread(run, ())
#
#
# # start_server = websockets.serve(time, "127.0.0.1", 5679)
# #
# # asyncio.get_event_loop().run_until_complete(start_server)
# # asyncio.get_event_loop().run_forever()
#
# if __name__ == "__main__":
#     websocket1.enableTrace(True)
#     ws = websocket1.WebSocketApp("ws://127.0.0.1:8888/",
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close)
#     ws.on_open = on_open
#     ws.run_forever()
import websocket


def on_message(ws, message):
    print(ws)
    print(message)


def on_error(ws, error):
    print(ws)
    print(error)


def on_close(ws):
    print(ws)
    print("### closed ###")


websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://127.0.0.1:8888/track",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()
