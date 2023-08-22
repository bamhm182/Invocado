#!/usr/bin/env python

import invocado

if __name__ == '__main__':
    h = invocado.Handler(debug=True)
    h.guacamole.authenticate()
    connections = h.guacamole.get_connections()
    connection = list(connections.keys())[0]
    parameters = h.guacamole.get_connection_parameters(connection)
