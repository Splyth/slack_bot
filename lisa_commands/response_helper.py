"""
A wrapper to apply additional fun options to the response we send to slack 
(e.g. post with different name or icon image.)
"""

import datetime

def apply_additional_message_options(body):
    """
    Lisa likes to get gussied up for special occasions. So we replace her
    name and icon in the response that appears in slack.

    body - response body (dict)
    """

    now = datetime.date.today()

    # During the 15 Days leading up to Easter
    days_till_easter = (calc_easter(now.year) - now).days
    if days_till_easter >= 0 and days_till_easter < 15:
        body['username'] ='Lucky Rabbit Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Easter.png'
    # During March 3rd for Lisa's Birthday
    elif now.month == 3 and now.day == 3:
        body['username'] = "It's My Birthday! I'm " + str(now.year - datetime.date(2019,3,3).year) + ' Years Old Today! Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Party_Hat.png'
    # During Aug 8th for Animunity's Birthday
    elif now.month == 8 and now.day == 8:
        body['username'] = "Celebrating " + str(now.year - datetime.date(2018,8,8).year) + ' Years of Animunity! Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Party_Hat.png'
    # During October for Halloween
    elif now.month == 10:
        body['username'] ='Witchy Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Easter.png'
    # During December for Christmas
    elif now.month == 12:
        body['username'] ='Santa Lisa'
        body["icon_url"] = 'https://raw.githubusercontent.com/Splyth/slack_bot/master/icons/Lisa_Christmas.png'

    return body

def calc_easter(year):
    """
    Returns Easter as a date object. Because Easter is a floating mess
    
    year - the year to calc easter for
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1    
    return datetime.date(year, month, day)
