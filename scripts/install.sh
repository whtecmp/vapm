#!/bin/bash

package_name=$1
apt -y install $package_name
err_code=$?

if [ "$err_code" == 0 ]; then
	sudo -u mycroft python3 /opt/mycroft-root/vapm/scripts/send_to_mycroft.py "Package $package_name installed successfully."
elif [ "$err_code" == 100 ]; then
	sudo -u mycroft python3 /opt/mycroft-root/vapm/scripts/send_to_mycroft.py "Package $package_name failed installation."
fi

