"""
Operate on TrueNAS jails.
"""
import logging

import salt.utils.path
import truenasutils as tn
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_jail"
__func_alias__ = {
    "list_": "list",
}


def __virtual__():
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def list_(name_prefix=None, order_by="id"):
    """
    List (all) present jails and their config.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.list

    name_prefix
        Filter jails by name (``id`` field) prefix.

    order_by
        Order returned list by this named value.
        Defaults to ``id`` (the name).
    """
    filters = []
    # ensure we don't get paged results
    options = {"limit": 0}
    if name_prefix:
        filters.append(["id", "~", name_prefix])
    if order_by:
        if not isinstance(order_by, list):
            order_by = [order_by]
        options["order_by"] = [str(x) for x in order_by]
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("jail.query", filters, options)
    return res


def exists(name):
    """
    Check if a jail exists.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.exists minio

    name
        The name (``id`` field) of the jail.
    """
    try:
        _get_jail(name)
    except CommandExecutionError as err:
        if "No such jail" not in str(err):
            raise
        return False
    return True


def is_running(name):
    """
    Check if a jail is running.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.is_running minio

    name
        The name (``id`` field) of the jail.
    """
    jail = _get_jail(name)
    return jail["state"] == "up"


def is_dead(name):
    """
    Check if a jail is stopped.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.is_dead minio

    name
        The name (``id`` field) of the jail.
    """
    jail = _get_jail(name)
    return jail["state"] == "down"


def start(name):
    """
    Start a jail.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.start minio

    name
        The name (``id`` field) of the jail.
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.job("jail.start", name)
    return res


def stop(name, force=False):
    """
    Stop a jail.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.stop minio

    name
        The name (``id`` field) of the jail.

    force
        Force stopping. Defaults to false.
    """
    options = {}
    if force:
        options["force"] = True
    with tn.get_client(__opts__, __context__) as client:
        res = client.job("jail.stop", name, options)
    return res


def restart(name):
    """
    Restart a jail.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.restart minio

    name
        The name (``id`` field) of the jail.
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.job("jail.restart", name)
    return res


def delete(name, force=False):
    """
    Delete a jail.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_jail.delete minio

    name
        The name (``id`` field) of the jail.

    force
        Force deletion. Defaults to false.
    """
    options = {}
    if force:
        options["force"] = True
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("jail.delete", name, options)
    return res


def _get_jail(name):
    curr = list_(name)
    if not curr:
        raise CommandExecutionError(f"No such jail: {name}")
    for jail in curr:
        if jail["id"] == name:
            return jail
    raise CommandExecutionError(f"No such jail: {name}")
