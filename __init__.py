
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context, adds_context
from lingua_franca.parse import extract_number

from .actions import search, get_description, install, remove

def _is_there_full_match(boolean):
    if boolean:
        return 'including a full match'
    return 'without a full match'


class Vapm(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
        self.latest_results = None

    def _ensure_results_exist(self, message):
        package_name = self._multiword_package_name_procesor(message.data.get('package_name'))
        self.log.debug ('Ensure- package_name is {}'.format(package_name))
        if self.latest_results != None and package_name in self.latest_results.get_packages_names():
            return True
        elif self.latest_results != None and self.latest_results.get_number_of_results() == 1:
            return True
        else:
            self.handle_search(message)
            return False

    @classmethod
    def _multiword_package_name_procesor(cls, package_name):
        return package_name.replace(' ', '-')

    @classmethod
    def _recognize_an_it(cls, param, name):
        for word in ['package', 'it', 'name']:
            if word in param:
                return name
        return param

    @intent_handler(IntentBuilder('Search').require('search').require('package').require('package_name').optionally('filter').optionally('filter_type').optionally('filter_param'))
    @adds_context('SearchResultsContext')
    def handle_search(self, message):
        package_name = self._multiword_package_name_procesor(message.data.get('package_name'))
        results = search(package_name)
        if isinstance(results, str):
            self.speak(results)
        else:
            self.set_context('package_name', package_name)
            filter_type = message.data.get('filter_type')
            filter_param = message.data.get('filter_param')
            self.log.info ('Search- name: {}, number: {}'.format(package_name, results.get_number_of_results()))
            if filter_param != None and filter_type != None:
                filter_param = self._recognize_an_it(filter_param, message.data.get('package_name'))
                new_packages_names = self.filtering(filter_param, filter_type, results.get_packages_names())
                results.set_packages_names(new_packages_names)
            self.latest_results = results
            if results.get_number_of_results() == 1:
                self.set_context(
                        'package_name',
                        results.get_packages_names()[0]
                        )
            self.speak('Got {} results, {}'.format(
                    results.get_number_of_results(),
                    _is_there_full_match(results.is_there_full_match(package_name))), expect_response=True)

    @classmethod
    def filtering(cls, filter_param, filter_type, packages_names):
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
        return new_packages_names

    @intent_handler(IntentBuilder('FilteringSearch').require('SearchResultsContext').require('filter').require('filter_type').require('filter_param').require('package_name'))
    def handle_filter(self, message):
        filter_param = message.data.get('filter_param')
        filter_type = message.data.get('filter_type')
        filter_param = self._recognize_an_it(filter_param, message.data.get('package_name'))
        packages_names = self.latest_results.get_packages_names()
        new_packages_names = self.filtering (filter_param, filter_type, packages_names)
        self.latest_results.set_packages_names(new_packages_names)
        results = self.latest_results
        if len(new_packages_names) == 1:
            self.set_context(
                    'package_name',
                    new_packages_names[0]
                    )
        self.speak('Got {} results'.format(
                results.get_number_of_results()), expect_response=True)

    def _get_number(self, message, default_number=-1):
        utterance = message.data.get('utterance')
        results = self.latest_results
        number = extract_number(utterance)
        if not number:
            return default_number
        else:
            return int(number)

    @intent_handler(IntentBuilder('ReadResults').require('SearchResultsContext').require('read').one_of('results', 'them').optionally('number'))
    def handle_read_results(self, message):
        if self.latest_results == None or self.latest_results.get_number_of_results() == 0:
            self.speak('No package searched for yet.')
        else:
            number = self._get_number(message, self.latest_results.get_number_of_results())
            for i in range(number):
                self.speak('{}'.format(self.latest_results.get_packages_names()[i]))

    @intent_handler(IntentBuilder('ReadDescription').optionally('read').require('description').require('package_name').one_of('package', 'it'))
    def handle_read_description(self, message):
        number = self._get_number(message)
        self.log.info ('Describe- number: {}'.format(number))
        if number == -1:
            if self._ensure_results_exist(message):
                package_name = self._multiword_package_name_procesor(message.data.get('package_name'))
                self.speak(get_description(package_name))
            else:
                pass
        else:
            package_name = self.latest_results.get_packages_names()[number - 1]
            self.speak(get_description(package_name))

    @intent_handler(IntentBuilder('Install').require('install').require('package_name').one_of('package', 'it'))
    def handle_install(self, message): 
        if self._ensure_results_exist(message):
            package_name = self._multiword_package_name_procesor(message.data.get('package_name'))
            self.speak(install(package_name))
        else:
            pass

    @intent_handler(IntentBuilder('Remove').require('remove').require('package_name').one_of('package', 'it'))
    def handle_remove(self, message):
        if self._ensure_results_exist(message):
            package_name = self._multiword_package_name_procesor(message.data.get('package_name'))
            self.speak(remove(package_name))
        else:
            pass


def create_skill():
    return Vapm()

