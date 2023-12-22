# vim: ft=sls

{#-
    Removes Telegraf and configuration.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}

Telegraf is stopped:
  service.dead:
    - name: telegraf

Telegraf init script is not registered:
  truenas_isscript.absent:
    - name: Start Telegraf

Telegraf dest is absent:
  file.absent:
    - name: {{ truenas.telegraf.dest }}
    - require:
      - Telegraf init script is absent
