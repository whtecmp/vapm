
from subprocess import Popen, PIPE
INITIAL_PATH='/opt/mycroft/skills/vapm/scripts/'

class Result(object):

    def __init__(self, packages_names):
        self.packages_names = packages_names

    def get_number_of_results(self):
        return len(self.packages_names)
    
    def is_there_full_match(self, package_name):
        return package_name in self.packages_names

    def get_packages_names(self):
        return self.packages_names

    def set_packages_names(self, packages_names):
        self.packages_names = packages_names

def search(package_name):
    result = Popen([INITIAL_PATH+'search.sh', package_name], stdout=PIPE)
    result = result.stdout.read().decode().strip()
    if result == '':
        return 'Could not find any package matching ' + package_name
    result = result.split(' ')
    result = Result(result)
    return result

def get_description(package_name):
    desc = Popen([INITIAL_PATH+'get_description.sh', package_name], stdout=PIPE)
    desc = desc.stdout.read().decode().strip()
    if desc == '':
        return 'Could not get description of package ' + package_name
    return desc

def install(package_name):
    return 'Installing ' + package_name

def remove(package_name):
    return 'Removing ' + package_name

