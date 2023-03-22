import os
from typing import Optional

from simpleperf_utils import AdbHelper


def install_apk(file: str, grant_perms: bool = False, arg_string: Optional[str] = None, adb: Optional[AdbHelper] = None,
                log_output: bool = False, log_stderr: bool = True) -> bool:
    if not os.path.isfile(file):
        raise FileNotFoundError(f'{file} was not found in directory {os.getcwd()}')

    cmd = ['install']
    if grant_perms:
        cmd += '-g'
    if arg_string is not None:
        cmd += arg_string
    if adb is None:
        adb = AdbHelper()
    return adb.run(adb_args=cmd, log_output=log_output, log_stderr=log_stderr)


def compile_package(pkg: str, mode: str = 'speed', adb: Optional[AdbHelper] = None,
                    log_output: bool = False, log_stderr: bool = True) -> bool:
    args = ['shell', 'cmd', 'package', 'compile', '-m', mode, '-f', pkg]
    if adb is None:
        adb = AdbHelper()
    return adb.run(adb_args=args, log_output=log_output, log_stderr=log_stderr)


def uninstall_package(pkg: str, adb: Optional[AdbHelper] = None, log_output: bool = False,
                      log_stderr: bool = True) -> bool:
    args = ['uninstall', pkg]
    if adb is None:
        adb = AdbHelper()
    return adb.run(adb_args=args, log_output=log_output, log_stderr=log_stderr)
