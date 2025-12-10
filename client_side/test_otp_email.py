"""
Standalone script to send a test email via AWS SES.
Use this to verify your SES credentials and email sending setup.
"""

import boto3
from botocore.exceptions import ClientError
import logging
from decouple import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

AWS_REGION = config("AWS_REGION", default="ca-central-1")
SENDER_EMAIL = config("AWS_SES_FROM_EMAIL")
RECIPIENT_EMAIL = config("TEST_EMAIL", default="kushalsharmacse@gmail.com")

SUBJECT = "🔐 TaxEase Test Email via AWS SES"
BODY_TEXT = ("This is a test email sent using AWS SES.\n"
             "If you're reading this, SES is working correctly!")

BODY_HTML = f"""
<html>
  <body>
    <h2>TaxEase – AWS SES Email Test</h2>
    <p>This is a test email sent from your backend.</p>
    <p><strong>If you received this, SES is configured correctly!</strong></p>
  </body>
</html>
"""

CHARSET = "UTF-8"


def send_test_email():
    """Send a test email using AWS SES."""
    logging.info("🚀 Starting SES email test...")
    logging.info(f"📧 Sender: {SENDER_EMAIL}")
    logging.info(f"📨 Recipient: {RECIPIENT_EMAIL}")
    logging.info(f"🌎 Region: {AWS_REGION}")

    # Create SES client
    client = boto3.client(
        "ses",
        region_name=AWS_REGION,
        aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY")
    )

    try:
        response = client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                "ToAddresses": [RECIPIENT_EMAIL],
            },
            Message={
                "Subject": {"Data": SUBJECT, "Charset": CHARSET},
                "Body": {
                    "Text": {"Data": BODY_TEXT, "Charset": CHARSET},
                    "Html": {"Data": BODY_HTML, "Charset": CHARSET},
                },
            },
        )

        logging.info("✅ Email sent successfully!")
        logging.info(f"📨 Message ID: {response['MessageId']}")
        logging.info("📬 Check inbox (and spam folder).")

    except ClientError as e:
        logging.error("❌ Error sending email via SES")
        logging.error(e.response["Error"]["Message"])
        logging.error("")
        logging.error("⚠️ Check the following:")
        logging.error(" - SES domain/email is verified")
        logging.error(" - SES account is out of sandbox OR recipient is verified")
        logging.error(" - AWS credentials are correct")
        return False

    return True


if __name__ == "__main__":
    success = send_test_email()
    if success:
        logging.info("🎉 SES Test Complete – All Good!")
    else:
        logging.error("❌ SES Test Failed.")
