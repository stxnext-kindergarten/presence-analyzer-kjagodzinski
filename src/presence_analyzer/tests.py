# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import os.path
import json
import datetime
import unittest

from time import time as tm

from presence_analyzer import main, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_user.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update(
            {
                'DATA_CSV': TEST_DATA_CSV,
                'DATA_XML': TEST_DATA_XML
            }
        )
        self.client = main.app.test_client()
        utils.CACHE = {}

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('/presence_weekday.html')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(
            data,
            sorted(data, key=lambda sort_by: sort_by['name'])
        )
        self.assertDictEqual(
            data[0],
            {
                'user_id': 141,
                'name': 'Adam P.',
                'avatar': 'https://host:443/api/images/users/141'
            }
        )

    def test_month_dropdown(self):
        """
        Test months listing.
        """
        resp = self.client.get('/api/v1/months')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(
            data,
            [
                {'name': 'January', 'month': 1},
                {'name': 'February', 'month': 2},
                {'name': 'March', 'month': 3},
                {'name': 'April', 'month': 4},
                {'name': 'May', 'month': 5},
                {'name': 'June', 'month': 6},
                {'name': 'July', 'month': 7},
                {'name': 'August', 'month': 8},
                {'name': 'September', 'month': 9},
                {'name': 'October', 'month': 10},
                {'name': 'November', 'month': 11},
                {'name': 'December', 'month': 12}
            ]
        )

    def test_api_mean_time(self):
        """
        Test api mean time weekday view for existing user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Mon', 0],
                ['Tue', 30047.0],
                ['Wed', 24465.0],
                ['Thu', 23705.0],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

    def test_template_for_url(self):
        """
        Test correct rendering template for url.
        """
        resp = self.client.get('/presence_weekday.html')
        self.assertEqual(resp.status_code, 200)

    def test_template_for_url_404(self):
        """
        Test rendering template for unexisting url.
        """
        resp = self.client.get('/xyz')
        self.assertEqual(resp.status_code, 404)

    def test_api_mean_time_404(self):
        """
        Test api mean time weekday view for unexisting user.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/1')
        self.assertEqual(resp.status_code, 404)

    def test_api_presence_weekday(self):
        """
        Test api presence weekday view for existing user.
        """
        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(
            data,
            [
                ['Weekday', 'Presence (s)'],
                ['Mon', 0],
                ['Tue', 30047.0],
                ['Wed', 24465.0],
                ['Thu', 23705.0],
                ['Fri', 0],
                ['Sat', 0],
                ['Sun', 0],
            ]
        )

    def test_api_presence_weekday_404(self):
        """
        Test api presence weekday view unexisting user.
        """
        resp = self.client.get('/api/v1/presence_weekday/1')
        self.assertEqual(resp.status_code, 404)

    def test_presence_start_end_view(self):
        """
        Test api presence start end view for existing user.
        """
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertListEqual(
            data,
            [
                ['Mon', {'start': 0, 'end': 0}],
                ['Tue', {'start': 34745.0, 'end': 64792.0}],
                ['Wed', {'start': 33592.0, 'end': 58057.0}],
                ['Thu', {'start': 38926.0, 'end': 62631.0}],
                ['Fri', {'start': 0, 'end': 0}],
                ['Sat', {'start': 0, 'end': 0}],
                ['Sun', {'start': 0, 'end': 0}]
            ]
        )

    def test_presence_startend_view_404(self):
        """
        Test api presence start end view for unexisting user.
        """
        resp = self.client.get('/api/v1/presence_start_end/1')
        self.assertEqual(resp.status_code, 404)

    def test_user_image_view(self):
        """
        Test api returning user's image for existing user.
        """
        resp = self.client.get('/api/v1/user_image/170')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data, 'https://host:443/api/images/users/170')

    def test_user_image_view_404(self):
        """
        Test api returning user's image for unexisting user.
        """
        resp = self.client.get('/api/v1/user_image/999')
        self.assertEqual(resp.status_code, 404)

    def test_presence_top_5_users_monthly_view(self):
        # pylint: disable=invalid-name
        """
        Test api returning top 5 users for month depend on mean monthly time.
        """
        resp = self.client.get('/api/v1/top5monthly/September')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]['mean'], 26072.333333333332)
        self.assertGreaterEqual(data[0]['mean'], data[1]['mean'])
        self.assertGreaterEqual(data[1]['mean'], data[2]['mean'])
        self.assertGreaterEqual(data[2]['mean'], data[3]['mean'])
        self.assertGreaterEqual(data[3]['mean'], data[4]['mean'])

    def test_presence_top_5_users_monthly_view_404(self):
        # pylint: disable=invalid-name
        """
        Test api returning 404 error for unexisting month.
        """
        resp = self.client.get('/api/v1/month/14')
        self.assertEqual(resp.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update(
            {
                'DATA_CSV': TEST_DATA_CSV,
                'DATA_XML': TEST_DATA_XML
            }
        )

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_get_data_xml(self):
        """
        Test parsing of XML file.
        """
        data = utils.get_data_xml()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11, 176, 170, 26, 141])
        self.assertItemsEqual(data[26].keys(), ['avatar', 'name'])
        self.assertTrue(data[26]['avatar'].startswith('https://host:443/'))
        self.assertEqual(data[176]['name'], 'Adrian K.')

    def test_memoize(self):
        """
        Test memorize data and updating if expired.
        """
        utils.get_data()
        self.assertIn('get_data', utils.CACHE)
        self.assertIn('value', utils.CACHE['get_data'])
        self.assertIn('time', utils.CACHE['get_data'])
        utils.CACHE['get_data']['time'] = 0
        utils.get_data()
        self.assertNotEqual(utils.CACHE['get_data']['time'], 0)
        utils.get_data_xml()
        self.assertEqual(len(utils.CACHE), 2)
        self.assertIn('get_data_xml', utils.CACHE)
        future_time = tm() + 100
        utils.CACHE['get_data'] = {'time': future_time, 'value': 'test'}
        utils.get_data()
        self.assertEqual(utils.CACHE['get_data']['value'], 'test')

    def test_group_by_weekday(self):
        """
        Groups entries by weekday.
        """
        sample_data = utils.get_data()
        result = utils.group_by_weekday(sample_data[10])
        self.assertListEqual(
            result,
            [[], [30047], [24465], [23705], [], [], []]
        )

    def test_seconds_since_midnight(self):
        """
        Test calculating amount of seconds since midnight.
        """
        time = datetime.time(1, 2, 3)
        self.assertEqual(utils.seconds_since_midnight(time), 3723)
        time = datetime.time(0, 0, 0)
        self.assertEqual(utils.seconds_since_midnight(time), 0)
        time = datetime.time(0, 0, 1)
        self.assertEqual(utils.seconds_since_midnight(time), 1)
        time = datetime.time(0, 2, 0)
        self.assertEqual(utils.seconds_since_midnight(time), 120)
        time = datetime.time(3, 0, 0)
        self.assertEqual(utils.seconds_since_midnight(time), 10800)

    def test_intervals(self):
        """
        Test calculating intervals between two datetime.time obj.
        """
        time = datetime.time(0, 0, 3)
        time2 = datetime.time(1, 2, 3)
        self.assertEqual(utils.interval(time, time2), 3720)
        self.assertEqual(utils.interval(time2, time), -3720)
        self.assertEqual(utils.interval(time2, time2), 0)
        self.assertGreaterEqual(time2, time)

    def test_mean_time(self):
        """
        Test calculating arithmetic mean.
        """
        items = [1, 2, 3]
        self.assertEqual(utils.mean(items), 2.0)
        items = [-1, -2, -3]
        self.assertEqual(utils.mean(items), -2.0)
        items = []
        self.assertEqual(utils.mean(items), 0)

    def test_mean_time_of_presence(self):
        """
        Test calculating mean entries for every weekday.
        """
        sample_data = utils.get_data()
        result = utils.mean_time_of_presence(sample_data[10])
        self.assertDictEqual(
            result,
            {
                0: {'start': 0, 'end': 0},
                1: {'start': 34745.0, 'end': 64792.0},
                2: {'start': 33592.0, 'end': 58057.0},
                3: {'start': 38926.0, 'end': 62631.0},
                4: {'start': 0, 'end': 0},
                5: {'start': 0, 'end': 0},
                6: {'start': 0, 'end': 0}
            }
        )

    def test_mean_by_month(self):
        """
        Test grouping mean time at work by month.
        """
        data = utils.get_data()
        sample_data_user = data[10]
        result = utils.mean_by_month(sample_data_user)
        self.assertListEqual(
            result,
            [
                0, 0, 0, 0,
                0, 0, 0, 0,
                26072.333333333332, 0, 0, 0
            ]
        )


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
