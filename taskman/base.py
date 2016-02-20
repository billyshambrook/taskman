"""Base classes."""
import logging

import consulate


logger = logging.getLogger(__name__)


class _Taskman(object):
    """Base client."""

    def __init__(
            self, vhost='/', base_path=None, host='localhost', port=8500, datacenter=None, token=None,
            scheme='http', adapter=None):
        """Arguments include the ones available for the consulate client."""
        self._vhost = vhost
        self._base_path = posixpath.join(base_path, vhost)

        self._client = consulate.Consul(host, port, datacenter, token, scheme, adapter)
        self._queue = Queue(self._client, self._base_path)

    @property
    def app(self):
        """The app name."""
        return self._app

    @property
    def app_path(self):
        """The base path where the application will store it's data."""
        return self._app_path

    @property
    def vhost(self):
        """
        The virtual host.

        Helps to segregate applications using the same Taskman instance.
        """
        return self._vhost
