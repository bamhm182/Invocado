#!/usr/bin/env python

import invocado


class Example:
    def __init__(self):
        self.handler = invocado.Handler(debug=True)
        # self.setup_guacamole()
        self.setup_repo()

    def setup_repo(self):
        self.handler.db.terraform_repo = 'https://gitlab.com/bamhm182/terraform-configs'
        self.handler.terraform.clone_repo()
        self.handler.terraform.add_configs_to_db()
        self.handler.db.prune_terraform_folders()

        self.handler.db.print_mac_mappings()

    def setup_guacamole(self):
        self.handler.guacamole.authenticate()

    def print_connections(self):
        connections = self.handler.guacamole.get_connections()
        connection = list(connections.keys())[0]
        parameters = self.handler.guacamole.get_connection_parameters(connection)
        print(parameters)


if __name__ == '__main__':
    e = Example()
