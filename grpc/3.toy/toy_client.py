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