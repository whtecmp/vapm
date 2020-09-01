
def search(package_name):
    result = lambda : None
    result.get_number_of_results = lambda : 40
    result.is_there_full_match = lambda : True
    return result

