from fastapi import FastAPI
from routers.task_3 import router as task_3_router
from routers.task_5 import router as task_5_router
from routers.task_5_4_5 import router as task_5_4_5_router

app = FastAPI()

app.include_router(task_3_router)
app.include_router(task_5_router)
app.include_router(task_5_4_5_router)