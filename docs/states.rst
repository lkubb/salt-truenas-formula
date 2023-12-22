Available states
----------------

The following states are found in this formula:

.. contents::
   :local:


``truenas``
^^^^^^^^^^^
A collection of states to manage some aspects of TrueNAS.
You will have to target each mod explicitly, just ``truenas``
does nothing.


``truenas.certs``
^^^^^^^^^^^^^^^^^
Manages certificates that will be imported into the certificate store.

When using a ``ca_server``, will rely on the SSH wrapper emulation
of ``x509.certificate_managed`` since the remote does not have access
to the event bus.

The wrapper is found in my PR #65654 or in my formula for a private CA:
https://github.com/lkubb/salt-private-ca-formula


``truenas.minio``
^^^^^^^^^^^^^^^^^
Manages the MinIO plugin.

Currently only manages a certificate.


``truenas.minio.cert``
^^^^^^^^^^^^^^^^^^^^^^
Manages a certificate for the MinIO plugin.

The jail must exist for this state to work at all.


``truenas.sshd``
^^^^^^^^^^^^^^^^
Manages the SSH service.


``truenas.sshd.authorized_keys``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Manages OpenSSH authorized keys.
If ``TrustedUserCAKeys`` has been specified in the server
configuration (``truenas:sshd:config``), all CA keys from
``truenas:sshd:trusted_user_ca_keys`` will be serialized
into the corresponding file as well.


``truenas.sshd.config``
^^^^^^^^^^^^^^^^^^^^^^^
Manages SSH configuration. TrueNAS automatically reloads the
config, so this is mostly standalone. It still depends on
`truenas.sshd.host_pki`_ since those should be managed before.


``truenas.sshd.host_pki``
^^^^^^^^^^^^^^^^^^^^^^^^^
Manages SSH host keys and other related files.


``truenas.sshd.service``
^^^^^^^^^^^^^^^^^^^^^^^^
Ensures SSH service is enabled and running.
No config since SSH is required for any of this to work.


``truenas.telegraf``
^^^^^^^^^^^^^^^^^^^^
Installs Telegraf and manages configuration.

You need to set ``truenas:telegraf:destination``.
It is advised to install it on a dataset to avoid it being
removed during an update.


``truenas.certs.clean``
^^^^^^^^^^^^^^^^^^^^^^^
Does not remove the certificates/keys because this is hard
to automate and can break a lot of things.
You will need to do this manually.


``truenas.sshd.authorized_keys.clean``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Removes managed OpenSSH authorized keys and trusted user CA keys.


``truenas.telegraf.clean``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Removes Telegraf and configuration.


