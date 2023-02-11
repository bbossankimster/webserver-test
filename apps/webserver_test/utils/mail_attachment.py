from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import io


def attach_scv(msg, csv_buffer, filename):
    attachment = MIMEBase('application', "octet-stream")
    attachment.set_payload(csv_buffer.getvalue())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
    msg.attach(attachment)


def add_attachment(message, attachments: list):
    REQUIRED_KEYS = ["type", "content"]
    for attchmnt in attachments:
        # type: plain, html, csv
        if set(attchmnt.keys()).intersection(set(REQUIRED_KEYS)) == set(REQUIRED_KEYS):
            if attchmnt["type"] == "text":
                message.attach(MIMEText(attchmnt["content"], 'plain'))
            if attchmnt["type"] == "html":
                message.attach(MIMEText(attchmnt["content"], attchmnt["type"]))
            if attchmnt["type"] == "csv":
                csv_data = attchmnt["content"]
                if type(csv_data) is not io.StringIO:
                    raise TypeError("EXCEPTION ERROR: invalid csv type {}".format(type(csv_data)))
                else:
                    attach_scv(message, attchmnt["content"], attchmnt.get("name", "noname.csv"))
        else:
            raise ValueError("EXCEPTION ERROR: wrong keys in attachment {}".format(attchmnt))
