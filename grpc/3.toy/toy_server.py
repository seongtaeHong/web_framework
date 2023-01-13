from concurrent import futures
import time
import logging
import grpc
import toy_pb2
import toy_pb2_grpc

import _credentials

class Toy (toy_pb2_grpc.ToyServicer):

    def Login(self, request, context):
        id=request.id
        pw=request.pw
        if request.id =='admin' and request.pw=='1234':
            return toy_pb2.Reply(key=False, log=request)
        else:
            return toy_pb2.Reply(key=True,log=request)
        
    
    def Calcualte(self, request, context):

        for n in range(9):
            result=request.num*(n+1)
            exp=str(request.num)+'*'+str(n+1)+'='
            tmp=toy_pb2.Result(exp=exp,solution=result)
            yield tmp


def serve():
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    toy_pb2_grpc.add_ToyServicer_to_server(Toy(),server)


    server_credentials = grpc.ssl_server_credentials(((
        _credentials.SERVER_CERTIFICATE_KEY, #private key
        _credentials.SERVER_CERTIFICATE, # certificate
    ),))

    #server.add_insecure_port('[::]:5000')
    server.add_secure_port('[::]:5000',server_credentials)
    server.start()

    try:
        while True:
            time.sleep

    except KeyboardInterrupt:
        server.stop(0)


if __name__=='__main__':
    logging.basicConfig()
    serve()


