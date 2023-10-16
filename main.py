from pathlib import Path
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from routers import roles_permissions, users, chats, messages, reactions, websocket, ip_groups
from config import Base, database, engine
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
Base.metadata.create_all(bind=engine)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Replace with your React app's URL
    "https://chat.altajer.org",
    "http://172.234.72.69:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin"],
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(title="API Docs", version="1.0.0", routes=app.routes)


app.include_router(users.router)
app.include_router(roles_permissions.router)
app.include_router(chats.router)
app.include_router(messages.router)
app.include_router(reactions.router)
app.include_router(websocket.router)
app.include_router(ip_groups.router)


# Run
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=8000, reload=True)
