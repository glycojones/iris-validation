import os
import time
from os import path

from iris_validation import generate_report

INPUT_DIR = './tests/test_data/'
OUTPUT_DIR = './tests/test_output/'

PDB_ID = '3atp'
ROOT_PATH = str(os.path.join(INPUT_DIR, PDB_ID)) + '{suffix}'

def test_generate_vanilla_report ():
    t0 = time.time()

    from importlib.metadata import version
    print("\nTesting Iris version " + version("iris_validation"))
          
    generate_report(latest_model_path=ROOT_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=ROOT_PATH.format(suffix='_final.mtz'),
                    previous_model_path=ROOT_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=ROOT_PATH.format(suffix='_0cyc.mtz'),
                    output_dir=OUTPUT_DIR,
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_name_prefix="vanilla_report")
    assert path.exists(OUTPUT_DIR.format(suffix="/report.html"))

def test_generate_one_model_report ():
    t0 = time.time()

    from importlib.metadata import version
    print("\nTesting Iris version " + version("iris_validation"))
          
    generate_report(latest_model_path=ROOT_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=ROOT_PATH.format(suffix='_final.mtz'),
                    output_dir=OUTPUT_DIR,
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_name_prefix="one_model_report")
    assert path.exists(OUTPUT_DIR.format(suffix="/report.html"))

    t1 = time.time()
    print('Time taken:', round(t1-t0, 2), 's')
    print()

    t1 = time.time()
    print('Time taken:', round(t1-t0, 2), 's')
    print()

def test_generate_rama_z_report ():
    t0 = time.time()

    generate_report(latest_model_path=ROOT_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=ROOT_PATH.format(suffix='_final.mtz'),
                    latest_sequence_path=ROOT_PATH.format(suffix='.fasta'),
                    latest_distpred_path=ROOT_PATH.format(suffix='.npz'),
                    previous_model_path=ROOT_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=ROOT_PATH.format(suffix='_0cyc.mtz'),
                    previous_sequence_path=ROOT_PATH.format(suffix='.fasta'),
                    previous_distpred_path=ROOT_PATH.format(suffix='.npz'),
                    run_covariance=False,
                    run_molprobity=False,
                    calculate_rama_z=True,
                    multiprocessing=True,
                    output_dir=OUTPUT_DIR,
                    output_name_prefix="rama_z_report")
    assert path.exists(OUTPUT_DIR.format(suffix="/report.html"))

    t1 = time.time()
    print('Time taken:', round(t1-t0, 2), 's')
    print()

def test_generate_molprobity_report ():
    t0 = time.time()

    generate_report(latest_model_path=ROOT_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=ROOT_PATH.format(suffix='_final.mtz'),
                    latest_sequence_path=ROOT_PATH.format(suffix='.fasta'),
                    latest_distpred_path=ROOT_PATH.format(suffix='.npz'),
                    previous_model_path=ROOT_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=ROOT_PATH.format(suffix='_0cyc.mtz'),
                    previous_sequence_path=ROOT_PATH.format(suffix='.fasta'),
                    previous_distpred_path=ROOT_PATH.format(suffix='.npz'),
                    run_covariance=False,
                    run_molprobity=True,
                    calculate_rama_z=False,
                    multiprocessing=True,
                    output_dir=OUTPUT_DIR,
                    output_name_prefix="molprobity_report")
    assert path.exists(OUTPUT_DIR.format(suffix="/report.html"))

    t1 = time.time()
    print('Time taken:', round(t1-t0, 2), 's')
    print()