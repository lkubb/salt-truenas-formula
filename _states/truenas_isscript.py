"""
Interface for Init/Shutdown Scripts
"""
import logging
from pathlib import Path

from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_isscript"

TYPES = ("COMMAND", "SCRIPT")
WHENS = ("PREINIT", "POSTINIT", "SHUTDOWN")


def __virtual__():
    try:
        __salt__["truenas_isscript.list"]
    except KeyError:
        return False, "`truenas_isscript` execution module not found"
    return __virtualname__


def present(name, data, typ="COMMAND", when="POSTINIT", enabled=True, timeout=None):
    """
    Ensure a TrueNAS init/shutdown script is present.

    name
        The comment. We need something to track entities. Could use ``data`` if
        we were disallowing script text.

    data
        The input for the type. For ``COMMAND``, the command to run.
        For ``SCRIPT``, either the script text or a local file.

    typ
        The entity type. Either ``COMMAND`` or ``SCRIPT``. Defaults to ``COMMAND``.

    when
        When the entity should be executed. Either ``PREINIT``, ``POSTINIT``
        or ``SHUTDOWN``. Defaults to ``POSTINIT``.

    enabled
        Whether the entity should be enabled. Defaults to true.

    timeout
        The timeout when running the entity.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The init/shutdown script is in the correct state",
        "changes": {},
    }
    try:
        curr = _find_iss(name)
        verb = "update"
        if curr is not None:
            args = _args(
                data=data, typ=typ, when=when, enabled=enabled, timeout=timeout
            )
            for param, val in args.items():
                if val is not None and curr[param] != val:
                    ret["changes"][param] = {"old": curr[param], "new": val}
        else:
            ret["changes"]["created"] = name
            verb = "create"
        if not ret["changes"]:
            return ret
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"Would have {verb}d the init/shutdown script"
            return ret
        if curr:
            __salt__["truenas_isscript.update"](
                name, data=data, typ=typ, when=when, enabled=enabled, timeout=timeout
            )
        else:
            __salt__["truenas_isscript.create"](
                data, typ=typ, when=when, comment=name, enabled=enabled, timeout=timeout
            )
    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def absent(name):
    """
    Ensure a TrueNAS init/shutdown script is absent.

    name
        The comment. We need something to track entities. Could use ``data`` if
        we were disallowing script text.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The init/shutdown script is in the correct state",
        "changes": {},
    }
    try:
        curr = _find_iss(name)
        if curr is None:
            return ret
        ret["changes"]["deleted"] = curr["name"]
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "Would have deleted the init/shutdown script"
            return ret
        __salt__["truenas_isscript.delete"](id=curr["id"])
        ret["comment"] = "Deleted the init/shutdown script"
    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def _find_iss(name):
    for iss in __salt__["truenas_isscript.list"]():
        if name.lower() in iss["comment"].lower():
            return iss


def _args(data=None, typ=None, when=None, comment=None, enabled=None, timeout=None):
    args = {}
    if data is not None:
        if typ == "COMMAND":
            data_dst = "command"
        else:
            if Path(data).exists():
                data_dst = "script"
            else:
                data_dst = "script_text"
        args[data_dst] = data
    if typ is not None:
        args["type"] = typ
    if when is not None:
        args["when"] = when
    if enabled is not None:
        args["enabled"] = enabled
    if comment is not None:
        args["comment"] = comment
    if timeout is not None:
        args["timeout"] = timeout
    return args
