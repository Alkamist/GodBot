from MeleeAI.dolphin import Dolphin
from MeleeAI.menu_manager import MenuManager
from MeleeAI.memory_watcher import MemoryWatcher
from MeleeAI.state import *
from MeleeAI.state_manager import StateManager
from MeleeAI.gamepad import *

import os
def write_locations(dolphin, state_manager):
    path = dolphin.user_directory + '/MemoryWatcher'
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + '/Locations.txt', 'w') as f:
        f.write('\n'.join(state_manager.locations()))

def main():
    dolphin = Dolphin()
    menu_manager = MenuManager()
    memory_watcher = MemoryWatcher()
    state = State()
    state_manager = StateManager(state)
    bot_gamepad = Gamepad(2, dolphin)
    write_locations(dolphin, state_manager)
    dolphin.run()

    try:
        while True:
            messages = memory_watcher.get_messages()
            if messages is not None:
                for message in messages:
                    state_manager.handle(*message)
            memory_watcher.advance()

            if state.menu == Menu.Characters:
                menu_manager.pick_fox(state, bot_gamepad)

            bot_gamepad.flush()

    except KeyboardInterrupt:
        dolphin.stop()
        print('Stopped')

if __name__ == "__main__":
    main()