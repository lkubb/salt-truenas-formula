# vim: ft=sls

{#-
    Manages certificates that will be imported into the certificate store.

    When using a ``ca_server``, will rely on the SSH wrapper emulation
    of ``x509.certificate_managed`` since the remote does not have access
    to the event bus.

    The wrapper is found in my PR #65654 or in my formula for a private CA:
    https://github.com/lkubb/salt-private-ca-formula
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}

{%- for cert in truenas.certs %}
{%-   if not cert.name %}
{%-     do salt["log.warning"]("Skipping unnamed certificate in trunas:certs") %}
{%-     continue %}
{%-   endif %}
{%- set crt_file = truenas.lookup.certs.workdir | path_join(cert.name ~ ".crt") %}
{%- set key_file = truenas.lookup.certs.workdir | path_join(cert.name ~ ".key") %}
{%-   if cert.ca_server %}
{%-     set pk_managed = cert.private_key_managed %}
{%-     do pk_managed.update({"name": key_file, "makedirs": true}) %}
{{
    salt["x509.certificate_managed_wrapper"](
      crt_file,
      ca_server=cert.ca_server,
      signing_policy=cert.signing_policy,
      private_key_managed=pk_managed,
      certificate_managed=cert.certificate_managed,
      test=opts.get("test")
    ) | yaml(false)
}}

{%-   else %}

{{ key_file }}_key:
  x509.private_key_managed:
    - name: {{ key_file }}
    {{ cert.private_key_managed | dict_to_sls_yaml_params | indent(4) }}
{%-     if cert.private_key_managed.get("new") and salt["file.file_exists"](key_file) %}
    - prereq:
      - {{ crt_file }}_crt
{%-     endif %}
    - makedirs: true
    - user: root
    - group: unifi
    - mode: '0640'

{{ crt_file }}_crt:
  x509.certificate_managed:
    - name: {{ crt_file }}
    - signing_policy: {{ cert.signing_policy or "null" }}
    - private_key: {{ key_file }}
    {{ cert.certificate_managed | dict_to_sls_yaml_params | indent(4) }}
{%-     if "signing_private_key" not in cert.certificate_managed %}
    # This will be a self-signed certificate
    - signing_private_key: {{ key_file }}
{%-     endif %}
    - mode: '0640'
    - user: root
    - group: unifi
    - makedirs: true
{%-     if not cert.private_key_managed.get("new") or not salt["file.file_exists"](key_file) %}
    - require:
      - {{ key_file }}_key
{%-     endif %}
{%-   endif %}

Certificate {{ cert.name }} is imported in TrueNAS:
  truenas_cert.imported:
    - name: {{ cert.name }}
    - certificate: {{ crt_file }}
    - private_key: {{ key_file }}
    - require:
      - x509: {{ crt_file }}
      - x509: {{ key_file }}

{%-   if cert.services %}

Latest certificate {{ cert.name }} is active:
  truenas_cert.active:
    - names: {{ cert.services | json }}
    - certificate_name: {{ cert.name }}
    - require:
      - Certificate {{ cert.name }} is imported in TrueNAS
{%-   endif %}
{%- endfor %}
