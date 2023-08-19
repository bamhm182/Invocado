"""
db/models/mac_mapping.py

This table contains MAC Address Mappings when using Apache Guacamole's WoL features

A MAC Address is made up of the following "positions", which I am using as follows:
0: First Level Folder
1: Second Level Folder
2: Third Level Folder
3: Fourth Level Folder
4: VLAN
5: Instance

I will provide some examples based on the following DB dump:

config table:
| mac_position_type_0 | ..type_1 | ..type__2 | ..type_3 | ..type_4 | ..type_5 |
| ------------------- | -------- | --------- | -------- | -------- | -------- |
| folder              | folder   | folder    | folder   | vlan     | instance |

mac_mapping table:
| Position | Value | Description |
| -------- | ----- | ----------- |
| 0        | 0     | kali        | #  0 == 0x00
| 0        | 26    | nixos       | # 26 == 0x1A
| 1        | 0     | ctf         | #  0 == 0x00
| 1        | 82    | base        | # 82 == 0x52
| 2        | 3     | thicc       | #  3 == 0x03
| 4        | 0     | 15          | #  0 == 0x00
| 4        | 10    | 1006        | # 10 == 0x0A

The 5th VM created from the terraform config at ./kali/ctf/main.tf
    and on VLAN 15 would have the following MAC:
        00:00:FF:FF:00:04

The 87th VM created from the terraform config at ./nixos/base/thicc/main.tf
    and on VLAN 1006 would have the following MAC:
        1A:52:03:FF:0A:57
"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MacMapping(Base):
    __tablename__ = 'mac_mapping'
    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
    position = sa.Column(sa.INTEGER)
    value = sa.Column(sa.INTEGER)
    description = sa.Column(sa.VARCHAR(100), default='')
