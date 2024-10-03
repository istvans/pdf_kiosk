"""Open a PDF, display it in full screen and scroll it constantly."""
import logging
from tkinter.filedialog import askopenfilename
import time

from selenium import webdriver
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


_logger = logging.getLogger(__name__)


def project_pdf() -> int:
    driver = None
    was_closed = False

    try:
        filename = askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not filename:
            print("Nem választottál file-t. Végeztünk. Szia!")
            return 1

        driver = webdriver.Firefox()

        driver.get(f"file://{filename}")
        driver.fullscreen_window()
        select = Select(driver.find_element(By.ID, "scaleSelect"))
        select.select_by_value('page-width')

        pages = driver.find_elements(By.CLASS_NAME, "page")
        num_pages = len(pages)

        print(f"A doksinak {num_pages} oldala van.")

        actions = ActionChains(driver)
        i = 0
        scroll_down = Keys.DOWN
        scroll_to_top = Keys.HOME

        last_page = pages[-1]
        end_of_last_page = last_page.find_element(By.CLASS_NAME, "endOfContent")

        import IPython; IPython.embed()
        raise NotImplementedError()

        while True:
            try:
                time.sleep(7)

                for _ in range(20):
                    actions.send_keys(scroll_down).perform()
                    time.sleep(0.02)

                rached_end_of_last_page = last_page.location["y"] < end_of_last_page.location["y"]

                i += 1
                if i == (3 * num_pages):
                    i = 0
                    actions.send_keys(scroll_to_top).perform()
            except WebDriverException as exc:
                if "Message: Failed to decode response from marionette" in str(exc):
                    was_closed = True
                    print("Végeztünk. Szia!")
                    break
                raise
    except Exception:
        _logger.exception("Nem várt hiba történt! :( "
                          "Kérlek másold ki a most következő hiba üzenetet (\"traceback\") "
                          "vagy legalább csinálj róla egy képernyő fotót és küld el nekem! "
                          "Bocsi!")
        print("Kérlek zárd be a böngésző ablakot (ha még nyitva van)!")
        input("Nyomj egy gombot és az ablak bezárul")
        return 1
    finally:
        if driver and (not was_closed):
            try:
                driver.close()
            except InvalidSessionIdException:
                pass  # let it go...

    return 0
