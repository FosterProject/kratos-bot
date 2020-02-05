import threading

from tools import bot
from tools.lib import debug
from tools.lib import wait

class EventManager:
    __instance = None
    @staticmethod
    def get_instance():
        if EventManager.__instance == None:
            EventManager()
        return EventManager.__instance

    def __init__(self):
        if EventManager.__instance != None:
            raise Exception("EventManager is already instantiated, access via get_instance()")
        else:
            self.__lock = threading.Lock()
            self.__event_stack = []
            EventManager.__instance = self


    def add_event(self, session, event):
        print(session.has_pending_event)
        if session.has_pending_event:
            debug("EventManager - add_event: session already has an event pending.. bot is configured wrong")
            return
        if not isinstance(event, Event):
            debug("EventManager - add_event: event is not of type Event")
            return
        with self.__lock:
            self.__event_stack.append((event, session))
            session.has_pending_event = True


    def process_event(self):
        # Only locks it to access the resource
        exit_early = False
        with self.__lock:
            if len(self.__event_stack) > 0:
                event, session = self.__event_stack.pop(0)
            else:
                exit_early = True
        if exit_early:
            return

        # Process event
        for action in event.actions:
            action()

        # Relieve session
        session.has_pending_event = False



class Event:
    def __init__(self):
        self.actions = []

    
    def add_action(self, action, delay):
        if not callable(action):
            debug("Event - add_action: action is not a callable")
            return
        def ac():
            action()
            wait(*delay)
        self.actions.append(ac)
    

    def click(self, pos):
        return lambda: bot.click(pos)


    def drag(self, pos1, pos2, time):
        return lambda: bot.drag(pos1, pos2, time)

    
    def type_string(self, string, send=False):
        return lambda: bot.type_string(string, send)
    

    def press_enter(self):
        return lambda: bot.press_enter()


    def press_space(self):
        return lambda: bot.press_space()
