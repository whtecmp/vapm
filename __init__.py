
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context, adds_context
from .actions import search
from lingua_franca.parse import extract_number


def is_there_full_match(boolean):
    if boolean:
        return 'including a full match'
    return 'without a full match'


class Vapm(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
        self.latest_results = ''

    @intent_handler(IntentBuilder('Search').require('search').require('package').require('package_name'))
    @adds_context('SearchResultsContext')
    def handle_search(self, message):
        package_name = message.data.get('package_name')
        results = search(package_name)
        self.set_context('package_name', package_name)
        self.latest_results = results
        self.speak('Got {} results, {}'.format(
                results.get_number_of_results(),
                is_there_full_match(results.is_there_full_match())), expect_response=True)

    
    @intent_handler(IntentBuilder('FilteringSearch').require('SearchResultsContext').require('filter').require('filter_type').require('filter_param'))
    def handle_filter(self, message):
        filter_param = message.data.get('filter_param')
        filter_type = message.data.get('filter_type')
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

    @intent_handler(IntentBuilder('ReadResults').require('SearchResultsContext').require('read').require('results').optionally('number'))
    def handle_read(self, message):
        utterance = message.data.get('utterance')
        results = self.latest_results
        number = extract_number(utterance)
        if not number:
            number = results.get_number_of_results()
        else:
            number = int(number)
        for i in range(number):
            self.speak('{}'.format(results.get_packages_names()[i]))

    @intent_handler(IntentBuilder('Install').require('install'))
    def handle_install(self, message):
        pass

    @intent_handler(IntentBuilder('Remove').require('remove'))
    def handle_remove(self, message):
        pass


def create_skill():
    return Vapm()

