from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText


def attach_scv(msg, csv_buffer, filename):
    attachment = MIMEBase('application', "octet-stream")
    attachment.set_payload(csv_buffer.getvalue())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
    msg.attach(attachment)


def add_attachment(message, attachments):
    for attchmnt in attachments:
        # type: plain, html, csv
        if attchmnt["type"] == "text":
            message.attach(MIMEText(attchmnt["content"], 'plain'))
        if attchmnt["type"] == "html":
            part = MIMEText(attchmnt["content"], attchmnt["type"])
            message.attach(part)
        if attchmnt["type"] == "csv":
            attach_scv(message, attchmnt["content"], attchmnt["name"])
