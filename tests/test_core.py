import os
import time
import pytest
import importlib 
from os import path

INPUT_DIR = './tests/test_data/'
OUTPUT_DIR = './tests/test_output/' + '{suffix}'

DATASET1_PATH = str(os.path.join(INPUT_DIR, "3atp")) + '{suffix}'
DATASET2_PATH = str(os.path.join(INPUT_DIR, "8ira")) + '{suffix}'
DATASET3_PATH = str(os.path.join(INPUT_DIR, "5ni1")) + '{suffix}'
DATASET4_PATH = str(os.path.join(INPUT_DIR, "neutron")) + '{suffix}'

@pytest.mark.simple
def test_2m2d_noCOV_noMP_noRamaZ_mpro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "2m2d_noCOV_noMP_noRamaZ_mpro"      
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                         second_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                         second_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=True,
                         output_name_prefix=job_name,
                         custom_labels={'First':'Input', 'Second':'Refined'} )
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_2m0d_noCOV_noMP_noRamaZ_mpro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "2m0d_noCOV_noMP_noRamaZ_mpro"      
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         second_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=True,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_2m2d_16chains_noCOV_noMP_noRamaZ_spro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "2m2d_16chains_noCOV_noMP_noRamaZ_spro"      
    iris.generate_report(first_model_path=DATASET2_PATH.format(suffix='.cif'),
                         first_reflections_path=DATASET2_PATH.format(suffix='.mtz'),
                         second_model_path=DATASET2_PATH.format(suffix='_final.cif'),
                         second_reflections_path=DATASET2_PATH.format(suffix='.mtz'),
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


# multiprocessing is definitely an issue - test wll run in single process mode until sorted
def test_1m1d_noCOV_noMP_noRamaZ_mpro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "1m1d_noCOV_noMP_noRamaZ_mpro"      
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                         second_model_path=None, 
                         second_reflections_path=None,
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


def test_1m1d_noCOV_noMP_noRamaZ_spro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "1m1d_noCOV_noMP_noRamaZ_spro"      
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")

def test_neutron ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "neutron"      
    iris.generate_report(first_model_path=DATASET4_PATH.format(suffix='.pdb'),
                         first_reflections_path=None,
                         second_model_path=None,
                         second_reflections_path=None,
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")

@pytest.mark.tortoize
def test_2m2d_noCOV_noMP_RamaZ_mpro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "2m2d_noCOV_noMP_RamaZ_mpro"
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                         first_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                         first_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                         second_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                         second_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                         second_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
                         second_distpred_path=DATASET1_PATH.format(suffix='.npz'),
                         run_covariance=False,
                         run_molprobity=False,
                         calculate_rama_z=True,
                         multiprocessing=False,
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


@pytest.mark.molprobity
def test_2m2d_noCOV_MP_noRamaZ_spro ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "test_2m2d_noCOV_MP_noRamaZ_spro"
    iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
                         first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
                         second_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
                         second_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
                         run_covariance=False,
                         run_molprobity=True,
                         calculate_rama_z=False,
                         multiprocessing=False,
                         discrete_metrics_to_display="Clashes",
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")

@pytest.mark.json
def test_json ():
    import iris_validation as iris
    importlib.reload(iris)
    job_name = "test_json"
    iris.generate_report(first_model_path=DATASET3_PATH.format(suffix='_refined.pdb'),
                         second_model_path=DATASET3_PATH.format(suffix='.pdb'),
                         first_model_metrics_json=DATASET3_PATH.format(suffix='_refined_data.json'),
                         second_model_metrics_json=DATASET3_PATH.format(suffix='_data.json'),
                         data_with_percentiles=["map_fit"],
                         continuous_metrics_to_display=["Avg. B","Std. B","Res. Fit","Rama Z"],
                         residue_bars_to_display=["Res. Fit"],
                         percentile_bar_range=[-3,3],
                         output_dir=OUTPUT_DIR.format(suffix=""),
                         output_name_prefix=job_name)
    assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")


# @pytest.mark.slow
# def test_2m2d_COV_MP_noRamaZ_spro ():
#     import iris_validation as iris
#     importlib.reload(iris)
#     job_name = "test_2m2d_COV_MP_noRamaZ_spro"
#     iris.generate_report(first_model_path=DATASET1_PATH.format(suffix='_final.pdb'),
#                          first_reflections_path=DATASET1_PATH.format(suffix='_final.mtz'),
#                          first_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
#                          first_distpred_path=DATASET1_PATH.format(suffix='.npz'),
#                          second_model_path=DATASET1_PATH.format(suffix='_0cyc.pdb'),
#                          second_reflections_path=DATASET1_PATH.format(suffix='_0cyc.mtz'),
#                          second_sequence_path=DATASET1_PATH.format(suffix='.fasta'),
#                          second_distpred_path=DATASET1_PATH.format(suffix='.npz'),
#                          run_covariance=True,
#                          run_molprobity=True,
#                          calculate_rama_z=False,
#                          multiprocessing=False,
#                          output_dir=OUTPUT_DIR.format(suffix=""),
#                          output_name_prefix=job_name)
#     assert path.exists(OUTPUT_DIR.format(suffix=job_name) + ".html")