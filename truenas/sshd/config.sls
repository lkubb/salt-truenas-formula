# vim: ft=sls

{#-
    Manages SSH configuration. TrueNAS automatically reloads the
    config, so this is mostly standalone. It still depends on
    `truenas.sshd.host_pki`_ since those should be managed before.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- set sls_host_pki = tplroot ~ ".sshd.host_pki" %}
{%- set sls_authorized_keys = tplroot ~ ".sshd.host_pki" %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}

include:
  - {{ sls_host_pki }}
  - {{ sls_authorized_keys }}

{%- if truenas.sshd.config.get("AuthorizedPrincipalsFile", "none") != "none" and truenas.sshd.authorized_principals %}
{%-   set pfile = truenas.sshd.config["AuthorizedPrincipalsFile"] %}
{%-   set requires_home = "%h" in pfile %}

OpenSSH authorized principals are managed:
  file.managed:
    - names:
{%-   for user, principals in truenas.sshd.authorized_principals.items() %}
{%-     set user_info = salt["user.info"](user) if requires_home else none %}
{%-     set home = (user_info.home if user_info else "__slot__:salt:user.info('" ~ user ~ "').home ~ ") if requires_home else "" %}
{%-     set primary_group = (salt["user.primary_group"](user) if user_info else ("__slot__:salt:user.primary_group('" ~  user ~ "')"))
                            if requires_home else truenas.lookup.rootgroup %}

        - {{ pfile | replace("%h", home) | replace("%u", user) | replace("%%", "%") }}:
          - context:
              principals: {{ principals | json }}
          - user: {{ user if requires_home else "root" }}
          - group: {{ primary_group }}
{%-   endfor %}
    - source: {{ files_switch(
                    ["sshd/principals.j2"],
                    config=truenas,
                    lookup="OpenSSH authorized principals are managed",
                 )
              }}
    - mode: '0600'
    - makedirs: true
    - template: jinja
    - defaults:
        truenas: {{ truenas | json }}
    - require_in:
      - truenas_service: ssh
{%- endif %}

SSH service is configured:
  truenas_service.configured:
    - name: ssh
{%- if truenas.sshd.config_truenas %}
    {{ truenas.sshd.config_truenas | dict_to_sls_yaml_params | indent(4) }}
{%- endif %}
    - options: {{ salt["file.read"](salt["cp.get_template"]("salt://" ~ tplroot ~ "/files/sshd_config.j2", none, truenas=truenas)).strip() | json }}
    - require:
      - sls: {{ sls_host_pki }}
      - sls: {{ sls_authorized_keys }}
