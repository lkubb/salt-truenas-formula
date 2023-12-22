from salt.exceptions import CommandExecutionError

try:
    import middlewared.client

    HAS_PYTHON_CLIENT = True

except ImportError:
    HAS_PYTHON_CLIENT = False

CKEY = "_truenas_client"


class TrueNASMiddlewaredClient:
    def __init__(self, client=None):
        if client is None:
            client = middlewared.client.Client()
        self.client = client

    def call(self, func, *args, timeout=None):
        """
        Call a TrueNAS middleware service.
        """
        return self._call(func, args, timeout=timeout)

    def job(self, func, *args, timeout=None, callback=None):
        """
        Some API calls are jobs.
        """
        kwargs = {
            "job": True,
            "callback": callback,
        }
        return self._call(func, args, timeout=timeout, **kwargs)

    def _call(self, func, args, timeout=None, **kwargs):
        if timeout is not None:
            kwargs["timeout"] = timeout
        return self.client.call(func, *args, **kwargs)

    def __enter__(self):
        self.client.__enter__()
        return self

    def __exit__(self, typ, value, traceback):
        self.client.__exit__(typ, value, traceback)
        return


# More clients could be added - midclt or REST


def get_client(opts, context):
    """
    Return a TrueNAS client.

    This can support multiple implementations, but currently only
    the Python middlewared client is ready.
    """
    # The client object cannot be reused after it's closed -
    # would need to do something like in the InfluxDB returner
    # if CKEY in context:
    #     return context[CKEY]
    client = None
    if HAS_PYTHON_CLIENT:
        client = TrueNASMiddlewaredClient()
    if client is not None:
        # context[CKEY] = client
        return client
    raise CommandExecutionError("Could not load TrueNAS client")
