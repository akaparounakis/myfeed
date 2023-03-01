from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.plot import Plot
from app import api

p = Plot()
p.generate()

app = FastAPI()

app.include_router(api.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
