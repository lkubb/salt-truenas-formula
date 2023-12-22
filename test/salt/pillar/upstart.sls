# vim: ft=yaml
---
truenas:
  lookup:
    master: template-master
    # Just for testing purposes
    winner: lookup
    added_in_lookup: lookup_value
    certs:
      workdir: /opt/certs
    sshd:
      config: /usr/local/etc/ssh
    telegraf:
      rcfile: /usr/local/etc/rc.d/telegraf
      source: https://dl.influxdata.com/telegraf/releases/telegraf-{release}_freebsd_amd64.tar.gz  # yamllint disable-line rule:line-length
  certs:
    - ca_server: null
      certificate_managed:
        authorityKeyIdentifier: keyid:always
        basicConstraints: critical, CA:false
        days_remaining: 7
        days_valid: 30
        subjectKeyIdentifier: hash
      name: ''
      private_key_managed:
        algo: rsa
        keysize: 3072
        new: true
      services: []
      signing_policy: null
  minio:
    cert:
      ca_server: null
      certificate_managed:
        authorityKeyIdentifier: keyid:always
        basicConstraints: critical, CA:false
        days_remaining: 7
        days_valid: 30
        subjectKeyIdentifier: hash
      private_key_managed:
        algo: rsa
        keysize: 3072
        new: true
      signing_policy: null
    jail_name: minio
  sshd:
    authorized_keys: {}
    authorized_principals: {}
    cert_params:
      all_principals: false
      backend: null
      backend_args: null
      ca_server: null
      signing_policy: null
      ttl: null
      ttl_remaining: null
      valid_principals: null
    config: {}
    config_truenas: {}
    keys:
      dsa:
        manage: true
        present: false
      ecdsa:
        manage: true
        present: true
      ed25519:
        manage: true
        present: true
      rsa:
        keysize: 2048
        manage: true
        present: true
    trusted_user_ca_keys: []
  telegraf:
    config: {}
    dest: null
    source_hash: a0748d1a3859602b7b23ff098e9119f75c4c20f3fda4b0c4a47550a7fd975ac1
    tls_ca: null
    version: 1.29.1

  tofs:
    # The files_switch key serves as a selector for alternative
    # directories under the formula files directory. See TOFS pattern
    # doc for more info.
    # Note: Any value not evaluated by `config.get` will be used literally.
    # This can be used to set custom paths, as many levels deep as required.
    files_switch:
      - any/path/can/be/used/here
      - id
      - roles
      - osfinger
      - os
      - os_family
    # All aspects of path/file resolution are customisable using the options below.
    # This is unnecessary in most cases; there are sensible defaults.
    # Default path: salt://< path_prefix >/< dirs.files >/< dirs.default >
    #         I.e.: salt://truenas/files/default
    # path_prefix: template_alt
    # dirs:
    #   files: files_alt
    #   default: default_alt
    # The entries under `source_files` are prepended to the default source files
    # given for the state
    # source_files:
    #   truenas-config-file-file-managed:
    #     - 'example_alt.tmpl'
    #     - 'example_alt.tmpl.jinja'

    # For testing purposes
    source_files:
      truenas-config-file-file-managed:
        - 'example.tmpl.jinja'

  # Just for testing purposes
  winner: pillar
  added_in_pillar: pillar_value
