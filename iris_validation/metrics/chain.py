from iris_validation.metrics.residue import MetricsResidue


class MetricsChain:
    def __init__(
        self,
        mmol_chain,
        parent_model=None,
        covariance_data=None,
        molprobity_data=None,
        density_scores=None,
        tortoize_data=None,
        bfactor_data=None,
        check_resnum=False,
        data_with_percentiles=None,
    ):
        self.minimol_chain = mmol_chain
        self.parent_model = parent_model
        self.covariance_data = covariance_data
        self.molprobity_data = molprobity_data
        self.density_scores = density_scores
        self.tortoize_data = tortoize_data

        self._index = -1
        self.residues = [ ]
        self.length = len(mmol_chain)
        self.chain_id = str(mmol_chain.id().trim())
        dict_ext_percentiles = {}  # stores the percentiles supplied externally
        for residue_index, mmol_residue in enumerate(mmol_chain):
            previous_residue = mmol_chain[residue_index-1] if residue_index > 0 else None
            next_residue = mmol_chain[residue_index+1] if residue_index < len(mmol_chain)-1 else None
            seq_num = int(mmol_residue.seqnum())
            res_id = str(mmol_residue.id()).strip()
            # covariance
            if covariance_data is None:
                residue_covariance_data = None
            else:
                if check_resnum:
                    try:
                        residue_covariance_data = covariance_data[res_id]
                    except KeyError:
                        residue_covariance_data = None
                else:
                    residue_covariance_data = covariance_data[seq_num]
            # molprobity
            if molprobity_data is None:
                residue_molprobity_data = None
            else:
                if check_resnum:
                    try:
                        residue_molprobity_data = molprobity_data[res_id]
                    except KeyError:
                        residue_molprobity_data = None
                else:
                    residue_molprobity_data = molprobity_data[seq_num]
            # density scores
            if density_scores is None:
                residue_density_scores = None
            else:
                if check_resnum:
                    if data_with_percentiles and "map_fit" in data_with_percentiles:
                        try:
                            residue_density_scores = density_scores[res_id][0]
                            dict_ext_percentiles["map_fit"] = density_scores[res_id][-1]
                        except KeyError:
                            residue_density_scores = None
                    else:
                        try:
                            residue_density_scores = density_scores[res_id]
                        except KeyError:
                            residue_density_scores = None
                else:
                    residue_density_scores = density_scores[seq_num]
            # rama_z
            if tortoize_data is None:
                residue_tortoize_scores = None
            else:
                if check_resnum:
                    try:
                        residue_tortoize_scores = tortoize_data[res_id]
                    except KeyError:
                        residue_tortoize_scores = None
                else:
                    residue_tortoize_scores = tortoize_data.get(seq_num, None)
            # ext b-factor
            if bfactor_data is None:
                residue_bfact_score = None
            else:
                if check_resnum:
                    if data_with_percentiles and "b-factor" in data_with_percentiles:
                        try:
                            residue_bfact_score = bfactor_data[res_id][0]
                            dict_ext_percentiles["b-factor"] = bfactor_data[res_id][-1]
                        except KeyError:
                            residue_bfact_score = None
                    else:
                        try:
                            residue_bfact_score = bfactor_data[res_id]
                        except KeyError:
                            residue_bfact_score = None
                else:
                    residue_bfact_score = bfactor_data[seq_num]
            residue = MetricsResidue(
                mmol_residue,
                residue_index,
                previous_residue,
                next_residue,
                self,
                residue_covariance_data,
                residue_molprobity_data,
                residue_density_scores,
                residue_tortoize_scores,
                residue_bfact_score,
                dict_ext_percentiles,
            )
            self.residues.append(residue)

        for residue_index, residue in enumerate(self.residues):
            if (0 < residue_index < len(self.residues)-1) and \
               (self.residues[residue_index-1].is_aa and residue.is_aa and self.residues[residue_index+1].is_aa) and \
               (self.residues[residue_index-1].sequence_number+1 == residue.sequence_number == self.residues[residue_index+1].sequence_number-1):
                residue.is_consecutive_aa = True
            else:
                residue.is_consecutive_aa = False

    def __iter__(self):
        return self

    def __next__(self):
        if self._index < self.length-1:
            self._index += 1
            return self.residues[self._index]
        self._index = -1
        raise StopIteration

    def get_residue(self, sequence_number):
        return next(residue for residue in self.residues if residue.sequence_number == sequence_number)

    def remove_residue(self, residue):
        if residue in self.residues:
            self.residues.remove(residue)
            self.length -= 1
        else:
            print('Error removing residue, no matching residue was found.')

    def remove_non_aa_residues(self):
        non_aa_residues = [ residue for residue in self.residues if not residue.is_aa ]
        for residue in non_aa_residues:
            self.remove_residue(residue)

    def b_factor_lists(self):
        all_bfs, aa_bfs, mc_bfs, sc_bfs, non_aa_bfs, water_bfs, ligand_bfs, ion_bfs = [ [ ] for _ in range(8) ]
        for residue in self.residues:
            all_bfs.append(residue.avg_b_factor)
            if residue.is_aa:
                aa_bfs.append(residue.avg_b_factor)
                mc_bfs.append(residue.mc_b_factor)
                sc_bfs.append(residue.sc_b_factor)
            else:
                non_aa_bfs.append(residue.avg_b_factor)
                if residue.is_water:
                    water_bfs.append(residue.avg_b_factor)
                # Followed to be consistent with the original CCP4 i2 validation tool:
                elif len(residue.atoms) > 1:
                    ligand_bfs.append(residue.avg_b_factor)
                else:
                    ion_bfs.append(residue.avg_b_factor)
        return all_bfs, aa_bfs, mc_bfs, sc_bfs, non_aa_bfs, water_bfs, ligand_bfs, ion_bfs
