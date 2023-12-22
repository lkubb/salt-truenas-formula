"""
Operate on the TrueNAS certificate store.
"""
import logging

import salt.utils.path
import truenasutils as tn
from salt.exceptions import CommandExecutionError

log = logging.getLogger(__name__)

__virtualname__ = "truenas_cert"
__func_alias__ = {
    "import_": "import",
    "list_": "list",
}


def __virtual__():
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def list_(name_prefix=None, order_by="name", include_private_key=False):
    """
    List (all) present certificates and their keys.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_cert.list

    include_private_key
        Include the private key contents. Defaults to false.
    """
    filters = []
    # ensure we don't get paged results
    options = {"limit": 0}
    if name_prefix:
        filters.append(["name", "~", name_prefix])
    if order_by:
        if not isinstance(order_by, list):
            order_by = [order_by]
        options["order_by"] = [str(x) for x in order_by]
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("certificate.query", filters, options)
    if not include_private_key:
        for cert in res:
            # Don't leak private keys by default
            cert.pop("privatekey", None)
    return res


def import_(name, certificate, private_key, append_certs=None):
    """
    Import a certificate.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_cert.import my-custom-cert /opt/ssl/my-cert.crt /opt/ssl/my-cert.key

    name
        The name for the imported certificate.

    certificate
        The certificate to import.
        Parameter for ``x509.encode_certificate`` (in short: path or contents).

    private_key
        The private key corresponding to the certificate.
        Parameter for ``x509.encode_private_key`` (in short: path or contents).

    append_certs
        A list of certificates to append to the imported one (certificate chain).
        Parameter for ``x509.encode_certificate`` (in short: list of paths or contents).
    """
    certificate = __salt__["x509.encode_certificate"](
        certificate, append_certs=append_certs, encoding="pem"
    )
    private_key = __salt__["x509.encode_private_key"](private_key, encoding="pem")
    payload = {
        "create_type": "CERTIFICATE_CREATE_IMPORTED",
        "name": name,
        "certificate": certificate,
        "privatekey": private_key,
    }
    with tn.get_client(__opts__, __context__) as client:
        return client.job("certificate.create", payload)


def delete(name):
    """
    Delete a certificate.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_cert.delete my-old-cert

    name
        The name of the certificate.
    """
    with tn.get_client(__opts__, __context__) as client:
        res = client.call("certificate.query", [["name", "=", name]])
        if not res:
            raise CommandExecutionError(f"Could not find a certificate named '{name}'.")
        cert = res[0]
        return client.job("certificate.delete", cert["id"])


def clean():
    """
    Remove expired certificates.

    CLI Example:

    .. code-block:: bash

        salt-ssh '*' truenas_cert.clean
    """
    certs = list_()
    remove = []
    for cert in certs:
        if __salt__["x509.expired"](cert["certificate"]):
            remove.append(cert["id"])
    with tn.get_client(__opts__, __context__) as client:
        for rm in remove:
            client.job("certificate.delete", rm)
    return remove
