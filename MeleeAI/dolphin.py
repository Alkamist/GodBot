import os
import configparser
import pathlib
import subprocess

class Dolphin():
    def __init__(self):
        self.user_directory = str(pathlib.Path.home().joinpath("Documents", "Dolphin Emulator"))
        self.dolphin_path = str(pathlib.Path.cwd().joinpath("DolphinEmulator", "Dolphin.exe"))
        self.melee_iso_path = str(pathlib.Path.cwd().joinpath("MeleeISO", "Super Smash Bros. Melee (v1.02).iso"))
        self.process = None
        self.change_settings([
            ["Core", 'enablecheats', "True"],
            ["Input", 'backgroundinput', "True"]
        ])
        self.turn_on_netplay_community_settings()

    def change_settings(self, new_settings):
        config = configparser.SafeConfigParser()
        config_file = self.user_directory + '/Config/Dolphin.ini'
        config.read(config_file)
        for setting in new_settings:
            config.set(setting[0], setting[1], setting[2])
        with open(config_file, 'w') as dolphinfile:
            config.write(dolphinfile)

    def turn_on_netplay_community_settings(self):
        config = configparser.SafeConfigParser(allow_no_value=True)
        config.optionxform = str
        melee_config_file = self.user_directory + "/GameSettings/GALE01.ini"
        config.read(melee_config_file)
        if not config.has_section("Gecko_Enabled"):
            config.add_section("Gecko_Enabled")
        config.set("Gecko_Enabled", "$Netplay Community Settings")
        with open(melee_config_file, 'w') as dolphinfile:
            config.write(dolphinfile)

    def run(self):
        process_args = [self.dolphin_path,
                        "--exec", self.melee_iso_path,
                        "--user", self.user_directory]

        print("Starting Dolphin.")
        self.process = subprocess.Popen(process_args)

    def stop(self):
        if self.process != None:
            self.process.terminate()