
#import os
from pathlib import Path
import data_insights as di

def run_data_exploration_pipeline(file_idx: int, csv_dataset_path: str):

    file_stem = Path(csv_dataset_path).stem
    report_folder = Path("eda_reports")  # location for storing all reports and plots.
    report_folder.mkdir(parents=True, exist_ok=True)
    pdf_report_filepath = report_folder / Path(f"{file_stem}_{file_idx}.pdf")  # pdf report that will summarize the insights.
    pdf_report_title = f" {file_stem}, {file_idx} DATA INSIGHTS"

    dsObj = di.DataInsights(
        path=csv_dataset_path,
        reportout_filepath=pdf_report_filepath, 
        pdf_report_title=pdf_report_title
        )

    dsObj.basic_info()
    dsObj.data_types_summary()
    dsObj.missing_values_analysis()
    dsObj.correlation_analysis()  # Good to perform AFTER eliminating missing values!! Otherwise, some correlations will be NaN and the analysis will fail.
    dsObj.numeric_summary()
    dsObj.numeric_distributions()  # Generates distribution plots (bar + kde) for each numeric column.
    dsObj.categorical_summary()

    # END OF COMMON DATA INSIGHTS ANALYSIS

    # START OF DATASET SPECIFIC INSIGHTS ANALYSIS
    # Based on the categorical_summary(), identify categories with too many unique values and (optionally) ignore them in the numerical_statistics_for_categorical_columns() analysis.
    # This is because when columns with too many unique cell values are used, this method will calculate meaningless statistics.
    dsObj.numerical_statistics_for_categorical_columns(ignored_columns = ['Date', 'Product ID'])

    # Sanitized time axis column name will be created and returned by the function.
    new_time_axis_column = dsObj.ts_time_axis_sanitization(time_axis_column = 'Date', original_timezone = 'Europe/Paris', save_folder=report_folder)  # Perform time axis driven sanitizations. Provide the time column name.

    # Next, let's segment the timestamps based on the unique values of a selected column.
    # The pdf report generated so far has "NUMERICAL STATISTICS FOR CATEGORICAL COLUMNS" section where column 'Control' has 3 unique values.
    # Based  on this value, some features are NaN. We also need to see how the timestamps are segmented based on "Control" values.

    column_of_interest = 'Control'  # Identified based on the pdf report generated so far.

    dsObj.ts_time_axis_segmentation(time_axis_column = new_time_axis_column, segment_column = column_of_interest, save_folder=report_folder)




    # WRAPPING UP AFTER FULL ANALYSIS
    dsObj.end_operation()  # finalize the pdf report and close all plots.


if __name__ == "__main__":

    datasets_folder = "C:\Cagri_Workspace\datasets\AI4I_PMDI"  # must have at least one csv dataset file in it

    # Create a list of file path strings that are csv files in the datasets folder
    list_of_datasets = [str(file) for file in Path(datasets_folder).glob("*.csv")]

    for file_idx, csv_dataset_path in enumerate(list_of_datasets):
        print(f"File {file_idx + 1} of {len(list_of_datasets)}: Processing: {csv_dataset_path}")
        run_data_exploration_pipeline(file_idx, csv_dataset_path)
