import logging
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.requests import Request

import tensorflow as tf

from .detect import start_detect, exec_detect, currentTimeMillis

logger = logging.getLogger(__name__)

the_infer = None

def init(model_path: str) -> None:
    logger.info('< INIT > - -------------')
    logger.info('< INIT > - Load Start...')
    loaded = tf.saved_model.load(export_dir=model_path)
    infer = loaded.signatures['serving_default']
    logger.info('< INIT > - Load DONE.')
    logger.info('< INIT > - -------------')

    global the_infer
    the_infer = infer

#

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event('startup')
def app_startup():
    logger.info('Start...')

    loop = asyncio.get_running_loop()
    start_detect(loop, the_infer)

    logger.info('DONE.')

@app.get('/')
def get_root():
    return { }

@app.post('/detect')
async def post_detect(r: Request):
    return await exec_detect(r)

@app.post('/loop')
async def post_loop(r: Request):
    ts = currentTimeMillis()
    return { 'objects': [], 'ts': [ ts, ts ] }

#
