
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
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

    @intent_handler(IntentBuilder('Search').require('search').require('package').require('package_details').optionally('filter').optionally('filter_type').optionally('filter_param'))
    @adds_context('SearchResultsContext')
    def handle_search(self, message):
        with open('/opt/mycroft/skills/vapm/locale/en-us/filter.voc', 'r') as vocabulary_file:
            vocabulary = vocabulary_file.readlines()
        vocabulary = [voc.strip() for voc in vocabulary]
        package_name = message.data.get('package_details')
        self.log.info ('utterance is {}\n package_name is {}\n filter_utterance is {}'.format(message.data.get('utterance'), package_name, message.data.get('filter_utterance')))
        words = package_name.split(' ')
        package_name = ''
        i = 0
        for word in words:
            if word not in vocabulary:
                package_name += (word + ' ')
                i+=1
            else:
                break
        package_name = package_name.strip()
        self.log.info (words)
        utterance = ' '.join(words[i:])
        package_name = self._multiword_package_name_procesor(package_name)
        results = search(package_name)
        if isinstance(results, str):
            self.speak(results)
        else:
            self.set_context('package_name', package_name)
            self.log.info ('utterance is {}'.format(utterance))
            if utterance != '':
                new_packages_names = self.utterance_filtering(utterance, results.get_packages_names(), package_name, self.log.info)
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
    def utterance_filtering(cls, utterance, packages_names, context_package_name, log=lambda __: None):
        with open('/opt/mycroft/skills/vapm/locale/en-us/filtering.rx', 'r') as regex_file:
            regex = regex_file.read().strip()
        engine = IntentDeterminationEngine()
        engine.register_regex_entity(regex)
        filter_intent = IntentBuilder('FilteringSearch').require('filter_type').require('filter_param').build()
        engine.register_intent_parser(filter_intent)
        words = utterance.split(' ')
        sentences = []
        sentence = ''
        yesno = 1
        for word in words:
            if word not in ['and', 'or', 'not']:
                sentence += (word + ' ')
            elif word != 'not':
                sentences.append((yesno, sentence))
                sentence = ''
                sentences.append((0, word))
                yesno = 1
            else:
                yesno = -1
        sentences.append((yesno, sentence))
        
        latest_operand = 'or'
        all_packages_names = packages_names
        current_packages_names = []
        for yesno, sentence in sentences:
            if sentence not in ['and', 'or']:
                log (sentence)
                for intent in engine.determine_intent(sentence):
                    break
                filter_param = intent.get('filter_param')
                filter_type = intent.get('filter_type')
                filter_param = cls._recognize_an_it(filter_param, context_package_name)
                new_packages_names = cls.filtering (filter_param, filter_type, all_packages_names)
                if yesno == -1:
                    new_packages_names = [package_name for package_name in all_packages_names if package_name not in new_packages_names]
                if latest_operand == 'or':
                    current_packages_names = [package_name for package_name in all_packages_names if package_name in current_packages_names or package_name in new_packages_names]
                elif latest_operand == 'and':
                    current_packages_names = [package_name for package_name in all_packages_names if package_name in current_packages_names and package_name in new_packages_names]
            else:
                latest_operand = sentence
        return current_packages_names

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
        utterance = message.data.get('utterance')
        new_packages_names = self.utterance_filtering(utterance, self.latest_results.get_packages_names(), message.data.get('package_name'), self.log.debug)
        self.latest_results.set_packages_names(new_packages_names)
        if len(new_packages_names) == 1:
            self.set_context(
                    'package_name',
                    new_packages_names[0]
                    )
        self.speak('Got {} results'.format(
                self.latest_results.get_number_of_results()), expect_response=True)

    def _get_number(self, message, default_number=-1):
        utterance = message.data.get('utterance')
        results = self.latest_results
        number = extract_number(utterance, ordinals=True)
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
        self.log.debug ('Describe- number: {}'.format(number))
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

