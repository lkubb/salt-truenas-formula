.. _readme:

TrueNAS Formula
===============

|img_sr| |img_pc|

.. |img_sr| image:: https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg
   :alt: Semantic Release
   :scale: 100%
   :target: https://github.com/semantic-release/semantic-release
.. |img_pc| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :alt: pre-commit
   :scale: 100%
   :target: https://github.com/pre-commit/pre-commit

Manage TrueNAS with Salt.

This is a collection of states intended to be run over Salt-SSH.

.. contents:: **Table of Contents**
   :depth: 1

General notes
-------------

See the full `SaltStack Formulas installation and usage instructions
<https://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html>`_.

If you are interested in writing or contributing to formulas, please pay attention to the `Writing Formula Section
<https://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html#writing-formulas>`_.

If you want to use this formula, please pay attention to the ``FORMULA`` file and/or ``git tag``,
which contains the currently released version. This formula is versioned according to `Semantic Versioning <http://semver.org/>`_.

See `Formula Versioning Section <https://docs.saltstack.com/en/latest/topics/development/conventions/formulas.html#versioning>`_ for more details.

If you need (non-default) configuration, please refer to:

- `how to configure the formula with map.jinja <map.jinja.rst>`_
- the ``pillar.example`` file
- the `Special notes`_ section

Special notes
-------------


Configuration
-------------
An example pillar is provided, please see `pillar.example`. Note that you do not need to specify everything by pillar. Often, it's much easier and less resource-heavy to use the ``parameters/<grain>/<value>.yaml`` files for non-sensitive settings. The underlying logic is explained in `map.jinja`.


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



Contributing to this repo
-------------------------

Commit messages
^^^^^^^^^^^^^^^

**Commit message formatting is significant!**

Please see `How to contribute <https://github.com/saltstack-formulas/.github/blob/master/CONTRIBUTING.rst>`_ for more details.

pre-commit
^^^^^^^^^^

`pre-commit <https://pre-commit.com/>`_ is configured for this formula, which you may optionally use to ease the steps involved in submitting your changes.
First install  the ``pre-commit`` package manager using the appropriate `method <https://pre-commit.com/#installation>`_, then run ``bin/install-hooks`` and
now ``pre-commit`` will run automatically on each ``git commit``. ::

  $ bin/install-hooks
  pre-commit installed at .git/hooks/pre-commit
  pre-commit installed at .git/hooks/commit-msg

State documentation
~~~~~~~~~~~~~~~~~~~
There is a script that semi-autodocuments available states: ``bin/slsdoc``.

If a ``.sls`` file begins with a Jinja comment, it will dump that into the docs. It can be configured differently depending on the formula. See the script source code for details currently.

This means if you feel a state should be documented, make sure to write a comment explaining it.

Testing
-------

Linux testing is done with ``kitchen-salt``.

Requirements
^^^^^^^^^^^^

* Ruby
* Docker

.. code-block:: bash

   $ gem install bundler
   $ bundle install
   $ bin/kitchen test [platform]

Where ``[platform]`` is the platform name defined in ``kitchen.yml``,
e.g. ``debian-9-2019-2-py3``.

``bin/kitchen converge``
^^^^^^^^^^^^^^^^^^^^^^^^

Creates the docker instance and runs the ``truenas`` main state, ready for testing.

``bin/kitchen verify``
^^^^^^^^^^^^^^^^^^^^^^

Runs the ``inspec`` tests on the actual instance.

``bin/kitchen destroy``
^^^^^^^^^^^^^^^^^^^^^^^

Removes the docker instance.

``bin/kitchen test``
^^^^^^^^^^^^^^^^^^^^

Runs all of the stages above in one go: i.e. ``destroy`` + ``converge`` + ``verify`` + ``destroy``.

``bin/kitchen login``
^^^^^^^^^^^^^^^^^^^^^

Gives you SSH access to the instance for manual testing.
