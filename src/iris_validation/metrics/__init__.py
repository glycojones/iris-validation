from multiprocessing import Process, Queue

import subprocess
import json
import clipper

from iris_validation.utils import ONE_LETTER_CODES
from iris_validation.metrics.residue import MetricsResidue
from iris_validation.metrics.chain import MetricsChain
from iris_validation.metrics.model import MetricsModel
from iris_validation.metrics.series import MetricsModelSeries
from iris_validation.metrics.reflections import ReflectionsHandler


def _get_minimol_from_path(model_path):
    fpdb = clipper.MMDBfile()
    minimol = clipper.MiniMol()
    try:
        fpdb.read_file(model_path)
        fpdb.import_minimol(minimol)
    except Exception as exception:
        raise Exception("Failed to import model file") from exception
    return minimol


def _get_minimol_seq_nums(minimol):
    seq_nums = {}
    for chain in minimol:
        chain_id = str(chain.id()).strip()
        seq_nums[chain_id] = []
        for residue in chain:
            seq_num = int(residue.seqnum())
            seq_nums[chain_id].append(seq_num)
    return seq_nums


def _get_reflections_data(model_path, reflections_path, model_id=None, out_queue=None):
    minimol = _get_minimol_from_path(model_path)
    reflections_handler = ReflectionsHandler(reflections_path, minimol=minimol)
    resolution = reflections_handler.resolution_limit
    density_scores = reflections_handler.calculate_all_density_scores()
    reflections_data = (resolution, density_scores)
    if out_queue is not None:
        out_queue.put(("reflections", model_id, reflections_data))
    return reflections_data


def _get_molprobity_data(model_path, seq_nums, model_id=None, out_queue=None):
    try:
        from mmtbx.command_line import load_model_and_data
        from mmtbx.command_line.molprobity import get_master_phil
        from mmtbx.validation.molprobity import molprobity, molprobity_flags
    except (ImportError, ModuleNotFoundError):
        print(
            "WARNING: Failed to import MolProbity; continuing without MolProbity analyses"
        )
        return

    try:
        cmdline = load_model_and_data(
            args=[f'pdb.file_name="{model_path}"', "quiet=True"],
            master_phil=get_master_phil(),
            require_data=False,
            process_pdb_file=True,
        )
        validation = molprobity(model=cmdline.model)
    except Exception:
        print(
            "WARNING: Failed to run MolProbity; continuing without MolProbity analyses"
        )
        return

    molprobity_data = {}
    molprobity_data["model_wide"] = {}
    molprobity_data["model_wide"]["summary"] = {
        "cbeta_deviations": validation.cbetadev.n_outliers,
        "clashscore": validation.clashscore(),
        "ramachandran_outliers": validation.rama_outliers(),
        "ramachandran_favoured": validation.rama_favored(),
        "rms_bonds": validation.rms_bonds(),
        "rms_angles": validation.rms_angles(),
        "rotamer_outliers": validation.rota_outliers(),
        "molprobity_score": validation.molprobity_score(),
    }

    molprobity_data["model_wide"]["details"] = {
        "clash": [],
        "c-beta": [],
        "nqh_flips": [],
        "omega": [],
        "ramachandran": [],
        "rotamer": [],
    }

    molprobity_results = {
        "clash": validation.clashes.results,
        "c-beta": validation.cbetadev.results,
        "nqh_flips": validation.nqh_flips.results,
        "omega": validation.omegalyze.results,
        "ramachandran": validation.ramalyze.results,
        "rotamer": validation.rotalyze.results,
    }

    for chain_id, chain_seq_nums in seq_nums.items():
        molprobity_data[chain_id] = {}
        for seq_num in chain_seq_nums:
            molprobity_data[chain_id][seq_num] = {
                category: None for category in molprobity_results
            }
            molprobity_data[chain_id][seq_num]["clash"] = 2

    for category, results in molprobity_results.items():
        for result in results:
            if category == "clash":
                for atom in result.atoms_info:
                    chain_id = atom.chain_id.strip()
                    seq_num = int(atom.resseq.strip())
                    try:
                        if molprobity_data[chain_id][seq_num][category] > 0:
                            molprobity_data[chain_id][seq_num][category] -= 1
                    except:
                        print(
                            f"chain id: {chain_id}, seq_num: {seq_num} category: {category}"
                        )
                details_line = [
                    " ".join(a.id_str().split()) for a in result.atoms_info
                ] + [result.overlap]
                molprobity_data["model_wide"]["details"][category].append(details_line)
                continue

            chain_id = result.chain_id.strip()
            seq_num = int(result.resseq.strip())
            if category in ("ramachandran", "rotamer"):
                if result.score < 0.3:
                    molprobity_data[chain_id][seq_num][category] = 0
                elif result.score < 2.0:
                    molprobity_data[chain_id][seq_num][category] = 1
                else:
                    molprobity_data[chain_id][seq_num][category] = 2
            else:
                if result.outlier:
                    chain_id = result.chain_id.strip()
                    seq_num = int(result.resseq.strip())
                    molprobity_data[chain_id][seq_num][category] = 0

            if result.outlier:
                score = result.deviation if category == "c-beta" else result.score
                details_line = [
                    result.chain_id.strip(),
                    result.resid.strip(),
                    result.resname.strip(),
                    score,
                ]
                molprobity_data["model_wide"]["details"][category].append(details_line)

    if out_queue is not None:
        out_queue.put(("molprobity", model_id, molprobity_data))

    return molprobity_data


