import os
import time
import pytest
import importlib 
from os import path

INPUT_DIR = './tests/test_data/KSWdata/'
OUTPUT_DIR = './tests/test_output/' + '{suffix}'

DATASET1_PATH = str(os.path.join(INPUT_DIR, "acnr")) + '{suffix}'


def test_acnr_noCOV_noMP_noRamaZ_spro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "acnr_noCOV_noMP_noRamaZ_spro"      
    iris.generate_report(latest_model_path=DATASET1_PATH.format(suffix='.pdb'),
                         latest_reflections_path=DATASET1_PATH.format(suffix='_refined.mtz'),
                         previous_model_path=DATASET1_PATH.format(suffix='_refined.pdb'),
                         previous_reflections_path=DATASET1_PATH.format(suffix='_refined.mtz'),
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")