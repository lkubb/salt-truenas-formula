"""
Manage TrueNAS service configuration.
"""
import json
import logging

from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_service"


def __virtual__():
    try:
        __salt__["truenas_service.get_all"]
    except KeyError:
        return False, "Did not find truenas_service execution module"
    return __virtualname__


def configured(name, **kwargs):
    """
    Ensure a TrueNAS service configuration is set as specified.
    """

    def check_changes(old):
        changes = {}
        for param, val in kwargs.items():
            if param not in old:
                raise SaltInvocationError(
                    f"Invalid parameter '{param}' for service '{name}'. Available: {', '.join(old)}"
                )
            if old[param] != val:
                changes[param] = {"old": old[param], "new": val}
        return changes

    ret = {
        "name": name,
        "result": True,
        "comment": "The service is already configured as specified",
        "changes": {},
    }
    try:
        if not __salt__["truenas_service.available"](name):
            raise SaltInvocationError(f"Unknown service: {name}")
        curr = __salt__["truenas_service.get_config"](name)
        changes = check_changes(curr)
        if not changes:
            return ret
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "Would have updated the service configuration"
            ret["changes"] = changes
            return ret
        __salt__["truenas_service.update_config"](name, **kwargs)
        new = __salt__["truenas_service.get_config"](name)
        new_changes = check_changes(new)
        if new_changes:
            ret["result"] = False
            ret[
                "comment"
            ] = f"Updated the service configuration, but it is still not as expected. Differences: {json.dumps(changes)}"
            ret["changes"] = {k: v for k, v in changes.items() if k not in new_changes}
        else:
            ret["comment"] = "Updated the service configuration"
            ret["changes"] = changes
    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
    return ret
