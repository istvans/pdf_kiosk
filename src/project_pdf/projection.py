"""Open a PDF, display it in full screen and scroll it constantly."""
from enum import Enum
import functools
import logging
from tkinter.filedialog import askopenfilename
from typing import Callable, List
import time

from selenium import webdriver
from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchWindowException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


_logger = logging.getLogger(__name__)


class Format(Enum):
    KRETA = "Kréta"
    OTHER = "'Másik'"


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


def infinite_loop(scroller: Callable[[int], int], start_index: int = 0):
    index = start_index
    print("Indulás!")
    while True:
        try:
            index = scroller(index)
        except (WebDriverException, NoSuchWindowException) as exc:
            if ("Message: Failed to decode response from marionette" in str(exc) or
                "Message: Browsing context has been discarded" in str(exc)):
                print("Végeztünk. Szia!")
                break
            raise


def infinite_scroll_kreta(driver, content, display_time):
    def scroll_teachers(teachers: List, teacher_index: int) -> int:
        teachers[teacher_index].location_once_scrolled_into_view
        time.sleep(display_time)
        return (teacher_index + 1) % len(teachers)

    teachers = []
    for page in content:
        for (row_index, row) in enumerate(page):
            row_text = ""
            for column in row:
                row_text += column.text
            if "Dátum" in row_text:
                teacher = page[row_index - 1][0]
                teachers.append(teacher)

    infinite_loop(functools.partial(scroll_teachers, teachers), start_index=0)


def infinite_scroll_other(driver, content, display_time):
    def scroll_to_the_end_and_back(scroll_down, scroll_to_top, last_element, _):
        if not _is_element_visible_in_viewpoint(driver, last_element):
            for _ in range(15):
                actions.send_keys(scroll_down).perform()
                time.sleep(0.02)

        time.sleep(display_time)

        if _is_element_visible_in_viewpoint(driver, last_element):
            actions.send_keys(scroll_to_top).perform()
            time.sleep(display_time)

        return -1

    actions = ActionChains(driver)
    scroll_down = Keys.DOWN
    scroll_to_top = Keys.HOME

    last_page = content[-1]
    last_element = last_page[-1][-1]

    time.sleep(display_time)
    infinite_loop(functools.partial(
        scroll_to_the_end_and_back,
        scroll_down,
        scroll_to_top,
        last_element,
    ))


def project_pdf() -> int:
    driver = None
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

        elements = []
        for page in pages:
            elements.append([])
            page_content = elements[-1]
            spans = page.find_elements(By.XPATH, ".//span[string-length(text()) > 0]")
            for span in spans:
                text = span.text.strip()
                if text:
                    page_content.append(span)

        content = []
        for (page_index, page) in enumerate(elements):
            page.sort(key=lambda e: e.location["y"])
            rows = []
            columns = []
            prev = None
            for e in page:
                diff = 0 if (prev is None) else (e.location["y"] - prev.location["y"])
                if diff > 25:
                    columns.sort(key=lambda e: e.location["x"])
                    rows.append(columns[:])
                    columns.clear()

                columns.append(e)
                prev = e

            columns.sort(key=lambda e: e.location["x"])
            rows.append(columns[:])  # add the last row

            content.append(rows)

        display_time = 8

        format_ = None
        for page in content:
            for row in page:
                row_text = ""
                for column in row:
                    if "óra" in column.text:
                        format_ = Format.OTHER
                        break
                    row_text += column.text
                if "Dátum" in row_text:
                    format_ = Format.KRETA
                    break

        if format_ is None:
            raise ValueError(f"Nem sikerült felismerni a PDF formátumát! Új formátum? Támogatott formátumok: {Format}")

        print(f"Felismert formátum: {format_.value}")

        match format_:
            case Format.KRETA:
                infinite_scroll_kreta(driver, content, display_time)
            case Format.OTHER:
                infinite_scroll_other(driver, content, display_time)
    except Exception:
        _logger.exception("Nem várt hiba történt! :( "
                          "Kérlek másold ki a most következő hiba üzenetet (\"traceback\") "
                          "vagy legalább csinálj róla egy képernyő fotót és küld el nekem! "
                          "Bocsi!")
        input("Nyomj egy gombot és az ablak bezárul")
        return 1
    finally:
        if driver:
            try:
                driver.close()
            except InvalidSessionIdException:
                pass  # let it go...

    return 0
