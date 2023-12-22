# vim: ft=sls

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}
{%- from tplroot ~ "/libtofsstack.jinja" import files_switch with context %}

{%- for user, config in truenas.sshd.authorized_keys.items() %}
{%-   if config.get("sync") %}

Authorized keys for user {{ user }} are synced:
  ssh_auth.manage:
    - ssh_keys: {{ config.get("keys", []) | json }}
    - user: {{ user }}
    - options: {{ config.get("options", []) | json }}
    - comment: {{ config.get("comment") | json }}
{%-     if truenas.sshd.config.get("AuthorizedKeysFile") %}
    - config: '{{ truenas.sshd.config["AuthorizedKeysFile"] }}'
{%-     endif %}
{%-   else %}

Authorized keys for user {{ user }} are present:
  ssh_auth.present:
    - names: {{ config.get("keys", []) | json }}
    - user: {{ user }}
    - options: {{ config.get("options", []) | json }}
    - comment: {{ config.get("comment") | json }}
{%-     if truenas.sshd.config.get("AuthorizedKeysFile") %}
    - config: '{{ truenas.sshd.config["AuthorizedKeysFile"] }}'
{%-     endif %}

Unwanted authorized keys for user {{ user }} are absent:
  ssh_auth.absent:
    - names: {{ config.get("keys_absent", []) | json }}
    - user: {{ user }}
    - options: {{ config.get("options", []) | json }}
    - comment: {{ config.get("comment") | json }}
{%-     if truenas.sshd.config.get("AuthorizedKeysFile") %}
    - config: '{{ truenas.sshd.config["AuthorizedKeysFile"] }}'
{%-     endif %}
{%-   endif %}
{%- endfor %}

{%- if truenas.sshd.config.get("TrustedUserCAKeys") %}

Trusted user CA keys are managed:
  file.managed:
    - name: {{ truenas.sshd.config["TrustedUserCAKeys"] }}
    - source: {{ files_switch(
                    ["sshd/trusted_user_ca_keys.pem", "sshd/trusted_user_ca_keys.pem.j2"],
                    config=truenas,
                    lookup="Trusted user CA keys are managed",
                 )
              }}
    - mode: '0644'
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - makedirs: true
    - template: jinja
    - context:
        truenas: {{ truenas | json }}
{%- endif %}
