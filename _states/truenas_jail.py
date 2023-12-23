"""
Manage TrueNAS jails.
"""
import logging
import time

from salt.exceptions import CommandExecutionError, SaltInvocationError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_jail"


def __virtual__():
    try:
        __salt__["truenas_jail.list"]
    except KeyError:
        return False, "`truenas_jail` execution module not found"
    return __virtualname__


def running(name, timeout=30):
    """
    Ensure a jail is running.

    name
        The name (``id`` field) of the jail.

    timeout
        This state checks whether the jail was started successfully. Specify
        the maximum wait time in seconds. Defaults to 30.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The jail is already running",
        "changes": {},
    }
    try:
        try:
            state = __salt__["truenas_jail.is_running"](name)
        except CommandExecutionError as err:
            if "No such jail" not in str(err) or not __opts__["test"]:
                raise
            ret["result"] = None
            ret["comment"] = (
                str(err)
                + ". If the jail is created before, you can ignore this message"
            )
            return ret
        if state:
            return ret
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "The jail is set to be started"
            ret["changes"]["started"] = name
            return ret

        __salt__["truenas_jail.start"](name)
        start_time = time.time()

        while not __salt__["truenas_jail.is_running"](
            name,
        ):
            if time.time() - start_time > timeout:
                ret["result"] = False
                ret["comment"] = "Tried to start the jail, but it is still not running."
                ret["changes"] = {}
                return ret
            time.sleep(0.25)

        ret["comment"] = "The jail was started"
        ret["changes"]["started"] = name

    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def dead(name, force=False, timeout=30):
    """
    Ensure a jail is stopped.

    name
        The name (``id`` field) of the jail.

    force
        Force stopping the jail. Defaults to false.

    timeout
        This state checks whether the jail was stopped successfully. Specify
        the maximum wait time in seconds. Defaults to 30.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The jail is already dead",
        "changes": {},
    }
    try:
        try:
            state = __salt__["truenas_jail.is_dead"](name)
        except CommandExecutionError as err:
            if "No such jail" not in str(err) or not __opts__["test"]:
                raise
            ret["result"] = None
            ret["comment"] = (
                str(err)
                + ". If the jail is created before, you can ignore this message"
            )
            return ret
        if state:
            return ret
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "The jail is set to be stopped"
            ret["changes"]["stopped"] = name
            return ret

        __salt__["truenas_jail.stop"](name)
        start_time = time.time()

        while not __salt__["truenas_jail.is_dead"](
            name,
        ):
            if time.time() - start_time > timeout:
                break
            time.sleep(0.25)
        else:
            ret["comment"] = "The jail was stopped"
            ret["changes"]["stopped"] = name
            return ret
        if force:
            __salt__["truenas_jail.stop"](name, force=True)
            while not __salt__["truenas_jail.is_dead"](
                name,
            ):
                if time.time() - start_time > timeout:
                    ret["result"] = False
                    ret[
                        "comment"
                    ] = "Tried to force-stop the jail, but it is still not dead."
                    ret["changes"] = {}
                    return ret
                time.sleep(0.25)
            ret["comment"] = "The jail was force-stopped."
            ret["changes"] = {"stopped": name, "forced": True}
        else:
            ret["result"] = False
            ret["comment"] = "Tried to stop the jail, but it is still not dead."
            ret["changes"] = {}

    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def absent(name, force=False):
    """
    Ensure a jail is not present.

    name
        The name (``id`` field) of the jail.

    force
        Force deletion. Defaults to false.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The jail is already absent",
        "changes": {},
    }
    try:
        if not __salt__["truenas_jail.exists"](name):
            return ret
        ret["changes"]["deleted"] = name
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "The jail would have been deleted"
            return ret
        __salt__["truenas_jail.delete"](name, force=force)
        if __salt__["truenas_jail.exists"](name):
            raise CommandExecutionError("Tried deleting the jail, but it still exists")
        ret["comment"] = "Deleted the jail"

    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def mod_watch(name, sfun=None, **kwargs):
    """
    Support the ``watch`` requisite for ``truenas_jail.running`` and ``truenas_jail.dead``.
    """
    ret = {"name": name, "changes": {}, "result": True, "comment": ""}
    pp_suffix = "ed"

    try:
        if sfun in ["dead", "running"]:
            if sfun == "dead":
                verb = "stop"
                pp_suffix = "ped"

                if __salt__["truenas_jail.is_running"](name):
                    func = __salt__["truenas_jail.stop"]
                    check_func = __salt__["truenas_jail.is_dead"]
                else:
                    ret["comment"] = "Jail is already stopped."
                    return ret

            # "running" == sfun evidently
            else:
                check_func = __salt__["truenas_jail.is_running"]
                if __salt__["truenas_jail.is_running"](name):
                    verb = "restart"
                    func = __salt__["truenas_jail.restart"]
                else:
                    verb = "start"
                    func = __salt__["truenas_jail.start"]

        else:
            ret["comment"] = f"Unable to trigger watch for truenas_jail.{sfun}"
            ret["result"] = False
            return ret

        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"Jail is set to be {verb}{pp_suffix}."
            ret["changes"][verb + pp_suffix] = name
            return ret

        func(name)

        timeout = kwargs.get("timeout", 10)
        start_time = time.time()

        while not check_func(name):
            if time.time() - start_time > timeout:
                ret["result"] = False
                ret[
                    "comment"
                ] = f"Tried to {verb} the jail, but it is still not {sfun}."
                ret["changes"] = {}
                return ret
            time.sleep(0.25)

    except (CommandExecutionError, SaltInvocationError) as e:
        ret["result"] = False
        ret["comment"] = str(e)
        return ret

    ret["comment"] = f"Jail was {verb}{pp_suffix}."
    ret["changes"][verb + pp_suffix] = name

    return ret
