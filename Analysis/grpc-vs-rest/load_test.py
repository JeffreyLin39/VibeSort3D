# load_test.py
"""
Asynchronous benchmark driver.
Example:
    python load_test.py --protocol grpc --payload 128 --concurrency 32 --requests 100000
    python load_test.py --protocol rest --payload 65536 --concurrency 32 --requests 10000
"""
import argparse
import asyncio
import base64
import json
import statistics
import time
from typing import List

import grpc
import httpx
import numpy as np

import benchmark.echo_pb2 as echo_pb2
import benchmark.echo_pb2_grpc as echo_pb2_grpc


def percentile(latencies: List[float], p: float) -> float:
    return float(np.percentile(np.asarray(latencies), p))


async def worker_grpc(
    stub: echo_pb2_grpc.EchoStub, payload: bytes, sem: asyncio.Semaphore, latencies: list
):
    async with sem:
        start = time.perf_counter()
        await stub.Ping(echo_pb2.PingRequest(payload=payload))
        latencies.append(time.perf_counter() - start)


async def worker_rest(
    client: httpx.AsyncClient, payload64: str, sem: asyncio.Semaphore, latencies: list
):
    async with sem:
        start = time.perf_counter()
        await client.post("/ping", json={"payload": payload64})
        latencies.append(time.perf_counter() - start)


async def run_grpc(args) -> None:
    payload = bytes(args.payload)
    latencies: List[float] = []
    sem = asyncio.Semaphore(args.concurrency)
    async with grpc.aio.insecure_channel("localhost:50051") as channel:
        stub = echo_pb2_grpc.EchoStub(channel)
        tasks = [
            asyncio.create_task(worker_grpc(stub, payload, sem, latencies))
            for _ in range(args.requests)
        ]
        t0 = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - t0
    report(latencies, elapsed, args)


async def run_rest(args) -> None:
    payload64 = base64.b64encode(bytes(args.payload)).decode()
    latencies: List[float] = []
    sem = asyncio.Semaphore(args.concurrency)
    async with httpx.AsyncClient(base_url="http://localhost:8080") as client:
        tasks = [
            asyncio.create_task(worker_rest(client, payload64, sem, latencies))
            for _ in range(args.requests)
        ]
        t0 = time.perf_counter()
        await asyncio.gather(*tasks)
        elapsed = time.perf_counter() - t0
    report(latencies, elapsed, args)


def report(latencies: List[float], elapsed: float, args) -> None:
    avg = statistics.mean(latencies) * 1e3  # ms
    p95 = percentile(latencies, 95) * 1e3
    p99 = percentile(latencies, 99) * 1e3
    rps = args.requests / elapsed
    print(
        f"\n=== {args.protocol.upper()} RESULTS ===\n"
        f"Total requests     : {args.requests:,}\n"
        f"Concurrency        : {args.concurrency}\n"
        f"Payload size       : {args.payload} bytes\n"
        f"Elapsed time       : {elapsed:.2f} s\n"
        f"Throughput         : {rps:,.0f} req/s\n"
        f"Avg latency        : {avg:.2f} ms\n"
        f"P95 latency        : {p95:.2f} ms\n"
        f"P99 latency        : {p99:.2f} ms\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="gRPC vs REST load tester")
    parser.add_argument(
        "--protocol",
        choices=["grpc", "rest"],
        required=True,
        help="Which server to hit",
    )
    parser.add_argument("--payload", type=int, default=128, help="Payload size in bytes")
    parser.add_argument("--concurrency", type=int, default=32, help="Concurrent workers")
    parser.add_argument("--requests", type=int, default=100_000, help="Total requests")
    args = parser.parse_args()
    if args.protocol == "grpc":
        asyncio.run(run_grpc(args))
    else:
        asyncio.run(run_rest(args))


if __name__ == "__main__":
    main()
