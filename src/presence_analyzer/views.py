# -*- coding: utf-8 -*-
"""
Defines views.
"""
import calendar
import logging

from flask import abort, make_response, redirect
from flask.ext.mako import render_template  # pylint: disable=import-error
from mako.exceptions import TopLevelLookupException

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify, get_data, mean, group_by_weekday, mean_time_of_presence,
    get_data_xml, mean_by_month
)


log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.route('/<string:template_file>', methods=['GET'])
def template_for_url(template_file):
    """
    Render templates for url.
    """
    if not template_file.endswith('.html'):
        template_file = '{}.html'.format(template_file)

    try:
        return render_template(template_file, template_file=template_file)
    except TopLevelLookupException:
        return make_response('page not found', 404)


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data_xml = get_data_xml()
    return [
        {
            'user_id': user_id,
            'name': data_xml[user_id]['name'],
            'avatar': data_xml[user_id]['avatar']
        } for user_id in data_xml]


@app.route('/api/v1/months', methods=['GET'])
@jsonify
def months_view():
    """
    Months listing for dropdown.
    """
    return [
        {
            'month': month,
            'name': calendar.month_name[month]
        } for month in range(1, 13)
    ]


@app.route('/api/v1/top5monthly/<month>', methods=['GET'])
@jsonify
def presence_top_5_users_monthly_view(month):  # pylint: disable=invalid-name
    """
    Return 5 users from top of mean presence by month.
    """
    months = calendar.month_name[1:]
    if month not in months:
        abort(404)
    data_xml = get_data_xml()
    data = get_data()
    result = []
    for user_id in data_xml:
        result.append(
            {
                'avatar': data_xml[user_id]['avatar'],
                'user_id': user_id,
                'name': data_xml[user_id]['name'],
                'mean': mean_by_month(
                    data.get(user_id, [])
                    )[months.index(month)],
            }
        )
    return sorted(
        result,
        key=lambda sort_by: sort_by['mean'],
        reverse=True
    )[:5]


@app.route('/api/v1/user_image/<int:user_id>', methods=['GET'])
@jsonify
def user_image_view(user_id):
    """
    Return avatar value for selected user.
    """
    data_xml = get_data_xml()
    if user_id not in data_xml:
        log.debug('User %s not found!', user_id)
        abort(404)

    return data_xml[user_id]['avatar']


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()

    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean time of presence.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    mean_times = mean_time_of_presence(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean_times[value])
        for weekday, value in enumerate(mean_times)
    ]
    return result
