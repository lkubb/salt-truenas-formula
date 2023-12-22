"""
Report TrueNAS-specific data.

Inspired by https://github.com/arensb/ansible-truenas
"""
import salt.utils.path
import truenasutils as tn

__virtualname__ = "truenas"


def __virtual__():
    # __salt__ is not defined here, so check like this
    if salt.utils.path.which("midclt"):
        return __virtualname__
    return False, "Does not seem to be TrueNAS"


def truenas_info():
    with tn.get_client(__opts__, __context__) as client:
        # TrueNAS
        product_name = client.call("system.product_name")
        # CORE/SCALE...
        product_type = client.call("system.product_type")
        # TrueNAS-(SCALE)?-13.0-U6
        version = client.call("system.version")

    if version.startswith(f"{product_name}-"):
        version = version[len(product_name) + 1 :]
    if version.startswith(f"{product_type}-"):
        version = version[len(product_type) + 1 :]
    # 13.0-U6
    parsed_version, *rev = version.split("-")
    if rev:
        rev = rev[0]
        rev = rev.lstrip("U")
        parsed_version += f".{rev}"
    parsed_version = tuple(int(x) for x in parsed_version.split("."))

    return {
        "truenas_product_name": product_name,
        "truenas_product_type": product_type,
        "truenas_version_str": version,
        "truenas_osrelease_info": parsed_version,
        "truenas_osmajorrelease": parsed_version[0],
        "truenas_osrelease": ".".join(str(x) for x in parsed_version[:2]),
    }
