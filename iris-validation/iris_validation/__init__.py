import os
import subprocess
import json

from iris_validation.graphics import Panel
from iris_validation.metrics import metrics_model_series_from_files


def generate_report(latest_model_path,
                    latest_reflections_path=None,
                    latest_sequence_path=None,
                    latest_distpred_path=None,
                    previous_model_path=None,
                    previous_reflections_path=None,
                    previous_sequence_path=None,
                    previous_distpred_path=None,
                    run_covariance=False,
                    run_molprobity=False,
                    multiprocessing=True,
                    wrap_in_html=True,
                    output_dir=None,
                    use_tortoize=True):
    model_paths = (previous_model_path, latest_model_path)
    reflections_paths = (previous_reflections_path, latest_reflections_path)
    sequence_paths = (previous_sequence_path, latest_sequence_path)
    distpred_paths = (previous_distpred_path, latest_distpred_path)

    tortoize_results = []
    if use_tortoize:
        valid_model_paths = [model_path for model_path in model_paths if model_path]
        valid_model_paths = [latest_model_path]
        for model_path in valid_model_paths:
            tortoize_process = subprocess.Popen(
                f'tortoize {model_path}',
                shell=True,
                stdout=subprocess.PIPE)
            tortoize_output = tortoize_process.communicate()[0]
            tortoize_dict = json.loads(tortoize_output)
            tortoize_residues = tortoize_dict["model"]["1"]["residues"]
            tortoize_z_scores = {
                residue["seqID"]: residue["ramachandran"]["z-score"]
                for residue in tortoize_residues}
            tortoize_results.append(tortoize_z_scores)

    model_series = metrics_model_series_from_files(model_paths,
                                                   reflections_paths,
                                                   sequence_paths,
                                                   distpred_paths,
                                                   run_covariance,
                                                   run_molprobity,
                                                   multiprocessing)
    model_series_data = model_series.get_raw_data(tortoize_results)
    panel = Panel(model_series_data)
    panel_string = panel.dwg.tostring()
    if wrap_in_html:
        panel_string = f'<!DOCTYPE html>\n<html lang="en">\n\t<head>\n\t\t<meta charset="utf-8">\n\t\t<title>Iris Report</title>\n\t</head>\n\t<body>\n\t\t{panel_string}\n\t</body>\n</html>'

    if output_dir is None:
        return panel_string

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    extension = 'html' if wrap_in_html else 'svg'
    with open(os.path.join(output_dir, f'report.{extension}'), 'w', encoding='utf8') as outfile:
        outfile.write(panel_string)
