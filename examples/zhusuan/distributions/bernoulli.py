import jittor as jt
import numpy as np

from zhusuan.distributions.base import Distribution


class Bernoulli(Distribution):
    def __init__(self,
                 dtype='float32',
                 param_dtype='float32',
                 is_continues=False,
                 is_reparameterized=True,
                 group_ndims=0,
                 **kwargs):
        super(Bernoulli, self).__init__(dtype,
                                        param_dtype,
                                        is_continues,
                                        is_reparameterized,
                                        group_ndims=group_ndims,
                                        **kwargs)
        self._probs = kwargs['probs']
        self._probs = jt.cast(self._probs, self._dtype)

    @property
    def probs(self):
        return self._probs

    def _batch_shape(self):
        return self.probs.shape

    def _sample(self, n_samples=1, **kwargs):
        if n_samples > 1:
            sample_shape = np.concatenate([[n_samples], self.batch_shape], axis=0).tolist()
            _probs = self._probs * jt.ones(sample_shape)
        else:
            _probs = self._probs
        _probs *= jt.cast(_probs <= 1, self._dtype)
        _sample = jt.bernoulli(_probs)
        _sample = jt.cast(_sample, self._dtype)
        self.sample_cache = _sample
        return _sample

    def _log_prob(self, sample=None):
        if sample is None:
            sample = self.sample_cache

        if len(sample.shape) > len(self._probs.shape):
            sample_shape = np.concatenate([[sample.shape[0]], self.batch_shape], axis=0).tolist()
            _probs = self._probs * jt.ones(sample_shape)
        else:
            _probs = self._probs

        log_prob = sample * jt.log(_probs + 1e-8) + (1 - sample) * jt.log(1 - _probs + 1e-8)
        return log_prob
