from mycroft import MycroftSkill, intent_file_handler


class Vapm(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('vapm.intent')
    def handle_vapm(self, message):
        self.speak_dialog('vapm')


def create_skill():
    return Vapm()

