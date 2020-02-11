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
        if session.has_pending_event:
            debug("EventManager - add_event: session already has an event pending.. bot is configured wrong")
            return
        if not isinstance(event, Event):
            debug("EventManager - add_event: event is not of type Event")
            return
        with self.__lock:
            debug("EventManager - add_event: adding event to the event stack")
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

        debug("Processing event")

        # Process event
        for action in event.actions:
            action()

        # Relieve session
        session.has_pending_event = False


class Event:
    def __init__(self, actions=[]):
        self.actions = []
        self.action_returns = []
        if isinstance(actions, list):
            for action, delay in actions:
                self.add_action(action, delay)

    
    def add_action(self, action, delay=None):
        if not callable(action):
            debug("Event - add_action: action is not a callable")
            return
        def ac():
            res = action()
            self.action_returns.append(res)
            if delay is not None:
                wait(*delay)
        self.actions.append(ac)
    

    @staticmethod
    def basic_click(session, pos, wait=None):
        click_event = Event([
            (Event.click(pos), wait)
        ])
        session.publish_event(click_event)

    @staticmethod
    def click(pos):
        return lambda: bot.click(pos)

    @staticmethod
    def click_long(pos):
        return lambda: bot.click_long(pos)

    @staticmethod
    def drag(pos1, pos2, time):
        return lambda: bot.drag(pos1, pos2, time)

    @staticmethod
    def type_string(string, send=False):
        return lambda: bot.type_string(string, send)
    
    @staticmethod
    def press_enter():
        return lambda: bot.press_enter()

    @staticmethod
    def press_space():
        return lambda: bot.press_space()
