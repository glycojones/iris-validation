"""
iris_validation

A Python package for interactive, all-in-one graphical validation of 3D protein models.

This framework enables scientists to visualise per-residue validation metrics
across entire protein chains in a compact, intuitive, and interactive radial
diagram. It integrates standard metrics (e.g., MolProbity, Tortoize from PDB-REDO),
highlighting model areas requiring attention.

Key Features:
-------------
- Computes and visualises per-residue metrics: geometry, clashes, rotamers,
  backbone conformations, and fit to electron density.
- Supports integration with validation tools such as MolProbity and PDB-REDO.
- Generates "ripple" effects on the radial plot to highlight problematic regions.
- Provides both standalone CLI tools and modules for embedding in GUIs
  (e.g., CCP4i2 or CCP4 Cloud).
- Interactive plots to inspect individual residues and per-chain quality.

Installation:
-------------
Available via pip, source code and most easily, through CCP4 (ccp4.ac.uk)
"""
import os
import sys
import json
from types import MappingProxyType

from iris_validation.graphics import Panel
from iris_validation.metrics import metrics_model_series_from_files

PYTEST_RUN = 'pytest' in sys.modules
# this is a way of making sure a dictionary parameter does not change within the
# function so that there are not weird effects if the function is run more than once
default_labels = MappingProxyType({'First':'First', 'Second':'Second'})

def generate_report(
    first_model_path,
    first_reflections_path=None,
    first_sequence_path=None,
    first_distpred_path=None,
    second_model_path=None,
    second_reflections_path=None,
    second_sequence_path=None,
    second_distpred_path=None,
    run_covariance=False,
    run_molprobity=False,
    calculate_rama_z=True,
    multiprocessing=True,
    first_model_metrics_json=None,
    second_model_metrics_json=None,
    data_with_percentiles=None,  # only works with model_metrics_json files
    discrete_metrics_to_display=None,
    continuous_metrics_to_display=None,
    residue_bars_to_display=None,
    percentile_bar_label=None,
    percentile_bar_range=None,
    wrap_in_html=True,
    output_dir=None,
    output_name_prefix="report",
    custom_labels=default_labels
):
    """
    Generate a comparative or single-structure validation report from one or two structural models, 
    with or without experimental data. 

    This function creates a report that compares two models (or reports on a single model),
    using various metrics and visualisations. It optionally includes MolProbity validation,
    Ramachandran Z-score calculation via Tortoize, and residue-level bar plots, selectable by 
    using the slider on the main graphics. The labels for the two models are customisable, so
    they can be used after refinement (e.g. 'Input' and 'Refined') or to compare different 
    data collections (e.g. 'cryo' and 'RT')

    When two models are supplied, Iris will show the second one by default and add a selector 
    button to toggle between first and second. 

    Parameters:
        first_model_path (str): Path to the first model file (PDB or mmCIF, mmCIF strongly preferred).
        first_reflections_path (str, optional): Path to the first model's reflection data (MTZ or CIF).
        first_sequence_path (str, optional): Path to the first model's sequence file (FASTA).
        first_distpred_path (str, optional): Path to predicted distance distribution file for the first model.
        second_model_path (str, optional): Path to the second model file, for comparison.
        second_reflections_path (str, optional): Path to the second model's reflection data.
        second_sequence_path (str, optional): Path to the second model's sequence file.
        second_distpred_path (str, optional): Path to predicted distance distribution file for the second model.
        run_covariance (bool, optional): If True, calculate coordinate covariance matrices.
        run_molprobity (bool, optional): If True, run MolProbity validation via mmtbx (needs CCP4)
        calculate_rama_z (bool, optional): If True, compute the Ramachandran Z-score via Tortoize (needs CCP4).
        multiprocessing (bool, optional): If True, use multiprocessing to speed up calculations.
        first_model_metrics_json (str, optional): Path to JSON file with precomputed metrics for the first model.
        second_model_metrics_json (str, optional): Path to JSON file with precomputed metrics for the second model.
        data_with_percentiles (dict, optional): JSON-like structure with percentile benchmarks for metrics.
        discrete_metrics_to_display (list, optional): List of discrete metrics (e.g. ['clashscore']) to display.
        continuous_metrics_to_display (list, optional): List of continuous metrics (e.g. side-chain fit) to display.
        residue_bars_to_display (list, optional): List of residue-level metrics to display as bar charts.
        percentile_bar_label (str, optional): Label for the percentile bar in summary plots.
        percentile_bar_range (tuple, optional): Tuple defining the display range of the percentile bar (min, max).
        wrap_in_html (bool, optional): If True, wraps the report in a standalone HTML page. 
        output_dir (str, optional): Directory where the output report and files will be saved.
        output_name_prefix (str, optional): Prefix for the output report filename. Default is "report".
        custom_labels (dict, optional): Dictionary specifying custom labels for 'First' and 'Second' models.

    Returns:
        str: Path to the generated report file.
    """

    # sanitise output file name
    output_name_prefix = output_name_prefix.replace('/','_').replace('.','_')

    model_series = metrics_model_series_from_files((first_model_path, second_model_path),
                                                   (first_reflections_path, second_reflections_path),
                                                   (first_sequence_path, second_sequence_path),
                                                   (first_distpred_path, second_distpred_path),
                                                   (first_model_metrics_json, second_model_metrics_json),
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
