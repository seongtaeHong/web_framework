from concurrent import futures

import grpc
import bi_pb2_grpc
import bi_pb2

class BidirectionalService(bi_pb2_grpc.BidirectionalServicer):

    def GetServerResponse(self, request_iterator, context):
        for message in request_iterator:
            yield message


def serve():
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bi_pb2_grpc.add_BidirectionalServicer_to_server(BidirectionalService(),server)
    server.add_insecure_port('[::]:5000')
    server.start()
    server.wait_for_termination()

if __name__=='__main__':
    serve()

    