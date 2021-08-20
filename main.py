# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import argparse

from preprocessing import Preprocessor

def preprocessing(input_data, output_data):
    """
    Function to call preprocessing class
    :param data_path: input data path
    :return: processed dataframe
    """
    preprocessor = Preprocessor(input_data)
    df = preprocessor.read_data()
    df = preprocessor.data_preprocess(df)
    preprocessor.write_data(df, output_data )

    return df

def main():
    """
    Main function to run. Calls other functions
    :return: None
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", action="store", default=os.path.join(os.getcwd(), "data", "FLUXSB_EC1week.csv"),
                        help="dataset path")
    parser.add_argument("--output", action="store", default=os.path.join(os.getcwd(), "FLUXSB_EC1week_output.csv"),
                        help="dataset path")

    df = preprocessing(args.input, args.output)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
