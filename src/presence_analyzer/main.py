# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
import re

from flask import Flask

app = Flask(__name__)  # pylint: disable=invalid-name


@app.template_filter('quoted')
def quoted(strpath):
    """
    Filter which get string from quotes e.g, {{ self | quotes }}.
    """
    find_expression = re.findall('\'([^\']*)\'', str(strpath))
    if find_expression:
        return find_expression[0]
    return None
