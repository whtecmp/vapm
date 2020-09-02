
def __set(result, packages_names):
    result.packages_names = packages_names

def search(package_name):
    result = lambda : None
    result.get_number_of_results = lambda : len(result.packages_names)
    result.is_there_full_match = lambda : package_name in result.packages_names
    result.packages_names = ['python', 'python3.6', 'libpython', 'libpython-dev', 'no-quick-yes']
    result.get_packages_names = lambda : result.packages_names
    result.set_packages_names = lambda packages_names: __set(result, packages_names)
    return result

def get_description(package_name):
    return 'Describing ' + package_name

def install(package_name):
    return 'Installing ' + package_name

def remove(package_name):
    return 'Removing ' + package_name

