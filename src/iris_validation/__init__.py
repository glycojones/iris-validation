import os
import sys
import json

from iris_validation.graphics import Panel
from iris_validation.metrics import metrics_model_series_from_files

PYTEST_RUN = 'pytest' in sys.modules

def generate_report(
    latest_model_path,
    latest_reflections_path=None,
    latest_sequence_path=None,
    latest_distpred_path=None,
    previous_model_path=None,
    previous_reflections_path=None,
    previous_sequence_path=None,
    previous_distpred_path=None,
    run_covariance=False,
    run_molprobity=False,
    calculate_rama_z=True,
    multiprocessing=True,
    latest_model_metrics_json=None,
    previous_model_metrics_json=None,
    data_with_percentiles=None,  # only works with model_metrics_json files
    discrete_metrics_to_display=None,
    continuous_metrics_to_display=None,
    residue_bars_to_display=None,
    percentile_bar_label=None,
    percentile_bar_range=None,
    wrap_in_html=True,
    output_dir=None,
    output_name_prefix="report",
    custom_labels={'Latest':'Latest', 'Previous':'Previous'}
):

    # sanitise output file name
    output_name_prefix = output_name_prefix.replace('/','_').replace('.','_')

    model_series = metrics_model_series_from_files((previous_model_path, latest_model_path),
                                                   (previous_reflections_path, latest_reflections_path),
                                                   (previous_sequence_path, latest_sequence_path),
                                                   (previous_distpred_path, latest_distpred_path),
                                                   (previous_model_metrics_json, latest_model_metrics_json),
                                                   run_covariance,
                                                   run_molprobity,
                                                   calculate_rama_z,
                                                   data_with_percentiles,
                                                   multiprocessing)
    
    model_series_data = model_series.get_raw_data()
    
    if PYTEST_RUN : 
        with open(os.path.join(output_dir, output_name_prefix + ".json"), 'w', encoding='utf8') as json_output :
            json.dump(model_series_data, json_output, indent=2)

    panel = Panel(
        model_series_data,
        continuous_metrics_to_display=continuous_metrics_to_display,
        discrete_metrics_to_display=discrete_metrics_to_display,
        residue_bars_to_display=residue_bars_to_display,
        percentile_bar_label=percentile_bar_label,
        percentile_bar_range=percentile_bar_range,
        custom_labels=custom_labels
    )
    panel_string = panel.dwg.tostring()

    if wrap_in_html:
        panel_string = f'<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="utf-8">\n\t\t<title>Iris Report</title>\n\t</head>\n\t<body>\n\t\t{panel_string}\n\t</body>\n</html>'

    if output_dir is None:
        return panel_string

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    extension = 'html' if wrap_in_html else 'svg'
    with open(os.path.join(output_dir, f"{output_name_prefix}.{extension}"), 'w', encoding='utf8') as outfile:
        outfile.write(panel_string)
