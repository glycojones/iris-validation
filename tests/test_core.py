import os
import time
import pytest
from os import path

from iris_validation import generate_report

INPUT_DIR = './tests/test_data/'
OUTPUT_DIR = './tests/test_output/' + '{suffix}'

DATASET1_PATH = str(os.path.join(INPUT_DIR, "3atp")) + '{suffix}'
DATASET2_PATH = str(os.path.join(INPUT_DIR, "refined")) + '{suffix}'


def test_generate_vanilla_report ():
    job_name = "vanilla_report"      
    generate_report(latest_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                    previous_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_generate_servalcat_report ():
    job_name = "servalcat_report"      
    generate_report(latest_model_path=DATASET2_PATH.format(suffix='.mmcif'),
                    previous_model_path=DATASET2_PATH.format(suffix='.pdb'),
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_no_expdata_report ():
    job_name = "noexp_data_report"      
    generate_report(latest_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                    previous_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")

@pytest.mark.problem
def test_generate_one_model_report ():
    job_name = "one_model_report"      
    generate_report(latest_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=False,
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_generate_rama_z_report ():
    job_name = "rama_z_report"
    generate_report(latest_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                    latest_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                    latest_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                    previous_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                    previous_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                    previous_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=True,
                    multiprocessing=True,
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


@pytest.mark.slow
def test_generate_molprobity_report ():
    job_name = "molprobity_report"
    generate_report(latest_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                    latest_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                    latest_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                    previous_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                    previous_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                    previous_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                    run_covariance=False,
                    run_molprobity=True,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_dir=OUTPUT_DIR.format(suffix=""),
                    output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")
