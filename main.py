import os
import logging

import uvicorn

from det_server.main import init

PORT = os.getenv('PORT', '8080')

logger = logging.getLogger(__name__)

logger.info(f'Startup... PORT={PORT}')

def run():
    init('./lite3')
    logger.info('uvicorn.run() : Start...')
    uvicorn.run('det_server.main:app', host = '0.0.0.0', port = int(PORT), log_level = 'debug')
    logger.info('uvicorn.run() : DONE.')

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s- %(name)s - %(levelname)s - %(message)s')
    run()
