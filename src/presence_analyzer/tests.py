# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import os.path
import json
import datetime
import unittest

from presence_analyzer import main, views, utils


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv')


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        self.client = main.app.test_client()

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
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {'user_id': 10, 'name': 'User 10'})

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

    def test_presence_start_end_view_404(self):
        """
        Test api presence start end view for unexisting user.
        """
        resp = self.client.get('/api/v1/presence_start_end/1')
        self.assertEqual(resp.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

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
