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
    filename = askopenfilename(filetypes=[("PDF", "*.pdf")])
    if not filename:
        print("Nem választottál filet")
        return 1

    driver = webdriver.Firefox()
    was_closed = False
    try:
        driver.get(f"file://{filename}")
        driver.fullscreen_window()
        select = Select(driver.find_element(By.ID, "scaleSelect"))
        select.select_by_value('page-width')
        actions = ActionChains(driver)
        i = 0
        scroll_down = Keys.DOWN
        scroll_to_top = Keys.HOME

        import IPython; IPython.embed()

        while True:
            try:
                for _ in range(20):
                    actions.send_keys(scroll_down).perform()
                    time.sleep(0.02)
                time.sleep(5)
                i += 1
                if i == 3:
                    i = 0
                    actions.send_keys(scroll_to_top).perform()
            except WebDriverException as exc:
                if str(exc) == "Message: Failed to decode response from marionette":
                    was_closed = True
                    print("Bezártad az ablakot")
                    break
                raise
    except Exception:
        _logger.exception("Nem várt hiba történt! :( "
                          "Kérlek másold ki vagy legalább csinálj róla egy képernyő fotót és "
                          "küld el nekem! Bocsi!")
        input("Nyomj egy gombot a bezáráshoz")
        return 1
    finally:
        if not was_closed:
            try:
                driver.close()
            except InvalidSessionIdException:
                pass  # let it go...

    return 0
