"""
Interface for Init/Shutdown Scripts
"""
import logging
from pathlib import Path

import salt.utils.path
import truenasutils as tn
from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_isscript"
__func_alias__ = {
    "list_": "list",
}

TYPES = ("COMMAND", "SCRIPT")
WHENS = ("PREINIT", "POSTINIT", "SHUTDOWN")


def __virtual__():
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def list_():
    """
    List scripts.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_isscript.list
    """
    options = {"limit": 0}
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("initshutdownscript.query", [], options)
    return res


def create(
    data, typ="COMMAND", when="POSTINIT", comment=None, enabled=True, timeout=None
):
    """
    Create a script.

    .. code-block:: bash

        salt-ssh '*' truenas_isscript.create 'echo foo' comment='Log dumb notification'

    data
        The data for the script. If ``typ`` is ``COMMAND``, the command to run.
        If ``typ`` is ``SCRIPT``, the path of the script or the script text to run.

    typ
        The type to create. ``COMMAND`` or ``SCRIPT``. Defaults to ``COMMAND``.

    when
        When the script should be run. Valid: ``PREINIT``, ``POSTINIT``, ``SHUTDOWN``.
        Defaults to ``POSTINIT``.

    comment
        A comment describing the script. This comment is used to track scripts
        in the ``truenas_isscript`` modules. Optional.

    enabled
        Whether the script should be enabled after creation. Defaults to true.

    timeout
        The timeout for the script. Optional.
    """
    typ, when = typ.upper(), when.upper()
    if typ not in TYPES:
        raise SaltInvocationError(f"Unknown type: '{typ}'. Valid: {', '.join(TYPES)}")
    if when not in WHENS:
        raise SaltInvocationError(f"Unknown when: '{when}'. Valid: {', '.join(WHENS)}")
    args = _args(
        data, typ=typ, when=when, comment=comment, enabled=enabled, timeout=timeout
    )
    with tn.get_client(__opts__, __context__) as client:
        return client.call("initshutdownscript.create", args)


def update(
    find=None,
    id=None,
    data=None,
    typ=None,
    when=None,
    comment=None,
    enabled=None,
    timeout=None,
):
    """
    Update a script.

    .. code-block:: bash

        salt-ssh '*' truenas_isscript.update 'Log dumb notification' data='echo hey'

    find
        A string that's part of the script's comment. Either this or ``id`` is required.

    id
        The ID of the script to update.

    data
        The data for the script. If ``typ`` is ``COMMAND``, the command to run.
        If ``typ`` is ``SCRIPT``, the path of the script or the script text to run.

    typ
        The type to create. ``COMMAND`` or ``SCRIPT``. Defaults to ``COMMAND``.

    when
        When the script should be run. Valid: ``PREINIT``, ``POSTINIT``, ``SHUTDOWN``.
        Defaults to ``POSTINIT``.

    comment
        A comment describing the script. This comment is used to track scripts
        in the ``truenas_isscript`` modules. Optional.

    enabled
        Whether the script should be enabled after creation. Defaults to true.

    timeout
        The timeout for the script. Optional.
    """
    id = _find_iss(find=find, id=id)
    args = _args(
        data, typ=typ, when=when, comment=comment, enabled=enabled, timeout=timeout
    )
    with tn.get_client(__opts__, __context__) as client:
        return client.call("initshutdownscript.update", id, args)


def delete(find=None, id=None):
    """
    Delete a script.

    .. code-block:: bash

        salt-ssh '*' truenas_isscript.delete 'Log dumb notification'

    find
        A string that's part of the script's comment. Either this or ``id`` is required.

    id
        The ID of the script to update.
    """
    id = _find_iss(find=find, id=id)
    with tn.get_client(__opts__, __context__) as client:
        return client.call("initshutdownscript.delete", id)


def _find_iss(find=None, id=None):
    if find is None and id is None:
        raise SaltInvocationError("Either `find` or `id` is required")
    if find:
        for iss in list_():
            if find.lower() in iss["comment"].lower():
                id = iss["id"]
                break
        else:
            raise CommandExecutionError("Could not find script with specified comment")
    return id


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
