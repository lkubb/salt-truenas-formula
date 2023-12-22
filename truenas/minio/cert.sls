# vim: ft=sls

{#-
    Manages a certificate for the MinIO plugin.

    The jail must exist for this state to work at all.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}
{%- from tplroot ~ "/libtofsstack.jinja" import files_switch with context %}
{%- set iocage = salt["cmd.run"]("iocage get -p") %}
{%- set minio_jail = "/mnt/{}/iocage/jails/{}/root".format(iocage, truenas.minio.jail_name) %}
{%- set minio_certs = minio_jail | path_join("usr", "local", "etc", "minio", "certs") %}
{%- set minio_jid = salt["truenas_jail.list"](truenas.minio.jail_name)[0]["jid"] %}
{%- set crt_file = minio_certs | path_join("public.crt") %}
{%- set key_file = minio_certs | path_join("private.key") %}

{%- if truenas.minio.cert.ca_server %}
{%-   set pk_managed = salt["defaults.deepcopy"](truenas.minio.cert.private_key_managed) %}
{%-   do pk_managed.update({"name": key_file, "user": "minio", "group": "minio", "mode": "0640"}) %}
{%-   set cert_managed = salt["defaults.deepcopy"](truenas.minio.cert.certificate_managed) %}
{%-   do cert_managed.update({"user": "minio", "group": "minio"}) %}
{{
    salt["x509.certificate_managed_wrapper"](
      crt_file,
      ca_server=truenas.minio.cert.ca_server,
      signing_policy=truenas.minio.cert.signing_policy,
      private_key_managed=pk_managed,
      certificate_managed=truenas.minio.cert.certificate_managed,
      test=opts.get("test")
    ) | yaml(false)
}}

{%- else %}

{{ key_file }}_key:
  x509.private_key_managed:
    - name: {{ key_file }}
    {{ truenas.minio.cert.private_key_managed | dict_to_sls_yaml_params | indent(4) }}
{%-   if truenas.minio.cert.private_key_managed.get("new") and salt["file.file_exists"](key_file) %}
    - prereq:
      - x509: {{ crt_file }}
{%-   endif %}

{{ crt_file }}_crt:
  x509.certificate_managed:
    - name: {{ crt_file }}
    - signing_policy: {{ truenas.minio.cert.signing_policy or "null" }}
    - private_key: {{ key_file }}
    {{ truenas.minio.cert.certificate_managed | dict_to_sls_yaml_params | indent(4) }}
{%- if "signing_private_key" not in truenas.minio.cert.certificate_managed %}
    # This will be a self-signed certificate
    - signing_private_key: {{ key_file }}
{%- endif %}
    - mode: '0640'
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
{%-   if not truenas.minio.cert.private_key_managed.get("new") or not salt["file.file_exists"](key_file) %}
    - require:
      - x509: {{ key_file }}
{%-   endif %}
{%- endif %}

MinIO service is running:
  service.running:
    - name: minio
    - enable: true
    - jail: {{ minio_jid }}
    - watch:
      - x509: {{ crt_file }}
