import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
import glob


def download_audio(youtube_utl, download_path="./static/music", timeout=20, alert_check_timeout=5):
    """Opens a Chrome browser, navigates to the given URL, attempts to convert
    and download audio from a provided YouTube-like URL, and checks for alerts.

    Args:
        url (str): The URL of the MP3 conversion website.
        youtube_utl (str): The YouTube-like URL to convert.
        download_path (str, optional): The directory to save downloaded files.
                                       Defaults to './static/music'.
        timeout (int, optional): The maximum time (in seconds) to wait for initial elements.
                                 Defaults to 20.
        alert_check_timeout (int, optional): The maximum time (in seconds) to wait for an alert
                                             after clicking the convert button. Defaults to 5.
    """
    driver = None
    try:
        os.makedirs(download_path, exist_ok=True)
        abs_download_path = os.path.abspath(download_path)

        chrome_options = Options()
        prefs = {"download.default_directory": os.path.abspath(download_path)}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://cnvmp3.com/v23")
        print(f"Successfully opened cnvmp3")

        wait = WebDriverWait(driver, timeout)

        # Wait for the video URL input field to be present
        video_url_input = wait.until(
            EC.presence_of_element_located((By.ID, "video-url")))
        print("Video URL input field loaded.")

        # Enter the YouTube-like URL
        video_url_input.send_keys(youtube_utl)
        print(f"Entered URL: {youtube_utl}")

        # Click the convert button
        convert_button = wait.until(
            EC.element_to_be_clickable((By.ID, "convert-button-1")))
        convert_button.click()
        print("Clicked the convert button.")

        # Check for alert after clicking convert
        try:
            alert_wait = WebDriverWait(driver, alert_check_timeout)
            alert_wait.until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()  # Or alert.dismiss() depending on the alert
            raise Exception(f"Alert present after conversion: {alert_text}")
        except TimeoutException:
            print("No alert present after conversion (within the specified timeout).")
        except NoAlertPresentException:
            print("No alert present at the moment.")

        time.sleep(30)  # Keep the existing sleep for potential processing
        list_of_files = glob.glob(os.path.join(abs_download_path, "*.mp3"))
        if list_of_files:
            list_of_files.sort(key=os.path.getmtime, reverse=True)
            downloaded_file = list_of_files[0]
            print(
                f"Potentially downloaded file: {os.path.basename(downloaded_file)}")
            return downloaded_file
        else:
            print("No MP3 file found in the download directory within the wait time.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        print("Processing complete.")
        if driver is not None:
            driver.quit()
