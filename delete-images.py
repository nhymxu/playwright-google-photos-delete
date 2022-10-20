import os
import time
import pathlib
import typing
from playwright.sync_api import sync_playwright, Page
from playwright._impl._api_types import TimeoutError

# PLAYWRIGHT_BROWSERS_PATH=./pw-browsers python -m playwright install
# PLAYWRIGHT_BROWSERS_PATH=./pw-browsers bpython

GOOGLE_EMAIL = os.getenv('GOOGLE_EMAIL')
GOOGLE_PASSWORD = os.getenv('GOOGLE_PASSWORD')

if not GOOGLE_EMAIL or not GOOGLE_PASSWORD:
    raise ValueError('Please setup Google Account on environment first.')


TIME_CONFIG = {
    'delete_cycle': 20,
    'press_button_delay': 2
}

ELEMENT_SELECTORS = {
    'checkboxClass': '.ckGgle',
    'languageAgnosticDeleteButton': 'div[data-delete-origin] button',
    'deleteButton': 'button[aria-label="Delete"]',
    'confirmationButton': '#yDmH0d > div.llhEMd.iWO5td > div > div.g3VIld.V639qd.bvQPzd.oEOLpc.Up8vH.J9Nfi.A9Uzve.iWO5td > div.XfpsVe.J9fJmf > button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.nCP5yc.kHssdc.HvOprf'
}

playwright = sync_playwright().start()
# browser = playwright.firefox.launch(
#     headless=False,
#     firefox_user_prefs={'permissions.default.image': 2}
# )

browser = playwright.firefox.launch_persistent_context(
    headless=False,
    user_data_dir=pathlib.Path('.') / 'user_data',
)
page: typing.Optional[Page] = None


def google_login():
    page.goto(
        "https://accounts.google.com/signin/v2/identifier?hl=en&flowName=GlifWebSignIn&flowEntry=ServiceLogin",
        wait_until="domcontentloaded"
    )
    page.wait_for_selector('input[type="email"]')
    page.type('input[type="email"]', GOOGLE_EMAIL)
    page.click("#identifierNext")

    page.wait_for_selector('input[type="password"]', state='visible')
    page.type('input[type="password"]', GOOGLE_PASSWORD)
    page.wait_for_selector("#passwordNext", state='visible')
    page.click("#passwordNext")


def process_delete():
    global delete_count

    print('Get checkbox list')
    checkboxes = page.query_selector_all(ELEMENT_SELECTORS['checkboxClass'])
    if not checkboxes:
        print('Empty checkbox select')
        return 'wrong'

    total_checkboxes = len(checkboxes)
    print('Have ', total_checkboxes, 'checkboxes')

    print('Click all checkboxes')
    for e in checkboxes:
        if not e or not e.is_visible():
            continue

        try:
            e.click()
        except TimeoutError as e:
            print('Click timeout')
            continue

    print('Click delete button')
    time.sleep(TIME_CONFIG['press_button_delay'])
    delete_button = page.query_selector('div[data-delete-origin] button')
    delete_button.click()

    print('Confirm delete button')
    time.sleep(TIME_CONFIG['press_button_delay'])
    confirmation_button = page.query_selector(ELEMENT_SELECTORS['confirmationButton'])
    confirmation_button.click()

    delete_count += total_checkboxes
    print('Delete ', delete_count, 'image')


def enter_homepage():
    global page

    if page:
        page.close()

    print('Enter Google Photos homepage')
    page = browser.new_page()
    page.goto("https://photos.google.com/?hl=en", wait_until="networkidle")


# Process
delete_count = 0
round_num = 0

enter_homepage()

while True:
    round_num += 1

    print('----- Round', round_num)

    if round_num % 5 == 0:
        enter_homepage()

    result = process_delete()
    if result == 'wrong':
        break

    print('Sleeping')
    time.sleep(TIME_CONFIG['delete_cycle'])


browser.close()
playwright.stop()
