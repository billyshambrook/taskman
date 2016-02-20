import consulate


class Consul(consulate.Consul):
    def __init__(self, **kwargs):
        super(OwnConsul, self).__init__(**kwargs)
        self._lock = Lock(
            self._base_uri('http', kwargs['host'], kwargs['port']),
            self._adapter,
            self._session,
            None,
            None)

    @property
    def lock(self):
        return self._lock
