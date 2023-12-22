# vim: ft=sls

{#-
    Installs Telegraf and manages configuration.

    You need to set ``truenas:telegraf:destination``.
    It is advised to install it on a dataset to avoid it being
    removed during an update.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}
{%- from tplroot ~ "/libtofsstack.jinja" import files_switch with context %}

Telegraf root dir is present:
  file.directory:
    - name: {{ truenas.telegraf.dest }}
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - mode: '0755'

Telegraf is extracted:
  archive.extracted:
    - name: {{ truenas.telegraf.dest | path_join("pkg") }}
    - source: {{ truenas.lookup.telegraf.source.format(release=truenas.telegraf.version) }}
    - source_hash: {{ truenas.telegraf.source_hash }}
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - require:
      - file: {{ truenas.telegraf.dest }}

Telegraf initfile is present:
  file.managed:
    - name: {{ truenas.telegraf.dest | path_join("telegraf.init") }}
    - source: {{ files_switch(
                    ["telegraf/telegraf.init", "telegraf/telegraf.init.j2"],
                    config=truenas,
                    lookup="Telegraf initfile is present",
                 )
              }}
    - template: jinja
    - context:
        truenas: {{ truenas | json }}
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - mode: '0755'
    - require:
      - file: {{ truenas.telegraf.dest }}

{%- if truenas.telegraf.tls_ca %}

TLS CA file is present:
  x509.pem_managed:
    - name: {{ truenas.telegraf.dest | path_join("tls_ca.pem") }}
    - text: {{ truenas.telegraf.tls_ca | json }}
    - require:
      - file: {{ truenas.telegraf.dest }}
    - require_in:
      - Telegraf config is managed
{%- endif %}

Telegraf config is managed:
  file.managed:
    - name: {{ truenas.telegraf.dest | path_join("telegraf.conf") }}
    - contents: {{ salt["slsutil.serialize"]("toml", truenas.telegraf.config) | json }}
    # The serializer uses the `toml` lib, not `tomllib`. The latter would
    # be available in Py 3.11+, but TrueNAS CORE has a lower one. Also
    # cannot easily install Python modules, thus render on the master.
    # - serializer: toml
    # - dataset: {# truenas.telegraf.config | json #}
    - mode: '0640'
    - user: root
    - group: {{ truenas.lookup.rootgroup }}
    - require:
      - file: {{ truenas.telegraf.dest }}

Telegraf init script is registered and running:
  truenas_isscript.present:
    - name: Start Telegraf
    - typ: COMMAND
    - when: POSTINIT
    - data: ln -s '{{ truenas.telegraf.dest | path_join("telegraf.init") }}' '{{ truenas.lookup.telegraf.rcfile }}'; service telegraf start
    - enabled: true
    - timeout: 30
    - require:
      - Telegraf config is managed

Telegraf is running:
  service.running:
    - name: telegraf
    - watch:
      - Telegraf config is managed
