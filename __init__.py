
from mycroft import MycroftSkill, intent_file_handler, intent_handler


class Vapm(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler('install.intent')
    def handle_install(self, message):
        package = message.data.get('package')
        pass

    @intent_handler('remove.intent')
    def handle_remove(self, message):
        pass

    @intent_handler('search.intent')
    def handle_remove(self, message):
        pass

    def converse(self, utterances, lang):
        pass


def create_skill():
    return Vapm()

