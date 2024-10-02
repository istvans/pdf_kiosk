"""Open a PDF, display it in full screen and scroll it constantly."""
from tkinter.filedialog import askopenfilename
import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select


def project():
    filename = askopenfilename()

    driver = webdriver.Firefox()
    was_closed = False
    try:
        driver.get(f"file://{filename}")
        driver.fullscreen_window()
        select = Select(driver.find_element("css selector", "#scaleSelect"))
        select.select_by_value('page-width')
        actions = ActionChains(driver)
        i = 0
        scroll_down = Keys.DOWN
        scroll_to_top = Keys.HOME
        while True:
            try:
                actions.send_keys(scroll_down)
                actions.send_keys(scroll_down)
                actions.send_keys(scroll_down)
                actions.perform()
                time.sleep(2)
                i += 1
                if i == 20:
                    i = 0
                    actions.send_keys(scroll_to_top)
                    actions.perform()
            except WebDriverException:
                was_closed = True
                print("Bye!")
                break
    finally:
        if not was_closed:
            driver.close()
