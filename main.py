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
        potential_matches.append("_shutdown")

        results = list()
        for potential_match in potential_matches:
            result = {
                "Title": f"CloseIn - {potential_match}",
                "IcoPath": "Images\\closein.png"
            }
            if time_string:
                parsed_time = self.parse_time_string(time_string)
                if parsed_time:
                    target_time, target_date = self.calculate_schedule_time_strings(parsed_time)
                    result["Subtitle"] = f"Close at {target_time} on {target_date}"
                    result["JsonRPCAction"] = {
                        "method": "schedule_close_of_process",
                        "parameters": [
                            potential_match,
                            target_time,
                            target_date
                        ],
                        "dontHideAfterAction": False
                    }
                else:
                    result["Subtitle"] = "Invalid time input"
            elif " " not in query:
                result["JsonRPCAction"] = {
                    "method": "auto_complete_exe_name",
                    "parameters": [
                        potential_match
                    ],
                    "dontHideAfterAction": True
                }
                result["Subtitle"] = "Press enter to autocomplete"
            results.append(result)

        if target_process_name is False:
            return results
        return results

    def auto_complete_exe_name(self, potential_match: str):
        WoxAPI.change_query(f"{CloseIn.COMMAND_PREFIX} {potential_match} ", requery=True)

    def schedule_close_of_process(self, process_name, target_time: str, target_date: str):
        if process_name == "_shutdown":
            self.schedule_pc_shutdown(target_time, target_date)
            return

        if not process_name.endswith(".exe"):
            process_name += ".exe"
        task_name = f"wox_plugin_closein_{process_name.rstrip('.exe')}"
        os.system(f'schtasks /create '
                  f'/tn "{task_name}" '
                  f'/sc once '
                  f'/st {target_time} '
                  f'/sd {target_date} '
                  f'/tr "cmd /c \'schtasks /delete /tn {task_name} /f && taskkill /f /im {process_name} /t\'"')

    def parse_time_string(self, time_string):
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

    def calculate_schedule_time_strings(self, parsed_timedelta) -> typing.Tuple[str, str]:
        target_time = datetime.now() + parsed_timedelta
        # Date may need to be set if the target time goes into another day
        target_time_string = target_time.strftime("%H:%M:%S")
        target_date_string = target_time.strftime("%d/%m/%Y")
        return target_time_string, target_date_string

    def schedule_pc_shutdown(self, target_time_string, target_date_string):
        task_name = "wox_plugin_closein_shutdown_pc"
        os.system(f'schtasks /create '
                  f'/tn "{task_name}" '
                  f'/sc once '
                  f'/st {target_time_string} '
                  f'/sd {target_date_string} '
                  f'/tr "cmd /c \'schtasks /delete /tn {task_name} /f && shutdown /s /hybrid /t 0\'"')


if __name__ == '__main__':
    CloseIn()
