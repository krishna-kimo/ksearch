import logging
from functools import wraps
import os
import sys
import json


# decorator for logging Scrapy responses
def log_response(title, with_meta=False):
    def real_decorator(f):
        @wraps(f)
        def wrap(self, response):
            if not with_meta:
                self.logger.info('Opened {title} page (url: "{url}")'.format(url=response.url, title=title))
            else:
                meta = response.meta.copy()
                for a in ('download_timeout', 'download_slot', 'download_latency', 'redirect_urls'):
                    meta.pop(a, None)
                self.logger.info(
                    'Opened {title} page (url: "{url}", meta: {meta})'.format(url=response.url, meta=meta, title=title)
                )
            return f(self, response)
        return wrap
    return real_decorator


# logging methods and their arguments for scrapy spiders
def log_method(f):
    @wraps(f)
    def wrap(self, *args, **kwargs):
        logging_message = 'Call function {}.'.format(f.__name__.upper())
        if args: logging_message += ' Args: {}.'.format(', '.join(str(a) for a in args))
        if kwargs: logging_message += ' Kwargs: {}.'.format(kwargs)
        self.logger.info('')
        self.logger.info(logging_message)
        return f(self, *args, **kwargs)
    return wrap


# remove repeatable spaces and blank lines ("a   b c " -> "a b c")
def remove_spaces(s):
    return ' '.join(s.split()).strip()


# decorator for saving Scrapy response.text
def save_response(title, data_type='html'):
    def real_decorator(f):
        @wraps(f)
        def wrap(self, response):
            from scrapy_app.settings import PROJECT_DIR
            html_dir = os.path.join(PROJECT_DIR, 'etc', 'html', self.name)
            if not os.path.exists(html_dir):
                os.makedirs(html_dir)

            if data_type == 'json':
                file_name = title + '.json'
                try:
                    file_content = json.dumps(json.loads(response.text), indent=2, ensure_ascii=False)
                except Exception:
                    self.logger.warning('Content if not json!')
                    file_content = response.text
            else:
                file_name = title + '.html'
                file_content = response.text

            file_path = os.path.join(html_dir, file_name)
            with open(file_path, mode='w', encoding='utf-8') as fp:
                fp.write(file_content)
            self.logger.info('Saved response to {name}'.format(name=file_path))
            return f(self, response)
        return wrap
    return real_decorator


# configure logging to file
def configure_file_logging(file_name, log_dir, mode='w', level=logging.DEBUG):
    import os
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_logger = logging.FileHandler(filename=os.path.join(log_dir, file_name), mode=mode, encoding='utf-8')
    file_logger.setLevel(level)
    file_logger.setFormatter(formatter)
    logging.getLogger().addHandler(file_logger)


# send email using gmail account
def send_email(subject, body, email=''):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from scrapy_app.settings import BOT_EMAIL, BOT_PASSWORD, EMAIL_TO
    email_to_list = [email] if email else EMAIL_TO

    msgRoot = MIMEMultipart()
    msgRoot['From'] = BOT_EMAIL
    msgRoot['To'] = ', '.join(email_to_list)
    msgRoot['Subject'] = subject
    msgRoot.attach(MIMEText(body, 'plain'))  # html
    logging_details = 'Subject: {}. From: {} to: {}'.format(subject, BOT_EMAIL, ', '.join(email_to_list))
    try:
        server = smtplib.SMTP(host='smtp.gmail.com', port=587)
        server.ehlo()
        server.starttls()
        server.login(BOT_EMAIL, BOT_PASSWORD)
        server.sendmail(BOT_PASSWORD, email_to_list, msgRoot.as_string())
        server.close()
        logging.info('Email was sent successfully. ' + logging_details)
    except Exception as e:
        logging.info('Error sending email. ' + logging_details)
        print('Error sending email. ' + logging_details)
        print(e)


# JSON serializer for objects not serializable by default json code
def json_serial(obj):
    from datetime import date, datetime
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Set necessary environment settings - for Django and Scrapy settings modules and run django.setup()
# This function should be called before any import of Django models (used in crawler, email service, etc)
def configure_django():
    import django
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dir "scrapy_app"
    project_dir = os.path.dirname(app_dir)                                 # dir "sohb2bcrawlers"
    sys.path.extend([app_dir, project_dir])                                # add dirs to PATH
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_app.settings'           # set path to scrapy settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'db_app.settings'               # set path to django settings
    django.setup()
