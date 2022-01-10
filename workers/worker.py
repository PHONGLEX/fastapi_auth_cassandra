import asyncio
from celery import Celery
from celery.utils.log import get_task_logger

from helpers.config import config
from helpers.email_helper import send_mail

celery = Celery(__name__)
celery.conf.broker_url = config['CELERY_BROKER_URL']

logger = get_task_logger(__name__)

@celery.task(name="send_email_task")
def send_email_task(data):
    logger.info("send email task is being executed")
    asyncio.get_event_loop().run_until_complete(send_mail(data))