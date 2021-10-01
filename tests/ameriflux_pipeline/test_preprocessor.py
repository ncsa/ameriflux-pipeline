# Copyright (c) 2021 University of Illinois and others. All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License v2.0 which accompanies this distribution,
# and is available at https://www.mozilla.org/en-US/MPL/2.0/

import os

from ameriflux_pipeline.preprocessor import Preprocessor


def test_preprocessor():
    print(os.getcwd())
    input = "../data/FLUXSB_EC_Jul_week1.csv"
    output = "../data/output.csv"
    metadata = "../data/FLUXSB_EC.dat.meta.csv"

    df = Preprocessor.data_preprocess(input, output, 96, metadata)

    assert 'Ah_fromRH' in df


if __name__ == "__main__":
    test_preprocessor()
