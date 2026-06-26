import uvicorn

if __name__ == "__main__":
    print("Starting Uvicorn Server on http://localhost:8000")
    # We point Uvicorn to the 'app' object inside 'app/api/server.py'
    # reload=True automatically restarts the server when you save code changes
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)