# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/
import pycodestyle
import os

ROOT_FOLDER = os.path.dirname(os.path.dirname(__file__))

paths = [
    os.path.join(ROOT_FOLDER, 'ameriflux_pipeline'),
    os.path.join(ROOT_FOLDER, 'tests/ameriflux_pipeline/'),
]


def test_conformance(paths=paths):
    """Test that pyIncore conforms to PEP-8."""
    style = pycodestyle.StyleGuide(quiet=False, max_line_length=120)
    result = style.check_files(paths)
    assert result.total_errors == 0


test_conformance()
