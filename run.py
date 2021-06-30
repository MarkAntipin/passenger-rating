import uvicorn

from app.app import app


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        port=8080,
        proxy_headers=True,
        access_log=True,
    )
