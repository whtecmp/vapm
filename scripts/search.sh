#!/bin/bash

package_name=$1
echo $(apt search $package_name | grep -v ^\ | grep \/ | sort | uniq | python3 /opt/mycroft-root/vapm/scripts/get_name.py)

