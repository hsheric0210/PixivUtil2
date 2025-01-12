import codecs
import sys
import csv
import traceback

import PixivBrowserFactory
import PixivHelper
import base64
from PixivException import PixivException
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# from bs4 import BeautifulSoup


def export_member_list(caller,
                       config,
                       filename,
                       member_ids):
    dump_lock = Lock()
    dumps = []
    futures = []

    def func(_member_id):
        list_page = None
        try:
            # Try to get the member page
            while True:
                try:
                    (artist, list_page) = PixivBrowserFactory.getBrowser().getMemberPage(_member_id, 1, False, None, r18mode=config.r18mode, throw_empty_error=False, no_logs=True)
                    with dump_lock:
                        dumps.append({'member_id': _member_id, 'total_images': artist.totalImages, 'token': artist.artistToken, 'member_name': base64.b64encode(artist.artistName.encode('utf-8')).decode('ascii'), 'avatar': artist.artistAvatar})
                        print(f"Result for member \'{_member_id}\': [name=\"{artist.artistName}\", total_images={artist.totalImages}, token=\"{artist.artistToken}\", avatar=\"{artist.artistAvatar}\"]")
                    break
                except PixivException as ex:
                    caller.ERROR_CODE = ex.errorCode
                    PixivHelper.print_and_log('info', f'Member ID ({_member_id}): {ex}')
                    if ex.errorCode == PixivException.NO_IMAGES:
                        pass
                    else:
                        if list_page is None:
                            list_page = ex.htmlPage
                        if list_page is not None:
                            PixivHelper.dump_html(f"Dump for {_member_id} Error Code {ex.errorCode}.html", list_page)
                        if ex.errorCode == PixivException.USER_ID_NOT_EXISTS or ex.errorCode == PixivException.USER_ID_SUSPENDED:
                            PixivHelper.print_and_log('info', f'{_member_id} not exist.')
                        if ex.errorCode == PixivException.OTHER_MEMBER_ERROR:
                            PixivHelper.print_and_log(None, ex.message)
                            caller.__errorList.append(dict(type="Member", id=str(_member_id), message=ex.message, exception=ex))
                    break
                except AttributeError:
                    # Possible layout changes, try to dump the file below
                    raise
                except BaseException:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback)
                    PixivHelper.print_and_log('error', f'Error at processing Artist Info: {sys.exc_info()}')
                    raise
        except KeyboardInterrupt:
            raise
        except BaseException:
            PixivHelper.print_and_log('error', 'Error at export_member_list(): {0}'.format(sys.exc_info()))
            raise

    with ThreadPoolExecutor(max_workers=config.parallelMemberDumpThreads) as executor:
        for member_id in member_ids:
            futures.append(executor.submit(func, member_id))

    for future in futures:
        future.result(timeout=None)

    if len(dumps) > 0:
        with codecs.open(filename, 'w', encoding='utf-8') as writer:
            csvwriter = csv.DictWriter(writer, dumps[0].keys())
            csvwriter.writeheader()
            csvwriter.writerows(dumps)
