# vim: ft=sls

{#-
    Manages OpenSSH authorized keys.
    If ``TrustedUserCAKeys`` has been specified in the server
    configuration (``truenas:sshd:config``), all CA keys from
    ``truenas:sshd:trusted_user_ca_keys`` will be serialized
    into the corresponding file as well.
#}

include:
  - .manage
