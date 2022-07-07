"""
Script for checking and updating generic endpoint for HA
"""
import sys

import requests
import socket

GENERIC_HOSTNAME = "vault.services.fedcloud.eu"
UPDATE_SECRET = "XXXXX"
INSTANCE_HOSTNAMES = ("vault-infn.services.fedcloud.eu", "vault-ifca.services.fedcloud.eu")


def check_server_health(server):
    """
    Check server health
    :param server: server hostname
    :return: True if OK, False if something wrong
    """

    try:
        r = requests.head(f"https://{server}:8200/v1/sys/health", timeout=4)
        status = r.status_code
        if status in (200, 429):
            print(f"Server {server} is OK")
            return True
    except Exception as e:
        print(f'[ERROR]: {e}')

    # Return False by default
    return False


def update_generic_endpoint(generic, server, update_secret):
    """
    Update generic endpoint to the server
    :param generic: Generic hostname
    :param update_secret: Secret for updating IP
    :param server: Hostname of healthy instance
    :return: None
    """
    ip = socket.gethostbyname(server)
    update_string = f"https://{generic}:{update_secret}@nsupdate.fedcloud.eu/nic/update?hostname={generic}&myip={ip}"
    # print(f"Update string: {update_string}", file=sys.stderr)
    r = requests.get(update_string, timeout=4)
    print(f"Server response: {r.text}", file=sys.stderr)


def check_and_update(generic, instances, update_secret):
    """
    Check generic endpoint and update to a healthy instance
    :param generic: Generic hostname
    :param update_secret: Secret for updating IP
    :param instances: list of service instances
    :return: 0 if OK, 2 for Critical
    """

    # First, check the health of generic endpoint
    if check_server_health(generic):

        # If OK, nothing to do, print OK message and return OK
        print(f"Generic server {generic} is OK, nothing to do")
        return 0

    else:
        # Instance at generic endpoint is faulty

        # Looking for a healthy instance among the instance list
        for instance in instances:
            if check_server_health(instance):

                # Found a healthy one, updating generic endpoint to it
                print(f"Update {generic} to instance {instance}")
                update_generic_endpoint(generic, instance, update_secret)

                # Generic endpoint updated, return OK
                return 0

        # No healthy instance found, print error message and return CRITICAL
        print("Error: All servers are faulty. Raise alarm !!!")
        return 2


def main():
    """
    Main function
    """
    return check_and_update(GENERIC_HOSTNAME, INSTANCE_HOSTNAMES, UPDATE_SECRET)


if __name__ == "__main__":
    main()
