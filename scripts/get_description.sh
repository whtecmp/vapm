#!/bin/bash

package_name=$1
ret=$(apt search $package_name | grep -A 1 ^$package_name\/ | grep ^\ )
echo $ret

