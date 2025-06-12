from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "ChemGPT Auth Service is alive!"}
