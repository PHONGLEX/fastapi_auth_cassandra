from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from helpers.config import config


conf = ConnectionConfig(
    MAIL_USERNAME = config['EMAIL'],
    MAIL_PASSWORD = config['PASSWORD'],
    MAIL_FROM = config['EMAIL'],
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


async def send_mail(data):
    msg = MessageSchema(
        subject=data.get('subject'),
        body=data.get('body'),
        recipients=data.get('to')
    )
    fm = FastMail(conf)
    await fm.send_message(msg)