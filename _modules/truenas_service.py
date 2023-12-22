"""
Operate on TrueNAS services.
This currently does not override the inbuilt ``service`` module
for FreeBSD.
"""

import logging

import salt.utils.path
import truenasutils as tn
from salt.exceptions import SaltInvocationError
from salt.utils.immutabletypes import freeze

log = logging.getLogger(__name__)

__virtualname__ = "truenas_service"
__func_alias__ = {"reload_": "reload"}


# mapping of API namespace to service name alias(es)
API_SERVICE_ALIASES = freeze(
    {
        "afp": set(),
        "smb": {"cifs"},
        "dyndns": {"dynamicdns"},
        "ftp": set(),
        "iscsitarget": {"iscsi.target"},
        "ldap": set(),
        "lldp": set(),
        "nfs": set(),
        "openvpn.client": {"openvpn_client"},
        "openvpn.server": {"openvpn_server"},
        "rsyncd": {"rsync"},
        "s3": set(),  # this is deprecated and will be removed
        "smart": {"smartd"},
        "snmp": set(),
        "ssh": set(),
        "system.advanced": set(),
        "system.general": set(),
        "tftp": set(),
        "ups": set(),
        "webdav": set(),
    }
)


def __virtual__():
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def get_enabled():
    """
    List enabled services.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.get_enabled
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("service.query", [["enable", "=", True]])
    return list(sorted(x["service"] for x in res))


def get_disabled():
    """
    List disabled services.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.get_disabled
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("service.query", [["enable", "=", False]])
    return list(sorted(x["service"] for x in res))


def get_running():
    """
    List running services.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.get_running
    """
    with tn.get_client(__opts__, __context__) as client:
        # Filtering with state=RUNNING crashes
        res = client.call("service.query")
    return list(sorted(x["service"] for x in res if x["state"] == "RUNNING"))


def enable(name, **kwargs):
    """
    Enable a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.enable cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        client.call("service.update", name, {"enable": True})
    return True


def disable(name, **kwargs):
    """
    Disable a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.disable cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        client.call("service.update", name, {"enable": False})
    return True


def enabled(name, **kwargs):
    """
    Check whether a service is enabled.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.enabled cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    return name in get_enabled()


def disabled(name, **kwargs):
    """
    Check whether a service is disabled.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.disabled cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    return name in get_disabled()


def available(name):
    """
    Check whether a service is available.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.available cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    return name in get_all()


def missing(name):
    """
    Check whether a service is not available (inverse of ``available``).

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.missing cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    return name not in get_all()


def get_all():
    """
    List all available services.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.get_all
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("service.query")
    return list(sorted(x["service"] for x in res))


def start(name):
    """
    Start a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.start cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.call("service.start", name)


def stop(name):
    """
    Stop a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.stop cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        # This returns False on success, not sure about failure though
        res = client.call("service.stop", name)
        return res is False


def restart(name):
    """
    Restart a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.restart cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.call("service.restart", name)


def reload_(name):
    """
    Reload a service.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.reload cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.call("service.reload", name)


def status(name, sig=None):  # pylint: disable=unused-argument
    """
    Check whether a service is running.

    .. note::
        Does not support globbing on service names.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.status cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.

    sig
        Unused, accepted for API compatibility.
    """
    with tn.get_client(__opts__, __context__) as client:
        return client.call("service.started", name)


def get_config(name, include_private_keys=False):
    """
    Return the service configuration.
    This is TrueNAS-specific.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.get_config cifs

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.

    include_private_keys
        When querying the ``ssh`` configuration, also include
        private key contents in the output. Defaults to false.
    """
    ns = _get_api_ns(name)
    with tn.get_client(__opts__, __context__) as client:
        ret = client.call(f"{ns}.config")
    if ns == "ssh" and not include_private_keys:
        ret = {
            conf: val
            for conf, val in ret.items()
            if not (conf.startswith("host_") and conf.endswith("_key"))
        }
    return ret


def update_config(name, **kwargs):
    """
    Update a service configuration.
    This is TrueNAS-specific.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_service.update_config cifs workgroup="WORKGROUP"

    name
        The name of the service. Examples: ``cifs``, ``ssh``, ``ups``.
    """
    ns = _get_api_ns(name)
    payload = {k: v for k, v in kwargs.items() if not k.startswith("_")}
    with tn.get_client(__opts__, __context__) as client:
        return client.call(f"{ns}.update", payload)


def _get_api_ns(service):
    for ns, aliases in API_SERVICE_ALIASES.items():
        if service == ns or service in aliases:
            return ns
    raise SaltInvocationError(f"Unknown service '{service}'")
