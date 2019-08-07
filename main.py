# from grpc_server import serve
from compiler import compile

if __name__ == '__main__':
    app_dir = 'apps/l3'
    dp_file = app_dir + '/on_packet.mag'
    offline_file = app_dir + '/offline.py'
    out_dir = 'out'
    compile(dp_file, None)
    # t = Thread(target=serve, args=(fp)).start()
    # serve()


