
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from mycroft.skills.context import removes_context, adds_context
#from .actions import search

class Vapm(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)

    #@adds_context('SearchResultsContext')
    @intent_handler(IntentBuilder('Search').require('search').require('package'))
    def handle_search(self, message):
        package = message.data.get('package')
        #results = search(package)
        #self.set_context('package_name', package)
        #self.set_context('result', result)
        self.speak('I am not ready yet, but hey, I can do this: {}'.format(package))
        '''self.speak('Got {} results, {}, do you want to filter results?'.format(
                results.get_number_of_results(),
                results.is_there_full_match() ? 'Including a full match' : 'Without a full match'), expect_response=True)'''

    '''
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
    '''


def create_skill():
    return Vapm()

