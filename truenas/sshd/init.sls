# vim: ft=sls

{#-
    Manages the SSH service.
#}

include:
  - .authorized_keys
  - .host_pki
  - .config
  - .service
