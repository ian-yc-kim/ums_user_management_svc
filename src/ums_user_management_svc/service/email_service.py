import logging


def send_verification_email(email: str) -> None:
    """Send a verification email to the specified email address."""
    try:
        # Implement email sending logic here
        logging.info(f"Sending verification email to {email}")
    except Exception as e:
        logging.error(e, exc_info=True)
