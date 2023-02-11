from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from ..utils.mail_attachment import add_attachment
from io import StringIO

COL_TO_PRINT = ['group_name', 'host_label', 'host_ip', 'service_name', 'status_code']


class MailSender:
    def __init__(self, auth, sender_email, to_list, subject, attachments, **kwargs):
        self.auth = auth
        self.sender_email = sender_email
        self.to_list = to_list
        self.subject = subject
        self.cc_list = kwargs.get("cc_list")
        self.sender_label = kwargs.get("sender_label")
        self.attachments = attachments

    def _make_msg(self):
        message = MIMEMultipart()
        sender = self.sender_email
        if self.sender_label:
            sender = self.sender_label + "<{}>".format(self.sender_email)
        message["Subject"] = self.subject
        message["From"] = sender
        message["To"] = ", ".join(self.to_list)
        if self.cc_list:
            message["cc"] = ", ".join(self.cc_list)
        add_attachment(message, self.attachments)
        return message

    def sendmail(self):
        message = self._make_msg()
        try:
            with smtplib.SMTP(host=self.auth["server"], port=587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(user=self.auth["username"], password=self.auth["passwd"])
                smtp.sendmail(message["From"], message["To"], message.as_string())
            error = None
        except Exception as e:
            error = "\n#\tException error!\n{}\nCan not send mail to {}".format(e, message["To"])
        return error


class WTestMailSender(MailSender):
    def __init__(self, auth, wtest, to_string, subject, **kwargs):
        sender_email = auth["username"]
        attachments = self._make_attachments(wtest, to_string)
        super().__init__(auth, sender_email, self.to_list, subject, attachments, **kwargs)

    def _make_attachments(self, wtest, to_string):
        buffer = StringIO()
        emails_to = [val.split(",") for val in to_string.split(";")]
        if len(emails_to) == 1:
            emails_to.append(emails_to[0])
        if not wtest.errors.empty:
            errors = wtest.errors[COL_TO_PRINT]
            self.to_list = emails_to[0]
            begin = ""
            if wtest.findings:
                begin = "<h3>{}</h3><br>".format("<br>".join(wtest.findings.split("\n")))
            logs = ""
            if wtest.logs:
                logs = "<br><h3>Логи веб серверов:</h3><br>{}".format(wtest.logs.to_html())
            html = {"content": begin + errors.to_html() + logs, "type": "html"}
            wtest.errors.to_csv(buffer)
            csv = {"content": buffer, "type": "csv", "name": "test_result_errors.csv"}
            attachments = [html, csv]
        else:
            no_errors = wtest.no_errors[COL_TO_PRINT]
            self.to_list = emails_to[1]
            html = {"content": no_errors.to_html(), "type": "html"}
            wtest.no_errors.to_csv(buffer)
            csv = {"content": buffer, "type": "csv", "name": "test_result_no_errors.csv"}
            attachments = [html, csv]
        return attachments
