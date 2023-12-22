# vim: ft=sls

{#-
    Ensures SSH service is enabled and running.
    No config since SSH is required for any of this to work.
#}

{%- set tplroot = tpldir.split("/")[0] %}
{%- from tplroot ~ "/map.jinja" import mapdata as truenas with context %}

# We don't need to reload on changes since TrueNAS takes care
# of this automatically.
# The following is mostly a check
SSH service is enabled and running:
  service.running:
    - name: openssh
    - enable: true
