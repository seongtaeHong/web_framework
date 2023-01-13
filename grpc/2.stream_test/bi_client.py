from __future__ import print_function
import bi_pb2_grpc
import bi_pb2
import grpc

def make_message(message):
    return bi_pb2.Message(
        message=message
    )

def generate_message():

    total=[]

    for tmp in range(1000):
        a=str(tmp)
        total.append(make_message(a))
    
    for msg in total:
        print('Hello %s' % msg.message)
        yield msg


def send_message(stub):
    responses=stub.GetServerResponse(generate_message())
    for res in responses:
        print(res.message)



def run():
    channel=grpc.insecure_channel('[::]:5000')
    stub=bi_pb2_grpc.BidirectionalStub(channel)
    send_message(stub)


if __name__=='__main__':
    run()

