from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def read_root():
	return {"status": "ok"}

@app.post("/execute")
def execute_code(code: str):
	return eval(code)

if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)
