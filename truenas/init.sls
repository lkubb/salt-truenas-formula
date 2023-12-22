# vim: ft=sls

{#-
    A collection of states to manage some aspects of TrueNAS.
    You will have to target each mod explicitly, just ``truenas``
    does nothing.
#}

include: []

This file does nothing:
  test.show_notification:
    - text: |
        You will have to target each mod explicitly, this file
        does nothing.
