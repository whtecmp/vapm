
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context, adds_context
from .actions import search

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
        self.speak('Got {} results, {}, do you want to filter results?'.format(
                results.get_number_of_results(),
                is_there_full_match(results.is_there_full_match())), expect_response=True)

    
    @intent_handler(IntentBuilder('FilteringSearch').require('SearchResultsContext').require('filter'))
    def handle_filter(self, message):
        pass

    @intent_handler(IntentBuilder('ReadResults').require('SearchResultsContext').require('read').require('result').optionally('number'))
    def handle_read(self, message):
        number = message.data.get('number')
        results = message.data.get('results')
        #number = number is None ? result.get_number_of_results() : int(number)
        for i in range(len(number)):
            self.speak('{}', results[i].name)

    @intent_handler(IntentBuilder('Install').require('install'))
    def handle_install(self, message):
        pass

    @intent_handler(IntentBuilder('Remove').require('remove'))
    def handle_remove(self, message):
        pass


def create_skill():
    return Vapm()

