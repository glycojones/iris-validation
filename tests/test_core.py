import os
import time
from os import path

from iris_validation import generate_report


INPUT_DIR = './test_data/'
OUTPUT_DIR = './test_output/'

PDB_ID = '3atp'
ROOT_PATH = str(os.path.join(INPUT_DIR, PDB_ID)) + '{suffix}'


if __name__ == '__main__':
    cwd = os.getcwd()
    print (cwd)
    t0 = time.time()

    generate_report(latest_model_path=ROOT_PATH.format(suffix='_final.pdb'),
                    latest_reflections_path=ROOT_PATH.format(suffix='_final.mtz'),
                    previous_model_path=ROOT_PATH.format(suffix='_0cyc.pdb'),
                    previous_reflections_path=ROOT_PATH.format(suffix='_0cyc.mtz'),
                    output_dir=OUTPUT_DIR)
    assert path.exists(OUTPUT_DIR)

    t1 = time.time()
    print('Time taken:', round(t1-t0, 2), 's')
    print()
