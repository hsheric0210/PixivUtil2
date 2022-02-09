import codecs
import sys
import csv
import traceback

import PixivBrowserFactory
import PixivHelper
from PixivException import PixivException


# from bs4 import BeautifulSoup

# TODO This can be parallelized

def export_member_list(caller,
                       config,
                       filename,
                       member_ids):
    dumps = []
    for member_id in member_ids:
        try:
            list_page = None

            # Try to get the member page
            while True:
                try:
                    (artist, list_page) = PixivBrowserFactory.getBrowser().getMemberPage(member_id, 1, False, None, r18mode=config.r18mode, throw_empty_error=False)
                    dumps.append({'member_id': member_id, 'total_images': artist.totalImages})
                    break
                except PixivException as ex:
                    caller.ERROR_CODE = ex.errorCode
                    PixivHelper.print_and_log('info', f'Member ID ({member_id}): {ex}')
                    if ex.errorCode == PixivException.NO_IMAGES:
                        pass
                    else:
                        if list_page is None:
                            list_page = ex.htmlPage
                        if list_page is not None:
                            PixivHelper.dump_html(f"Dump for {member_id} Error Code {ex.errorCode}.html", list_page)
                        if ex.errorCode == PixivException.USER_ID_NOT_EXISTS or ex.errorCode == PixivException.USER_ID_SUSPENDED:
                            PixivHelper.print_and_log('info', f'{member_id} not exist.')
                        if ex.errorCode == PixivException.OTHER_MEMBER_ERROR:
                            PixivHelper.print_and_log(None, ex.message)
                            caller.__errorList.append(dict(type="Member", id=str(member_id), message=ex.message, exception=ex))
                    return
                except AttributeError:
                    # Possible layout changes, try to dump the file below
                    raise
                except BaseException:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback)
                    PixivHelper.print_and_log('error', f'Error at processing Artist Info: {sys.exc_info()}')
            print(f"Result: Name=\"{artist.artistName}\", Total_Images={artist.totalImages}")
        except KeyboardInterrupt:
            raise
        except BaseException:
            PixivHelper.print_and_log('error', 'Error at export_member_list(): {0}'.format(sys.exc_info()))
            raise

    if len(dumps) > 0:
        with codecs.open(filename, 'w', encoding='utf-8') as writer:
            csvwriter = csv.DictWriter(writer, dumps[0].keys())
            csvwriter.writeheader()
            csvwriter.writerows(dumps)
