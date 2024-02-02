"""
Manage certificates in the key store and activate them on services.
"""
import logging
import time

from salt.exceptions import CommandExecutionError, SaltInvocationError
from salt.utils.immutabletypes import freeze

log = logging.getLogger(__name__)

__virtualname__ = "truenas_cert"


CERT_CONFIGS = freeze(
    {
        "ftp": "ssltls_certificate",
        "ldap": "certificate",
        "openvpn.client": "client_certificate",
        "openvpn.server": "server_certificate",
        "s3": "certificate",
        "system.advanced": "syslog_tls_certificate",
        "system.general": "ui_certificate",
        "webdav": "certssl",
    }
)


def __virtual__():
    try:
        __salt__["truenas_cert.list"]
    except KeyError:
        return False, "`truenas_cert` execution module not found"
    return __virtualname__


def imported(name, certificate, private_key, append_certs=None, clean=True):
    """
    Ensure a certificate has been imported.
    This appends the current timestamp to the name on changes
    since we need to operate atomically.

    name
        The name prefix of the certificate. The actual name will be
        suffixed with a timestamp.

    certificate
        The certificate to import.
        Parameter for ``x509.encode_certificate`` (in short: path or contents).

    private_key
        The private key corresponding to the certificate.
        Parameter for ``x509.encode_private_key`` (in short: path or contents).

    append_certs
        A list of certificates to append to the imported one (certificate chain).
        Note that even if the file you want to import contains them, you will need
        to specify them here as well.
        Parameter for ``x509.encode_certificate`` (in short: list of paths or contents).

    clean
        Remove expired certificate with the same name prefix.
        Defaults to true.
    """

    def list_expired(certs):
        expired = []
        for cert in certs:
            if __salt__["x509.expires"](cert["certificate"]):
                expired.append(cert["name"])
        return expired

    ret = {
        "name": name,
        "result": True,
        "comment": "The certificate has already been imported",
        "changes": {},
    }
    expired = []
    try:
        try:
            wanted = __salt__["x509.encode_certificate"](
                certificate, append_certs=append_certs
            )
        except SaltInvocationError as err:
            if "Could not load provided source" not in str(err):
                raise
            if not __opts__["test"]:
                raise
            ret["result"] = None
            ret[
                "comment"
            ] = "Could not load the certificate. If it's a path and created before, you can ignore this message."
            return ret
        actual_name = f"{name}-{int(time.time())}"
        certs = __salt__["truenas_cert.list"](name, order_by="name")
        if certs:
            curr = certs[-1]
            if wanted == curr["certificate"]:
                return ret
            verb = "reimport"
        else:
            verb = "import"
        ret["changes"][f"{verb}ed"] = actual_name
        if clean:
            expired = list_expired(certs)
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = f"The certificate would have been {verb}ed"
            if expired:
                ret["changes"]["cleaned"] = expired
            return ret
        __salt__["truenas_cert.import"](
            actual_name, certificate, private_key, append_certs=append_certs
        )
        # Give it some time
        time.sleep(5)
        new = __salt__["truenas_cert.list"](actual_name)
        if not new:
            raise CommandExecutionError(
                "No errors during import, but the certificate was not listed as present"
            )
        if new[-1]["certificate"] != wanted:
            log.debug(f"Wanted:\n{wanted}\nActual:\n{new[-1]['certificate']}")
            raise CommandExecutionError(
                "Certificate was imported, but it did not match what was expected"
            )
        ret["comment"] = f"The certificate has been {verb}ed"
        failed = {}
        for cert in expired:
            try:
                __salt__["truenas_cert.delete"](cert)
            except Exception as err:  # pylint: disable=broad-except
                log.error(str(err))
                failed[cert] = str(err)
        if failed:
            # We don't want to fail this state since the import worked
            for cert, reason in failed.items():
                ret["comment"] += "\n" + f"Error for '{cert}': {reason}"
    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret


def active(name, certificate_name):
    """
    Ensure the latest named certificate is active for a service.

    name
        The name of the scope where it should be active.

    certificate_name
        The name of the certificate that was passed to ``truenas_cert.imported``.
        The latest iteration will be selected.
    """
    ret = {
        "name": name,
        "result": True,
        "comment": "The certificate is already active",
        "changes": {},
    }
    try:
        if name not in CERT_CONFIGS:
            raise SaltInvocationError(
                f"Cannot manage service '{name}'. Allowed: {', '.join(CERT_CONFIGS)}"
            )
        cert_config = CERT_CONFIGS[name]
        certs = __salt__["truenas_cert.list"](certificate_name, order_by="name")
        if not certs:
            err_msg = (
                f"Did not find a certificate with name prefix '{certificate_name}'"
            )
            if __opts__["test"]:
                ret["result"] = None
                ret[
                    "comment"
                ] = f"{err_msg}. If the certificate is imported before, you can ignore this message"
                return ret
            raise CommandExecutionError(err_msg)
        curr = certs[-1]
        curr_config = __salt__["truenas_service.get_config"](name)[cert_config]
        if curr_config["id"] == curr["id"]:
            return ret
        ret["changes"] = {"old": curr_config["name"], "new": curr["name"]}
        if __opts__["test"]:
            ret["result"] = None
            ret["comment"] = "Would have updated the certificate config"
            return ret
        kwarg = {cert_config: curr["id"]}
        __salt__["truenas_service.update_config"](name, **kwarg)
        ret["comment"] = "Updated the certificate config"
        if name == "system.general":
            # Restart UI on changes - other services might need this also
            try:
                __salt__["truenas.call"]("system.general.ui_restart")
            except Exception as err:
                ret["result"] = False
                ret["comment"] += f". Failed restarting UI: {err}"
            else:
                ret["changes"]["restarted"] = name
    except (CommandExecutionError, SaltInvocationError) as err:
        ret["result"] = False
        ret["comment"] = str(err)
        ret["changes"] = {}
    return ret
