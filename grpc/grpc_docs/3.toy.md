# toy

기존의 프로젝트에  server-client 간 TLS 프로토콜을 사용하여 통신 구현.

최종 디렉토리는 다음과 같이 구성

```bash
├── credentials
│   ├── server.crt
│   └── server.key
├── _credentials.py
├── toy.proto
├── toy_server.py
├── toy_client.py
├── toy_pb2.py
└── toy_pb2_grpc.py
```



## OpenSSL을 이용한 private key, certificate만들기

해당 키를 생성하고자 하는 디렉토리에서 다음 명령어 실행, 본 프로젝트에서는 credentials 디렉토리 생성 후 키 저장

~~~shell
openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt
~~~

> private key(server.key) 와 root certificate(server.crt) 생성
>
> 여러 정보 입력 후 Common Name은 local에서 테스트 시 **localhost**로 입력
>
> remote에서 request를 보내는 경우 해당 서버의 DNS 도메인으로 설정
>
> 배포 시에는 server.crt만 배포 (server.key 외부 유출 X)



## crt & key load 모듈 추가

이전 생성한 키 load를 위하여 모듈을 분리하여 구현

```python
# _credentials.py 

import os

def _load_credential_from_file(filepath):
    real_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(real_path, 'rb') as f:
        return f.read()

SERVER_CERTIFICATE = _load_credential_from_file('credentials/server.crt')
SERVER_CERTIFICATE_KEY = _load_credential_from_file('credentials/server.key')
```



## Server side 수정

서버는 인증서가 자신이 발급한 인증서인지 확인하기 위하여 자신의 private key와 인증서를 가지고 있어야 함.

따라서, 'toy_server.py' 다음 코드를 추가로 삽입

```python
server_credentials = grpc.ssl_server_credentials(((
    _credentials.SERVER_CERTIFICATE_KEY, #private key
    _credentials.SERVER_CERTIFICATE, # certificate
),))

#server.add_insecure_port('[::]:5000')
server.add_insecure_port('[::]:5000',server_credentials)
```

두 정보를 이용하여 서버의 credential를 생성. TLS를 적용하지 않은 코드에서는 server.add_insecue_port를 사용했지만,  TLS를 적용한 secure port를 사용해야 하므로 add_secure_port함수를 사용해야함



## Client side 수정

```python
with open('credentials/server.crt','rb') as f:
    trusted_certs=grpc.ssl_channel_credentials(f.read())
        
   	#channel = grpc.insecure_channel('localhost:5000') 
    channel = grpc.secure_channel('localhost:5000',trusted_certs) 
```

기존과 다르게 서버 연결 시 인증서가 필요. insecure_channel에서 secure_channel로 변경



## Final Code

### proto

~~~protobuf
//login.proto

syntax = "proto3";

service Toy {

  // Login method (unary,unary)
  rpc Login (Member) returns (Reply) {}
  // Login method (unary,stream)
  rpc Calcualte(MulNum) returns (stream Result){}
}

message Member{
  string id=1;
  string pw=2;
}

message Reply{
  bool key = 1;
  Member log=2;
}

message MulNum{
	int32 num=1;
}

message Result{
	string exp=1;
	int32 solution=2;
}
~~~

##### proto compile

~~~shell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./toy.proto 
~~~



### server

~~~python
#toy_server.py

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
~~~



### client

~~~python
#toy_client.py

from __future__ import print_function
import logging
import grpc
import toy_pb2_grpc
import toy_pb2

def run():
    
    with open('credentials/server.crt','rb') as f:
        trusted_certs=grpc.ssl_channel_credentials(f.read())
        
    #channel = grpc.insecure_channel('localhost:5000') 
    channel = grpc.secure_channel('localhost:5000',trusted_certs) 
    stub = toy_pb2_grpc.ToyStub(channel)

    #gui or cli
    response =True

    while response:
        id=input('아이디 입력: ')
        pw=input('패스워드 입력: ')
        response=stub.Login(toy_pb2.Member(id=id,pw=pw)).key
    print('success login\n')

    while True:
        num=input('input num: ')
        response=stub.Calcualte(toy_pb2.MulNum(num=int(num)))
        for tmp in response:
            print(tmp.exp,tmp.solution)

if __name__ == '__main__':
    logging.basicConfig()
    run()
~~~



---

##### reference

https://github.com/grpc/grpc/tree/v1.24.0/examples/python/auth

https://atez.kagamine.me/54
