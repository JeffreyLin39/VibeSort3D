import asyncio
import logging
from concurrent import futures

import grpc
import benchmark.echo_pb2 as echo_pb2
import benchmark.echo_pb2_grpc as echo_pb2_grpc


class EchoServicer(echo_pb2_grpc.EchoServicer):
    async def Ping(self, request, context):
        # Echo payload straight back
        return echo_pb2.PingResponse(payload=request.payload)


async def serve() -> None:
    server = grpc.aio.server()
    echo_pb2_grpc.add_EchoServicer_to_server(EchoServicer(), server)
    server.add_insecure_port("[::]:50051")
    logging.info("gRPC server listening on :50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    asyncio.run(serve())