def _get_covariance_data(
    model_path,
    sequence_path,
    distpred_path,
    seq_nums,
    distpred_format="rosettanpz",
    map_align_exe="map_align",
    dssp_exe="mkdssp",
    model_id=None,
    out_queue=None,
):
    try:
        from Bio.PDB import PDBParser
        from Bio.PDB.DSSP import DSSP
        from conkit import applications, command_line, io, plot
    except (ImportError, ModuleNotFoundError):
        print(
            "WARNING: Failed to import Biopython; continuing without covariance analyses"
        )
        return

    parser = PDBParser()
    structure = parser.get_structure("structure", model_path)[0]
    dssp = DSSP(structure, model_path, dssp=dssp_exe, acc_array="Wilke")
    model = io.read(model_path, "pdb" if model_path.endswith(".pdb") else "mmcif").top
    prediction = io.read(distpred_path, distpred_format).top
    sequence = io.read(sequence_path, "fasta").top
    figure = plot.ModelValidationFigure(
        model, prediction, sequence, dssp, map_align_exe=map_align_exe
    )

    covariance_data = {}
    for chain_id, chain_seq_nums in seq_nums.items():
        covariance_data[chain_id] = {}
        for seq_num in chain_seq_nums:
            # TODO: by chain
            score = (
                figure.smooth_scores[seq_num]
                if 0 < seq_num < len(figure.smooth_scores)
                else None
            )
            alignment = 0 if seq_num in figure.alignment.keys() else 1
            covariance_data[chain_id][seq_num] = (score, alignment)

    if out_queue is not None:
        out_queue.put(("covariance", model_id, covariance_data))

    return covariance_data


