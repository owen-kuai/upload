"""该文件为道客DCS邮件连接及参数校验辅助工具"""
import re
import ssl
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr


EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$"
)


def check_smtp_conn(smtp_config):
    """测试右键是否可以连接"""
    smtp_ssl = smtp_config['smtp_ssl']
    smtp_server = smtp_config['smtp_server']
    smtp_port = smtp_config['smtp_port']
    smtp_email = smtp_config['smtp_email']
    smtp_password = smtp_config['smtp_password']

    if smtp_ssl:
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
            server.starttls()
        except ssl.SSLError:
            try:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=5)
            except Exception:
                raise Exception("Can't connect to smtp: {}".format(smtp_server))
        except Exception as error:
            # traceback.print_exc(e)
            raise Exception("Can't connect to smtp: {server}, {err}".format(
                server=smtp_server, err=str(error)))
    else:
        try:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
            server.starttls()
        except Exception:
            raise Exception("Can't connect to smtp: {}".format(smtp_server))
    try:
        server.login(smtp_email, smtp_password)
    except (smtplib.SMTPServerDisconnected, smtplib.SMTPHeloError,
            smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused,
            smtplib.SMTPDataError, smtplib.SMTPNotSupportedError,
            smtplib.SMTPException):
        raise Exception("Can't connect to smtp: {}".format(smtp_server))
    finally:
        server.close()
    return True


def send_email_test(send_to_email, config):
    """
    发送测试邮件
    :param send_to_email:
    :param config:
    :return:
    """
    if not verify_email_address(send_to_email):
        raise Exception('邮箱格式错误！')

    html_content = """
       <body><h1>Welcome aboard! </h1><p>这是一封来自 DaoCloud Services 管理台 SMTP 的测试邮件。
       </p><p>一切正常，准备启航。Have a nice day！</p></body>
       """
    msg = 'DaoCloud  Services  测试邮件'
    try:
        client = SMTPClient(config)
        client.send_content(send_to_email, msg, html_content)
    except Exception as error:
        raise Exception(str(error))
    return {'message': '测试邮件已发送至{}请注意查收！'.format(send_to_email)}


def verify_email_address(email_address):
    """检查邮箱格式是否符合"""
    if not EMAIL_PATTERN.match(email_address):
        return None

    return email_address


class SMTPClient(object):
    """邮件类"""
    def __init__(self, config):
        self.smtp_server = config["email_smtp_server"]
        self.smtp_email = config["email_smtp_email"]
        self.smtp_password = config["email_smtp_password"]
        self.smtp_port = config["email_smtp_port"]
        self.smtp_ssl = config["email_smtp_ssl"]
        self.from_email = config["email_from_email"] or self.smtp_email
        self.debug = True if config.get('debug') else False
        self.error_msg = ""

    def send_content(self, to_email, subject, content):
        """
        content 默认为 HTML
        attachment_urls 传入附件的 url 列表，下载完成之后再作为附件发送
                        之所以是 url 是因为通过 RESTful API 传文件不清真

        :param to_email:
        :param subject:
        :param content:
        :return:
        """
        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg['From'] = formataddr((Header("DaoCloud Services", 'utf-8').encode(), self.from_email))
        msg['To'] = formataddr((Header(to_email, 'utf-8').encode(), to_email))

        try:
            if not self.smtp_ssl:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=5)
        except smtplib.SMTPServerDisconnected:
            raise Exception("SMTP Disconnected, Check your STMP config.")
        except ssl.SSLError:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=5)
            server.starttls()

        server.debuglevel = 1 if self.debug else 0
        try:
            if self.smtp_password:
                server.login(self.smtp_email, self.smtp_password)
            res = server.sendmail(self.from_email, [to_email], msg.as_string())
            server.quit()
        except Exception as error:
            raise Exception(str(error))
        return res

    def return_ok(self):
        """滥竽充数"""
        return self.error_msg
