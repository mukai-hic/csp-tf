# detect

import logging
import asyncio
import json
import time

from asyncio.events import AbstractEventLoop

from concurrent.futures import ThreadPoolExecutor

from starlette.requests import Request

import tensorflow as tf

#

logger = logging.getLogger(__name__)

the_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='detect')

the_main_loop : AbstractEventLoop = None
the_infer = None

#

def currentTimeMillis() -> int:
    return int(time.time() * 1000)

def start_detect(loop : AbstractEventLoop, infer) -> None:
    global the_main_loop
    the_main_loop = loop
    global the_infer
    the_infer = infer

#

def do_detect(data: bytes) -> dict:
    try:
        return do_detect_impl(data)
    except Exception as ex:
        logger.exception(f'[do_detect] : {ex}')
        return { }

def do_detect_impl(data: bytes) -> dict:
    tms = currentTimeMillis()

    image = tf.io.decode_jpeg(data)
    inptn = tf.expand_dims(image, axis=0)

    # logger.info('[do_detect] : infer...')
    outtn = the_infer(inptn)

    tme = currentTimeMillis()
    # logger.info('[do_detect] : DONE.')

    res = format_out(outtn)

    res['ts'] = [ tms, tme ]

    logger.info(f'[do_detect] : {json.dumps(res)}')

    return res

#

def format_out(outtn) -> dict:
    # print(outtn)

    oprobs = outtn['output_1'][0]
    oboxs  = outtn['output_0'][0]
    otypes = outtn['output_2'][0]

    obs = list()
    for i in range(len(oprobs)):
        prob = float(oprobs[i])
        if prob >= 0.5:
            obs.append({
                'p': prob,
                't': int(otypes[i]),
                'b': [ float(oboxs[i][1]), float(oboxs[i][0]), float(oboxs[i][3]), float(oboxs[i][2]) ]
            })

    return { 'objects': obs }

#

async def exec_detect(r: Request):
    content_type = None
    if 'content-type' in r.headers:
        content_type = r.headers['content-type'].lower()

    if content_type is not None:
        logger.info(f'POST: {content_type}')

    body = await r.body()

    loop : AbstractEventLoop = asyncio.get_running_loop()

    res = await loop.run_in_executor(the_executor, do_detect, body)

    return res

#
