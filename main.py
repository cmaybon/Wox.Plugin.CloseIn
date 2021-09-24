import os
import re
import typing
from datetime import datetime
from datetime import timedelta

from wox import Wox, WoxAPI


def get_running_exes() -> typing.List[str]:
    raw = os.popen("tasklist").read()
    lines = raw.split("\n")
    exe_names = list()
    for line in lines:
        match = re.findall(r"^.*\.exe", line)
        if len(match) == 1:
            exe_names.append(match[0])
    return exe_names


class CloseIn(Wox):
    RUNNING_EXES = None
    COMMAND_PREFIX = "closein"

    def query(self, query: str):
        if CloseIn.RUNNING_EXES is None:
            CloseIn.RUNNING_EXES = get_running_exes()

        query_split = query.split()
        target_process_name = query_split[0]
        time_string = None
        if len(query_split) > 1:
            time_string = query_split[1]

        potential_matches = list()
        if target_process_name is False:
            potential_matches = list(CloseIn.RUNNING_EXES)
        else:
            for running_exe in CloseIn.RUNNING_EXES:
                if running_exe.lower().startswith(target_process_name.lower()):
                    potential_matches.append(running_exe)

        results = list()
        for potential_match in potential_matches:
            result = {
                "Title": "CloseIn",
                "Subtitle": f"match: {potential_match}, time: {time_string}",
                "IcoPath": "Images\\closein.png"
            }
            if time_string:
                result["JsonRPCAction"] = {
                    "method": "schedule_close_of_process",
                    "parameters": [
                        potential_match,
                        time_string
                    ],
                    "dontHideAfterAction": False
                }
            results.append(result)

        if target_process_name is False:
            return results

        if len(potential_matches) > 0:
            potential_match = potential_matches[0]
            results.insert(0, {
                "Title": "CloseIn Autocomplete",
                "Subtitle": f"Press enter to autofill: \"{potential_match}\"",
                "IcoPath": "Images\\closein.png",
                "JsonRPCAction": {
                    "method": "auto_complete_exe_name",
                    "parameters": [
                        potential_match
                    ],
                    "dontHideAfterAction": True
                }
            })
        return results

    def auto_complete_exe_name(self, potential_match: str):
        WoxAPI.change_query(f"{CloseIn.COMMAND_PREFIX} {potential_match} ", requery=True)

    def schedule_close_of_process(self, process_name, time_string):
        parsed_time = self.parse_time(time_string)
        if parsed_time is None:
            return
        target_time = datetime.now() + parsed_time
        target_time_string = target_time.strftime("%H:%M:%S")

        if process_name == "_shutdown":
            self.schedule_pc_shutdown(target_time_string)
            return

        if not process_name.endswith(".exe"):
            process_name += ".exe"
        task_name = f"wox_plugin_closein_{process_name.rstrip('.exe')}"
        os.system(f'schtasks /create '
                  f'/tn "{task_name}" '
                  f'/sc once '
                  f'/st {target_time_string} '
                  f'/tr "cmd /c \'schtasks /delete /tn {task_name} /f && taskkill /f /im {process_name} /t\'"')

    def parse_time(self, time_string):
        regex = re.compile(r'((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')

        parts = regex.match(time_string)
        if not parts:
            return
        parts = parts.groupdict()
        time_params = {}
        for name, param in parts.items():
            if param:
                time_params[name] = int(param)
        return timedelta(**time_params)

    def schedule_pc_shutdown(self, target_time_string):
        task_name = "wox_plugin_closein_shutdown_pc"
        os.system(f'schtasks /create '
                  f'/tn "{task_name}" '
                  f'/sc once '
                  f'/st {target_time_string} '
                  f'/tr "cmd /c \'schtasks /delete /tn {task_name} /f && shutdown /s /hybrid /t 0\'"')


if __name__ == '__main__':
    CloseIn()
