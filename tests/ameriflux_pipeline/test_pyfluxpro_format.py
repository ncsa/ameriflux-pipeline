import os
from ameriflux_pipeline.pyfluxpro_format import PyFluxProFormat


def test_pyfluxpro_format():
    print(os.getcwd())
    eddypro_full_output = "../data/eddypro_Sorghum_Jan1to7_2021_full_output_2021-11-03T083200_adv.csv"
    df = PyFluxProFormat.data_formatting(eddypro_full_output)

    assert 'sonic_temperature_C' in df


if __name__ == "__main__":
    test_pyfluxpro_format()
