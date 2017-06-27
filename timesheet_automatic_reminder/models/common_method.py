# -*- coding: utf-8 -*-
# © 2015-2017 Elico corp (http://www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import datetime, timedelta, date
import pytz

# from openerp import models, api

DATETIME = '%Y-%m-%d %H:%M:%S'
DATE = '%Y-%m-%d'
TIME = '%H:%M:%S'


def is_weekend(selected_date):
    """
    The function is used judge the weekend date,
    if is weekend return True else return False
    :param selected_date: the date need judged date,
    just support string date format '%Y-%m-%d %H:%M:%S' or datetime type
    :return: True or False
    """
    if not isinstance(selected_date, (datetime, date)):
        selected_date = datetime.strptime(selected_date, DATETIME)

    return True if selected_date.weekday() in [5, 6] else False


def str_to_datetime(date_str, tz_info=None, new_tz=None):
    """
    Translation string date into datetime date
    :param date_str:
    :param tz_info:
    :param new_tz:
    :return:
    """
    if new_tz and isinstance(new_tz, str):
        new_tz = pytz.timezone(new_tz)

    res = datetime.strptime(
        time.strftime(date_str),
        DATETIME
    )
    if tz_info:
        res = res.replace(tzinfo=tz_info)
    if new_tz:
        res = res.replace(
            tzinfo=pytz.utc
        ).astimezone(new_tz)

    return res


def tz_offset_today(employee_tz_str):
    """
    Get Today's Date format data
    :param employee_tz_str: The employee's timezone
    :return:
    """
    employee_tz = pytz.timezone(employee_tz_str)
    utc_date = datetime.today().replace(tzinfo=pytz.utc)
    return utc_date.astimezone(employee_tz).date()
