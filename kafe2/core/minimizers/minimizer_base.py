import numpy as np
from scipy.optimize import brentq


class MinimizerBase(object):

    def __init__(self):
        self._invalidate_cache()  # initializes caches with None
        self._save_state_dict = dict()

    def _reset(self):
        self._invalidate_cache()

    def _invalidate_cache(self):
        self._par_asymm_err = None

    def _save_state(self):
        self._save_state_dict['asymmetric_parameter_error'] = self._par_asymm_err

    def _load_state(self):
        self._par_asymm_err = self._save_state_dict['asymmetric_parameter_error']

    def _calculate_asymmetric_parameter_errors(self):  # TODO max calls
        self.minimize()
        self._save_state()
        _asymm_par_errs = np.zeros(shape=self.parameter_values.shape + (2,))
        for _par_index, _par_name in enumerate(self.parameter_names):
            _target_chi_2 = self.function_value + 1.0
            _min_parameters = self.parameter_values

            _par_min = self.parameter_values[_par_index]
            _par_err = self.parameter_errors[_par_index]

            _cut_dn = self._find_chi_2_cut(_par_name, _par_min - 2 * _par_err, _par_min, _target_chi_2,
                                           _min_parameters)
            _asymm_par_errs[_par_index, 0] = _cut_dn - _par_min

            _cut_up = self._find_chi_2_cut(_par_name, _par_min, _par_min + 2 * _par_err, _target_chi_2,
                                           _min_parameters)
            _asymm_par_errs[_par_index, 1] = _cut_up - _par_min
            self._load_state()
        return _asymm_par_errs

    def _find_chi_2_cut(self, parameter_name, low, high, target_chi_2, min_parameters):
        def _profile(parameter_value):
            self.set_several(self.parameter_names, min_parameters)
            self.set(parameter_name, parameter_value)
            self.fix(parameter_name)
            self.minimize()
            _fval = self.function_value
            self.release(parameter_name)
            return _fval - target_chi_2

        return brentq(f=_profile, a=low, b=high, xtol=self.tolerance)

    @property
    def function_value(self):
        raise NotImplementedError()

    @property
    def num_pars(self):
        raise NotImplementedError()

    @property
    def parameter_values(self):
        raise NotImplementedError()

    @property
    def parameter_errors(self):
        raise NotImplementedError()

    @property
    def asymmetric_parameter_errors(self):
        if self._par_asymm_err is None:
            self._par_asymm_err = self._calculate_asymmetric_parameter_errors()
        return self._par_asymm_err

    @property
    def parameter_names(self):
        raise NotImplementedError()

    @property
    def tolerance(self):
        raise NotImplementedError()

    @tolerance.setter
    def tolerance(self, new_tol):
        raise NotImplementedError()

    def set(self, parameter_name, parameter_value):
        raise NotImplementedError()

    def set_several(self, parameter_names, parameter_values):
        raise NotImplementedError()

    def fix(self, parameter_name):
        raise NotImplementedError()

    def release(self, parameter_name):
        raise NotImplementedError()

    def minimize(self):  # TODO max calls
        raise NotImplementedError()
