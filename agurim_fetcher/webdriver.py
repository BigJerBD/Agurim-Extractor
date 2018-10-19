import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def create_fetcher(url, driver,*, sleeptime=0.75, timeout=120, poll_frequency=1):
    class Fetcher:
        @staticmethod
        def get(kwargs):
            params = "&".join("%s=%s" % (key, value) for key, value in {**kwargs, "outfmt": 'file'}.items())
            driver.get(f"{url}?{params}")
            time.sleep(sleeptime)
            WebDriverWait(driver, timeout, poll_frequency).until(all_download_end)

    return Fetcher


def all_download_end(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script("""
        var items = downloads.Manager.get().items_;
        if (items.every(e => e.state === "COMPLETE"))
            return items.map(e => e.file_url);
        """)


def get_chrome_driver(download_directory, *, executable_path="chromedriver", show=False):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    if not show:
        option.add_argument("--window-position=-32000,-32000")

    return webdriver.Chrome(executable_path,options=option)
