# vim: ft=sls

{#-
    Removes managed OpenSSH authorized keys and trusted user CA keys.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}

{%- for user, config in truenas.sshd.authorized_keys.items() %}
{%-   set sync = config.get("sync", truenas.sshd.authorized_keys_sync) %}
{%-   if sync %}

Wanted authorized keys for user {{ user }} are absent:
  ssh_auth.manage:
    - user: {{ user }}
    - ssh_keys: []
{%-     if truenas.sshd.config.get("AuthorizedKeysFile") %}
    - config: '{{ truenas.sshd.config["AuthorizedKeysFile"] }}'
{%-     endif %}
{%-   else %}

Wanted authorized keys for user {{ user }} are absent:
  ssh_auth.absent:
    - names: {{ config.get("keys", []) | json }}
    - user: {{ user }}
    - options: {{ config.get("options", []) | json }}
    - comment: {{ config.get("comment") | json }}
{%-     if truenas.sshd.config.get("AuthorizedKeysFile") %}
    - config: '{{ truenas.sshd.config["AuthorizedKeysFile"] }}'
{%-     endif %}
{%-   endif %}
{%- endfor %}

{%- if truenas.sshd.config.get("TrustedUserCAKeys") %}

Trusted user CA keys are absent:
  file.absent:
    - name: truenas.sshd.config["TrustedUserCAKeys"]
{%- endif %}
