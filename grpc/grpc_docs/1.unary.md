

# unary



### proto

~~~protobuf
//helloworld.proto

syntax = "proto3";

package helloworld;

// 서비스 정의
service Greeter {

  rpc SayHello (HelloRequest) returns (HelloReply) {}

  rpc SayHelloAgain(HelloRequest) returns (HelloReply){}
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
}
~~~

> service는 RPC를 통해 서버가 클라이언트에게 제공할 함수 형태 정의
>
> message는 protofile에서 주고 받는 data 정의



~~~shell
python -m grpc_tools.protoc -I./. --python_out=. --grpc_python_out=. ./hellowolrd.proto	
~~~

> -I : import를 탐색할 디렉토리 지정
>
> python_out, grpc_python_out: python 소스 파일의 output directory 지정



### server

~~~python
#greeter_server.py

from concurrent import futures
import time
import logging
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

# 서비스 이름으르 클래서 생성, 서비스 이름+{Servicer}의 클래스 상속
class Greeter(helloworld_pb2_grpc.GreeterServicer):

    # proto에서 지정한 메소드 구현, request, context인자 받음
    # request 데이터 활용을 위해서 request.{메시지 형식 이름}으로 호출
    # 응답시 메소드 return에 proto buffer 형태로 메시지 형식에 내용을 적어 반환
    def SayHello(self, request, context):
        return helloworld_pb2.HelloReply(message='Hello, %s!' % request.name)
        
    def SayHelloAgain(self,request,context):
        return helloworld_pb2.HelloReply(message='hello again, %s' %request.name)


def serve():
    # 서버 정의 시, futures의 멀티 스레딩을 이용하여 서버 가동
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # 위에서 정의한 서버 저장
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    # port 연결
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
~~~

### client

~~~python
#greeter_client.py

from __future__ import print_function
import logging
import grpc
import helloworld_pb2
import helloworld_pb2_grpc


def run():
    #해당 port, insecure channel에 연결
    channel = grpc.insecure_channel('localhost:50051') 
    # stub 생성
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    # request & recieve, 서버에서 지정한 메소드에 요청 시 proto 메시지 형식으로 요청 전송
    response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)
    response=stub.SayHelloAgain(helloworld_pb2.HelloRequest(name='you'))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()
~~~

> server 실행 후 client 실행