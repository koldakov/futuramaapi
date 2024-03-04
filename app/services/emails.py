from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr, HttpUrl

from app.core import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.email.host_user,
    MAIL_PASSWORD=settings.email.api_key,
    MAIL_FROM=settings.email.default_from,
    MAIL_PORT=settings.email.port,
    MAIL_SERVER=settings.email.host,
    MAIL_FROM_NAME=settings.email.from_name,
    MAIL_STARTTLS=settings.email.start_tls,
    MAIL_SSL_TLS=settings.email.ssl_tls,
    USE_CREDENTIALS=settings.email.use_credentials,
    VALIDATE_CERTS=settings.email.validate_certs,
    TEMPLATE_FOLDER=settings.project_root / "templates",
)


fast_mail = FastMail(conf)


class _User(BaseModel):
    name: str
    surname: str


class ConfirmationBody(BaseModel):
    url: HttpUrl
    user: _User


async def send_confirmation(
    emails: list[EmailStr],
    subject: str,
    template_body: ConfirmationBody,
    /,
):
    message = MessageSchema(
        subject=subject,
        recipients=emails,
        template_body=template_body.model_dump(),
        subtype=MessageType.html,
    )
    await fast_mail.send_message(
        message,
        template_name="emails/confirmation.html",
    )
