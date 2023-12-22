# vim: ft=sls

{#-
    Manages SSH host keys and other related files.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}
{%- from tplroot ~ "/libsaltcli.jinja" import cli with context %}

{%- set managed_keys = [] %}
{%- set managed_certs = [] %}
{%- for key_type, config in truenas.sshd["keys"].items() %}
{%-   if not config.get("manage", True) %}
{%-     continue %}
{%-   endif %}
{%-   set filename = truenas.lookup.sshd.config | path_join("ssh_host_" ~ key_type ~ "_key") %}
{%-   if not config.get("present", True) %}

OpenSSH {{ key_type }} host key is absent:
  file.absent:
    - names:
      - {{ filename }}
      - {{ filename }}.pub
      - {{ filename }}.crt
{%-     continue %}
{%-   endif %}
{%-   do managed_keys.append(filename) %}
{%-   set algo_type = key_type if key_type != "ecdsa" else "ec" %}
{%-   set pk_params = {
        "name": filename,
        "algo": algo_type,
        "keysize": config.get("key_size"),
        "user": "root",
        "group": truenas.lookup.rootgroup,
        "mode": "0600",
        "new": config.get("cert") and config.get("rotate", true) | to_bool
      }
%}
{%-   if cli in ["ssh", "unknown"] and config.get("cert") and truenas.sshd.cert_params.ca_server %}
{%-     do managed_certs.append(filename) %}
{%-     set cert_params = {} %}
{%-     for param, val in truenas.sshd.cert_params.items() %}
{%-       if param not in ["ca_server", "backend", "backend_args", "signing_policy"] %}
{%-         do cert_params.update({param: val}) %}
{%-       endif %}
{%-     endfor %}
{%-     do cert_params.update({
          "cert_type": "host",
          "user": "root",
          "group": truenas.lookup.rootgroup
        })
%}

{{
    salt["ssh_pki.certificate_managed_wrapper"](
        filename ~ ".crt",
        ca_server=truenas.sshd.cert_params.ca_server,
        signing_policy=truenas.sshd.cert_params.signing_policy,
        backend=truenas.sshd.cert_params.backend,
        backend_args=truenas.sshd.cert_params.backend_args,
        private_key_managed=pk_params,
        certificate_managed=cert_params,
        test=opts.get("test")
    ) | yaml(false)
}}
{%-   else %}

OpenSSH {{ key_type }} host key is present:
  ssh_pki.private_key_managed:
    {{ pk_params | dict_to_sls_yaml_params | indent(4) }}
{%-     if config.get("cert") %}
{%-       do managed_certs.append(filename) %}
{%-       if salt["file.file_exists"](filename) is true %}
    # prereq_in complains about "Cannot extend ID"
    - prereq:
      - ssh_pki: {{ filename }}.pub
{%-       endif %}

OpenSSH {{ key_type }} host certificate is present:
  ssh_pki.certificate_managed:
    - name: {{ filename }}.crt
    - cert_type: host
    - user: root
    - private_key: {{ filename }}
    - group: {{ truenas.lookup.rootgroup }}
{%-       for param, val in truenas.sshd.cert_params.items() %}
    - {{ param }}: {{ val | json }}
{%-       endfor %}
{%-       if salt["file.file_exists"](filename) is false %}
    - require:
      - ssh_pki: {{ filename }}
{%-       endif %}
{%-     endif %}
{%-   endif %}

OpenSSH {{ key_type }} host pubkey is present:
  ssh_pki.public_key_managed:
    - name: {{ filename }}.pub
    - public_key_source: {{ filename }}
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - require:
      - ssh_pki: {{ filename }}
{%- endfor %}

{%- if managed_keys %}

OpenSSH host keys are persisted to the database:
  module.run:
    - truenas.call:
      - ssh.save_keys
    - onchanges:
{%-   for key in managed_keys %}
      - ssh_pki: {{ key }}
      - ssh_pki: {{ key }}.pub
{%-     if key in managed_certs %}
      - ssh_pki: {{ key }}.crt
{%-     endif %}
{%-   endfor %}
{%- endif %}
