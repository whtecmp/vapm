#!/bin/bash

package_name=$1
echo $(apt search $package_name | grep -v ^\ | sort | uniq | python3 /opt/mycroft/skills/vapm-skill/scripts/get_name.py)


