"""Week 3: send alert messages. Tokens and passwords come from settings (env vars), never from code."""


def format_job_message(job, alert_name: str) -> str:
    """Return a short text, e.g.:
        New match for "Python backend": Backend Engineer Intern at Acme (Remote)
        https://...
    """
    raise NotImplementedError("TODO Week 3: format_job_message")


def send_telegram(chat_id: str, text: str) -> None:
    """POST https://api.telegram.org/bot<TOKEN>/sendMessage with chat_id and text (timeout=10).

    If settings.TELEGRAM_BOT_TOKEN is empty, only log the message (good for local testing).
    Never log the token itself.
    """
    raise NotImplementedError("TODO Week 3: send_telegram")


def send_email(to: str, subject: str, body: str) -> None:
    """Use django.core.mail.send_mail (it reads EMAIL_* from settings).

    If settings.EMAIL_HOST is empty, only log the message.
    """
    raise NotImplementedError("TODO Week 3: send_email")
