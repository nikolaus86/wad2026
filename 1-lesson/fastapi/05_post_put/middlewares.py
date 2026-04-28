from starlette.requests import Request
import time

async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    print(f"Received request at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Path: {request.url.path}")
    print(f"Method: {request.method}")

    response = await call_next(request)

    end_time = time.perf_counter()
    elapsed_time = f"{(end_time - start_time) * 1000:.0f}"
    print(f"Response time: {elapsed_time} ms")

    response.headers["X-Response-Time"] = elapsed_time

    return response

