"""
General functions for TrueNAS integration.
"""
import logging

import salt.utils.path
import truenasutils as tn

log = logging.getLogger(__name__)

__virtualname__ = "truenas"


def __virtual__():
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def call(func, *args):
    """
    Execute a generic TrueNAS middleware call.
    Arguments can be specified as supplemental positional arguments.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas.call service.restart ssh

    func
        The API method to call.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.call(func, *args)


def job(func, *args):
    """
    Execute a generic TrueNAS middleware job.
    Arguments can be specified as supplemental positional arguments.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas.job certificate.delete 42

    func
        The API method to call as a job.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.job(func, *args)
