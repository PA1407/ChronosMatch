from fastapi import FastAPI

app = FastAPI(title="ChronusMatch")
@app.get("/success")
def success():
    return {"message": "Success!"}