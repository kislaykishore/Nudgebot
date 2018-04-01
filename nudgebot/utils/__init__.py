import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
import logging


def send_email(from_address, receivers, subject, body, attachments=None, text_format='plain', logger=None):
    """Sending an email from <from_address> to the <receivers> with the provided <subject> and <body>
        @param from_address: `str` The address from which the email is being sent.
        @param receivers: (`list` of `str`) A list of the email addresses of the receivers.
        @param subject: `str` The subject of the email.
        @param body: `str` The body of the email.
        @keyword attachments: (`list` of `str`) A list of paths to files to be attached.
        @keyword text_format: `str` The email text format, could be either 'plain' or 'html'
        @keyword logger: `logging.Logger` The logger to use.
    """
    # Validate params:
    assert isinstance(from_address, str)
    assert isinstance(receivers, (list, tuple))
    assert isinstance(subject, str)
    assert isinstance(body, str)
    assert isinstance(attachments, (type(None), list, tuple))
    if attachments:
        for attach in attachments:
            assert isinstance(attach, str), 'All attachments should be strings'
            assert os.path.exists(attach), 'No such file: "{}"'.format(attach)
    assert isinstance(text_format, str)
    text_format = text_format.lower()  # Insensitive
    assert text_format in ('plain', 'html')
    assert isinstance(logger, (logging.Logger, type(None)))
    # -
    logger = logger or logging
    logger.info('Sending Email from {} to {}; subject="{}"'.format(from_address, receivers, subject))

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = COMMASPACE.join(receivers)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, text_format))
    if attachments:
        for attachment in attachments:
            with open(attachment, "rb") as attachment_file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= {}"
                                .format(attachment))
                msg.attach(part)

    smtp_server = smtplib.SMTP('localhost')  # TODO: parameterize
    smtp_server.sendmail(from_address, receivers, msg.as_string())


def from_camel(string: str) -> str:
    """Converting a CamelCase string to non_camel_case"""
    assert isinstance(string, str), 'string must be a type of `str`'
    out = ''
    for i, c in enumerate(string):
        addition = c.lower()
        if c.isupper():
            if i != 0:
                addition = '_' + addition
        out += addition
    return out


def underscored(string):
    """Convert string from 'string with whitespaces' to 'string_with_whitespaces'"""
    assert isinstance(string, str)
    return string.replace(' ', '_')


def collect_subclasses(mod, cls, exclude=None):
    """Collecting all subclasses of `cls` in the module `mod`

    @param mod: `ModuleType` The module to collect from.
    @param cls: `type` or (`list` of `type`) The parent class(es).
    @keyword exclude: (`list` of `type`) Classes to not include.
    """
    out = []
    for name in dir(mod):
        attr = getattr(mod, name)
        if (
                isinstance(attr, type) and
                (attr not in cls if isinstance(cls, (list, tuple)) else attr != cls) and
                issubclass(attr, cls) and
                (attr not in exclude if exclude else True)):
            out.append(attr)
    return out
