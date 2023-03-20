from typing import Union, List

from simpleperf_utils import AdbHelper


def get_logcat_for_aut(aut: str, adb: AdbHelper) -> Union[str, None]:
    status, pid = adb.run_and_return_output(['shell', 'pidof', aut])
    if not status:
        print("failed to get pid")
        return None
    print(pid)
    status, logcat_str = adb.run_and_return_output(
        ['shell', 'logcat', '-d', '--pid=' + str(pid)], True, True)
    if not status:
        print("something went wrong with logcat!")
        return None
    return logcat_str


def filter_logcat_str_for_tags(logcat: List[str], tags: Union[str, List[str]]) -> List[str]:
    if isinstance(tags, str):
        def filter_fun(line):
            return tags in line
    elif isinstance(tags, List):
        def filter_fun(line):
            return any(tag in line for tag in tags)
    else:
        raise TypeError(f'Unknown type for tags: {type(tags)}')

    return list(filter(filter_fun, logcat))


def split_logcat(logcat: str, latest_first: bool = True) -> List[str]:
    log_list = logcat.split('\n')
    if latest_first:
        log_list.reverse()
    return log_list
