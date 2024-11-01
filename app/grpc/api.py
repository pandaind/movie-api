import grpc
from fastapi import APIRouter

from app.grpc.response import GRPCResponse
from grpcserver_pb2 import MessageRequest
from grpcserver_pb2_grpc import GrpcServerStub

router = APIRouter()

grpc_channel = grpc.aio.insecure_channel("localhost:50051")


@router.get("/grpc")
async def call_grpc(message: str) -> GRPCResponse:
    async with grpc_channel as channel:
        grpc_stub = GrpcServerStub(channel)
        response = await grpc_stub.GetServerResponse(MessageRequest(message=message))
        return response
