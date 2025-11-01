import pandas as pd


def get_source_mapping_data(filename):
    try:
        # specify columns
        columns = [
            "source_query_select",
            "table_id",
            "execution_order",
            "is_app_table"
        ]
        # read csv file into dataframe
        df = pd.read_csv(filename, usecols=columns)
        # filter data
        filtered_df = df[df["is_app_table"] == 1]
        # sort data
        data = filtered_df.sort_values(by=[
            "execution_order",
            "source_query_select"
        ])
        return data
    except FileNotFoundError as e:
        print(e)
    except Exception as e:  # pylint disable=broad-except
        print(e)


def get_destination_mapping_data(filename):
    try:
        # specify columns
        columns = [
            "destination_query_create",
            "destination_query_insert",
            "table_id",
            "execution_order",
            "is_app_table",
        ]
        # read csv file into dataframe
        df = pd.read_csv(filename, usecols=columns)
        # filter data
        filtered_df = df[df["is_app_table"] == 1]
        # sort data
        data = filtered_df.sort_values(
            by=["execution_order", "destination_query_insert"]
        )
        return data
    except FileNotFoundError as e:
        print(e)
    except Exception as e:  # pylint disable=broad-except
        print(e)


def write_mapping_data(data, output_filename):
    try:
        # write mapping data to output filename
        data.to_json(output_filename, orient="records")
    except Exception as e:  # pylint disable=broad-except
        print(e)
