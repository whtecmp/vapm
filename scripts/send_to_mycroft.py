
from mycroft_bus_client import MessageBusClient, Message
from sys import argv

def main():
    client = MessageBusClient()
    client.run_in_thread()
    client.emit(Message('speak', data={'utterance': argv[1]}))


if __name__ == '__main__':
    main()

