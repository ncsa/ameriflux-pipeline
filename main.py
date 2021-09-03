# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import argparse

from preprocessing import Preprocessor

def preprocessing(input_path, output_path, missing_time_threshold):
    """
    Function to call preprocessing class
    :param data_path: input data path
    :return: processed dataframe
    """
    preprocessor = Preprocessor(input_path, output_path, missing_time_threshold)
    df = preprocessor.read_data()
    print("Data contains ",df.shape[0], "rows ", df.shape[1], "columns")
    df = preprocessor.data_preprocess()

    return df

def write_data(df, output_data):
    """
    Write the dataframe to csv file
    :param df: input dataframe to be written to csv file
           output_data : filename to write data
    :return: None
    """
    df.to_csv(output_data, index=False)
    pass


def main():
    """
    Main function to run. Calls other functions
    :return: None
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", action="store", default=os.path.join(os.getcwd(), "data", "FLUXSB_EC_Jul_week1.csv"),
                        help="input data path")
    parser.add_argument("--output", action="store", default=os.path.join(os.getcwd(), "FLUXSB_EC_Jul_week1_output.csv"),
                        help="output data path")
    parser.add_argument("--missingTime", action="store", default=96,
                        help = "Number of 30min timeslot threshold to ask for user confirmation")
    # parse arguments

    args = parser.parse_args()

    # start preprocessing data
    df = preprocessing(args.input, args.output, args.missingTime)
    # write processed df to output path
    write_data(df, args.output)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
