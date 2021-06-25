import jittor as jt
import numpy as np

from zhusuan.distributions.base import Distribution


class Normal(Distribution):
    def __init__(self,
                 dtype='float32',
                 param_dtype='float32',
                 is_continues=True,
                 is_reparameterized=True,
                 group_ndims=0,
                 **kwargs):
        super(Normal, self).__init__(dtype,
                                     param_dtype,
                                     is_continues,
                                     is_reparameterized,
                                     group_ndims=group_ndims,
                                     **kwargs)
        self._mean = kwargs['mean']
        try:
            self._std = jt.cast(jt.array([kwargs['std']]), self._dtype) if type(kwargs['std']) in [int, float] else \
            kwargs['std']
        except:
            _logstd = jt.cast(jt.array([kwargs['logstd']]), self._dtype) if type(kwargs['logstd']) in [int, float] else \
            kwargs['logstd']
            self._std = jt.exp(_logstd)

    def _batch_shape(self):
      return self._mean.shape

    def _sample(self, n_samples=1, **kwargs):
        if n_samples > 1:
            _shape = self._mean.shape
            _shape = [n_samples] + _shape
            _len = len(self._mean.shape)
            _mean = jt.repeat(self._mean, [n_samples, *_len * [1]])
            _std = jt.repeat(self._std, [n_samples, *_len * [1]])
        else:
            _shape = self._mean.shape
            _mean = jt.cast(self._mean, self._dtype)
            _std = jt.cast(self._std, self._dtype)

        if not self.is_reparameterized:
            _mean.stop_grad()
            _std.stop_grad()
        epsilon = jt.normal(0., 1., size=_shape)
        _sample = _mean + _std * epsilon
        self.sample_cache = _sample
        return _sample

    def _log_prob(self, sample=None, **kwargs):
        if sample is None:
            sample = self.sample_cache
        if len(sample.shape) > len(self._mean.shape):
            n_samples = sample.shape[0]
            _len = len(self._mean.shape)
            _mean = jt.repeat(self._mean, [n_samples, *_len * [1]])
            _std = jt.repeat(self._std, [n_samples, *_len * [1]])
        else:
            _mean = self._mean
            _std = self._std
        if not self.is_reparameterized:
            _mean.stop_grad()
            _std.stop_grad()
        logstd = jt.log(_std)
        c = -0.5 * np.log(2 * np.pi)
        precision = jt.exp(-2 * logstd)
        log_prob = c - logstd - 0.5 * precision * ((sample - _mean) ** 2)
        return log_prob