def _get_tortoize_data(model_path, seq_nums, model_id=None, out_queue=None):
    rama_z_data = {chain_id: {} for chain_id in seq_nums.keys()}
    tortoize_process = subprocess.Popen(
        ["tortoize", str(model_path)],
        shell=False,  # False because Linux shell expects whole command in a string not a list
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        tortoize_output, tortoize_stderr = tortoize_process.communicate()
        if tortoize_process.returncode != 0 or tortoize_stderr:
            print("WARNING: Failed to run tortoize")
        tortoize_dict = json.loads(tortoize_output)
    except Exception:
        print("WARNING: Failed to read tortoize output")
        return

    residues = tortoize_dict["model"]["1"]["residues"]
    for res in residues:
        rama_z_data[res["pdb"]["strandID"]][res["pdb"]["seqNum"]] = res["ramachandran"][
            "z-score"
        ]

    if out_queue is not None:
        out_queue.put(("rama_z", model_id, rama_z_data))

    return rama_z_data


def metrics_model_series_from_files(
    model_paths,
    reflections_paths=None,
    sequence_paths=None,
    distpred_paths=None,
    model_json_paths=None,
    run_covariance=False,
    run_molprobity=False,
    calculate_rama_z=False,
    data_with_percentiles=None,
    multiprocessing=True,
):

    path_lists = [
        model_paths,
        reflections_paths,
        sequence_paths,
        distpred_paths,
        model_json_paths,
    ]

    all_minimol_data = []
    all_covariance_data = []
    all_molprobity_data = []
    all_reflections_data = []
    all_rama_z_data = []
    all_bfactor_data = []  # if externally supplied
    num_queued = 0
    results_queue = Queue()
    check_resnum = False
    for model_id, file_paths in enumerate(zip(*path_lists)):
        (
            model_path,
            reflections_path,
            sequence_path,
            distpred_path,
            json_data_path,
        ) = file_paths
        if model_path is None:
            continue
        minimol = _get_minimol_from_path(model_path)
        seq_nums = _get_minimol_seq_nums(minimol)
        covariance_data = None
        molprobity_data = None
        reflections_data = None
        rama_z_data = None
        bfactor_data = None

        # load external metric data from the provided json file path
        if json_data_path:
            check_resnum = True
            with open(json_data_path, "r") as j:
                json_data = json.load(j)
            for metric in json_data:
                if metric == "molprobity":
                    molprobity_data = json_data["molprobity"]
                    run_molprobity = False
                if metric == "rama_z":
                    rama_z_data = json_data["rama_z"]
                    calculate_rama_z = False
                if metric == "map_fit":
                    reflections_data = json_data["map_fit"]
                    reflections_path = None
                if metric == "b_factor":
                    bfactor_data = json_data["b_factor"]
        if run_covariance:
            if multiprocessing:
                p = Process(
                    target=_get_covariance_data,
                    args=(model_path, sequence_path, distpred_path, seq_nums),
                    kwargs={"model_id": model_id, "out_queue": results_queue},
                )
                p.start()
                num_queued += 1
                print("Adding covariance data")
            else:
                covariance_data = _get_covariance_data(
                    model_path, sequence_path, distpred_path, seq_nums
                )
        if run_molprobity:
            if multiprocessing:
                p = Process(
                    target=_get_molprobity_data,
                    args=(model_path, seq_nums),
                    kwargs={"model_id": model_id, "out_queue": results_queue},
                )
                p.start()
                num_queued += 1
                print("Adding molprobity data")
            else:
                molprobity_data = _get_molprobity_data(model_path, seq_nums)
        if reflections_path is not None:
            if multiprocessing:
                p = Process(
                    target=_get_reflections_data,
                    args=(model_path, reflections_path),
                    kwargs={"model_id": model_id, "out_queue": results_queue},
                )
                p.start()
                num_queued += 1
                print("Adding reflection data")
            else:
                reflections_data = _get_reflections_data(model_path, reflections_path)
        if calculate_rama_z:
            if multiprocessing:
                p = Process(
                    target=_get_tortoize_data,
                    args=(model_path, seq_nums),
                    kwargs={"model_id": model_id, "out_queue": results_queue},
                )
                p.start()
                num_queued += 1
                print("Adding tortoize data")
            else:
                rama_z_data = _get_tortoize_data(model_path, seq_nums)

        all_minimol_data.append(minimol)
        all_covariance_data.append(covariance_data)
        all_molprobity_data.append(molprobity_data)
        all_reflections_data.append(reflections_data)
        all_rama_z_data.append(rama_z_data)
        all_bfactor_data.append(bfactor_data)

    if multiprocessing:
        for _ in range(num_queued):
            result_type, model_id, result = results_queue.get()
            if result_type == "covariance":
                all_covariance_data[model_id] = result
            if result_type == "rama_z":
                all_rama_z_data[model_id] = result
            if result_type == "molprobity":
                all_molprobity_data[model_id] = result
            if result_type == "reflections":
                all_reflections_data[model_id] = result

    metrics_models = []
    for model_id, model_data in enumerate(
        zip(
            all_minimol_data,
            all_covariance_data,
            all_molprobity_data,
            all_reflections_data,
            all_rama_z_data,
            all_bfactor_data,
        )
    ):
        metrics_model = MetricsModel(*model_data, check_resnum, data_with_percentiles)
        metrics_models.append(metrics_model)

    metrics_model_series = MetricsModelSeries(metrics_models)
    return metrics_model_series
