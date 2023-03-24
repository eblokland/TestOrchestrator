import os
from typing import Optional

from simpleperf_utils import AdbHelper


def install_apk(file: str, grant_perms: bool = False, arg_string: Optional[str] = None, adb: Optional[AdbHelper] = None,
                log_output: bool = False, log_stderr: bool = True) -> bool:
    if not os.path.isfile(file):
        raise FileNotFoundError(f'{file} was not found in directory {os.getcwd()}')

    cmd = ['install']
    if grant_perms:
        cmd += ['-g']
    if arg_string is not None:
        cmd += arg_string
    if adb is None:
        adb = AdbHelper()
    cmd += [file]
    print(f'Installing apk with args {cmd}')
    return adb.run(adb_args=cmd, log_output=log_output, log_stderr=log_stderr)


def compile_package(pkg: str, mode: str = 'speed', adb: Optional[AdbHelper] = None,
                    log_output: bool = False, log_stderr: bool = True) -> bool:
    args = ['shell', 'cmd', 'package', 'compile', '-m', mode, '-f', pkg]
    if adb is None:
        adb = AdbHelper()
    print(f'Compiling package with args {args}')
    return adb.run(adb_args=args, log_output=log_output, log_stderr=log_stderr)


def uninstall_package(pkg: str, adb: Optional[AdbHelper] = None, log_output: bool = False,
                      log_stderr: bool = True) -> bool:
    args = ['uninstall', pkg]
    if adb is None:
        adb = AdbHelper()
    print(f'Uninstalling package with args {args}')
    return adb.run(adb_args=args, log_output=log_output, log_stderr=log_stderr)


def kill_app(pkg: str, adb: Optional[AdbHelper], log_output: bool = False, log_stderr: bool = True):
    args = ['shell', 'am', 'force-stop', pkg]
    if adb is None:
        adb = AdbHelper()
    print(f'Stopping package {pkg}')
    return adb.run(adb_args=args, log_output=log_output, log_stderr=log_stderr)
