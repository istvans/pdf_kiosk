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


def _is_element_visible_in_viewpoint(driver, element) -> bool:
    """https://stackoverflow.com/questions/45243992/verification-of-element-in-viewport-in-selenium"""
    return driver.execute_script(
        """
        var elem = arguments[0],
        box = elem.getBoundingClientRect(),
        cx = box.left + box.width / 2,
        cy = box.top + box.height / 2,
        e = document.elementFromPoint(cx, cy);
        for (; e; e = e.parentElement) {
            if (e === elem) {
                return true;
            }
        }
        return false;
        """,
        element
    )


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
        last_text = last_page.text.split('\n')[-1]
        last_element = last_page.find_elements(By.XPATH, f"//*[text() = {last_text}]")[-1]

        display_time = 5

        time.sleep(display_time)
        while True:
            try:
                for _ in range(15):
                    actions.send_keys(scroll_down).perform()
                    time.sleep(0.02)

                time.sleep(display_time)

                if (i == (3 * num_pages)) or _is_element_visible_in_viewpoint(driver, last_element):
                    i = 0
                    actions.send_keys(scroll_to_top).perform()
                    time.sleep(display_time)
                else:
                    i += 1
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
        input("Nyomj egy gombot és az ablak bezárul")
        return 1
    finally:
        if driver and (not was_closed):
            try:
                driver.close()
            except InvalidSessionIdException:
                pass  # let it go...

    return 0
