# from grpc_server import serve
from compiler import compile

if __name__ == '__main__':

    #app_dir = 'D:/CZU/PengCheng/magellan-pcl/apps/l2'
    app_dir = '/apps/l2'
    dp_file = app_dir + '/on_packet.mag'
    offline_file = app_dir + '/offline.py'
    out_dir = 'out'
    print(compile(dp_file, None))
    
    # t = Thread(target=serve, args=(fp)).start()
    # serve()


