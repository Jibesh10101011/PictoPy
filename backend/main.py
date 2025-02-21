"""
This module contains the main FastAPI application.
"""

from uvicorn import Config, Server
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from app.database.faces import cleanup_face_embeddings, create_faces_table
from app.database.images import create_image_id_mapping_table, create_images_table
from app.database.albums import create_albums_table
from app.database.yolo_mapping import create_YOLO_mappings
from app.facecluster.init_face_cluster import get_face_cluster, init_face_cluster
from app.routes.test import router as test_router
from app.routes.images import router as images_router
from app.routes.albums import router as albums_router
from app.routes.facetagging import router as tagging_router
import multiprocessing
from app.custom_logging import CustomizeLogger




@asynccontextmanager
async def lifespan(app: FastAPI):
    create_YOLO_mappings()
    create_faces_table()
    create_image_id_mapping_table()
    create_images_table()
    create_albums_table()
    cleanup_face_embeddings()
    init_face_cluster()
    yield
    face_cluster = get_face_cluster()
    if face_cluster:
        face_cluster.save_to_db()


app = FastAPI(lifespan=lifespan)


from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = ".".join(error["loc"])  # Gets the field name
        msg = error["msg"]  # Extracts the error message
        error_messages.append(f"{field}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "Invalid request payload",
            "errors": error_messages
        },
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "PictoPy Server is up and running!"}


app.include_router(test_router, prefix="/test", tags=["Test"])
app.include_router(images_router, prefix="/images", tags=["Images"])
app.include_router(albums_router, prefix="/albums", tags=["Albums"])
app.include_router(tagging_router, prefix="/tag", tags=["Tagging"])


# Runs when we use this command: python3 main.py (As in production)
if __name__ == "__main__":
    multiprocessing.freeze_support()  # Required for Windows.
    app.logger = CustomizeLogger.make_logger("app/logging_config.json")
    config = Config(app=app, host="0.0.0.0", port=8000, log_config=None)
    server = Server(config)
    server.run()
