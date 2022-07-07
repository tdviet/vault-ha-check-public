# vault-ha-check-public

This is the public version of Python script for Vault HA

The script check generic endpoint, and if something is wrong, 
check service instances and update the generic endpoint to 
the healthy instance. Raise alarm if no healthy instance found
