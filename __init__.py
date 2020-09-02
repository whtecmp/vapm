
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context, adds_context
from lingua_franca.parse import extract_number

from .actions import search, get_description, install, remove

def _is_there_full_match(boolean):
    if boolean:
        return 'including a full match'
    return 'without a full match'

def _ensure_results_exist(func):
    def new_func(self, message):
        package_name = message.data.get('package_name')
        if self.latest_results != None and package_name in self.latest_results.get_packages_names():
            func(self, message)
        elif self.latest_results != None and len(self.latest_results.get_packages_names()) == 1:
            self.set_context(
                    'package_name',
                    self.latest_results.get_packages_names()[0]
                    )
            func(self, message)
        else:
            self.handle_search(message)


class Vapm(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
        self.latest_results = None

    def _ensure_results_exist(self, message):
        package_name = message.data.get('package_name')
        if self.latest_results != None and package_name in self.latest_results.get_packages_names():
            return True
        else:
            self.handle_search(message)
            return False

    @intent_handler(IntentBuilder('Search').require('search').require('package').require('package_name'))
    @adds_context('SearchResultsContext')
    def handle_search(self, message):
        package_name = message.data.get('package_name')
        results = search(package_name)
        self.set_context('package_name', package_name)
        self.latest_results = results
        self.speak('Got {} results, {}'.format(
                results.get_number_of_results(),
                _is_there_full_match(results.is_there_full_match())), expect_response=True)

    
    @intent_handler(IntentBuilder('FilteringSearch').require('SearchResultsContext').require('filter').require('filter_type').require('filter_param').require('package_name'))
    def handle_filter(self, message):
        filter_param = message.data.get('filter_param')
        filter_type = message.data.get('filter_type')
        for word in ['package', 'it', 'name']:
            if word in filter_param:
                filter_param = message.data.get('package_name')
                break
        packages_names = self.latest_results.get_packages_names()
        begin = lambda name, param: name.startswith(param)
        end = lambda name, param: name.endswith(param)
        contain = lambda name, param: param in name
        filters = {
                    'begin': begin,
                    'begins': begin,
                    'end': end,
                    'ends': end,
                    'contain': contain,
                    'contains': contain,
                }
        filter = lambda name: filters[filter_type](name, filter_param)
        new_packages_names = []
        for package_name in packages_names:
            if filter(package_name):
                new_packages_names.append(package_name)
        self.latest_results.set_packages_names(new_packages_names)
        results = self.latest_results
        self.speak('Got {} results'.format(
                results.get_number_of_results()), expect_response=True)

    @intent_handler(IntentBuilder('ReadResults').require('SearchResultsContext').require('read').one_of('results', 'them').optionally('number'))
    def handle_read_results(self, message):
        utterance = message.data.get('utterance')
        results = self.latest_results
        number = extract_number(utterance)
        if not number:
            number = results.get_number_of_results()
        else:
            number = int(number)
        for i in range(number):
            self.speak('{}'.format(results.get_packages_names()[i]))

    @intent_handler(IntentBuilder('ReadDescription').optionally('read').require('description').require('package_name').one_of('package', 'it'))
    def handle_read_description(self, message):
        if self._ensure_results_exist(message):
            package_name = message.data.get('package_name')
            self.speak(get_description(package_name))
        else:
            pass

    @intent_handler(IntentBuilder('Install').require('install').require('package_name').one_of('package', 'it'))
    def handle_install(self, message): 
        if self._ensure_results_exist(message):
            package_name = message.data.get('package_name')
            self.speak(install(package_name))
        else:
            pass

    @intent_handler(IntentBuilder('Remove').require('remove').require('package_name').one_of('package', 'it'))
    def handle_remove(self, message):
        if self._ensure_results_exist(message):
            package_name = message.data.get('package_name')
            self.speak(remove(package_name))
        else:
            pass


def create_skill():
    return Vapm()

