# vim: ft=sls

{#-
    Does not remove the certificates/keys because this is hard
    to automate and can break a lot of things.
    You will need to do this manually.
#}


Certificates should not be cleaned:
  test.show_notification:
    - text: |
        Removing the generated certificates is only possible manually.
