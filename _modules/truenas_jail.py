"""
Operate on TrueNAS jails.
"""
import logging

import salt.utils.path
import truenasutils as tn

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
