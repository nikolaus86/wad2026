from fastapi import FastAPI
from routers.tasks import router as tasks_router
from middlewares import logging_middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

app.middleware("http")(logging_middleware)

# app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost"])

app.include_router(tasks_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

