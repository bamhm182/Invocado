#!/usr/bin/env python

import invocado

if __name__ == '__main__':
    h = invocado.Handler()
    h.guacamole.authenticate()
    connections = h.guacamole.get_connections()
    print(connections)
    parameters = h.guacamole.get_connection_parameters(list(connections.keys())[0])
    print(parameters)
