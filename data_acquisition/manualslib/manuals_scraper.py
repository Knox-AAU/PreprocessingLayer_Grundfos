import os
import subprocess
import sys
import random
import socket

import netifaces
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import urllib
import pydub
import speech_recognition as sr
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.proxy import Proxy, ProxyType

import re

# https://www.manualslib.com/download/2104359/Grundfos-Lc-108.html#product-96841859
FILE_TYPE = ".pdf"
DOMAIN = "https://www.manualslib.com/brand/grundfos/"
DEFAULT_DOMAIN = "https://www.manualslib.com"


def get_download_links():
    current_files = list_current_files()
    read = requests.get(DOMAIN)
    html_content = read.content
    soup = BeautifulSoup(html_content, "html.parser")
    list_of_links = set()
    soup_links = soup.find_all('a')

    pbar = tqdm(total=len(soup_links))
    pbar.set_description("Adding links to list")
    for link in soup_links:
        l = str(link.get('href'))
        if l.startswith("/manual"):
            for file in current_files:
                if file in l:
                    print("This file is already downloaded")
                    break
            l = l.replace("/manual/", "/download/")
            l = l.split(" ", 1)[0]
            list_of_links.add(l)
        pbar.update(1)

    pbar.close()
    print(len(list_of_links))
    get_rechapta(list_of_links)


def get_rechapta(links):
    ip_address, mask, gateway = get_default_network_details()
    interface_name = 'Wi-Fi'
    for link in links:
        l = DEFAULT_DOMAIN + link
        change_ip(interface_name, ip_address, mask, gateway)
        options = webdriver.ChromeOptions()
        # options.add_argument("--user-agent=New User Agent")
        prefs = {'download.default_directory': os.path.join(os.path.abspath(os.curdir), "downloads")}
        options.add_experimental_option('prefs', prefs)
        prox = Proxy()
        prox.proxy_type = ProxyType.AUTODETECT

        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, desired_capabilities=capabilities)
        wait = WebDriverWait(driver, 10)
        driver.get(l)
        try:
            driver.find_element_by_xpath('//button[normalize-space()="AGREE"]').click()
        except:
            print("no cookies needed")
        frames = driver.find_elements_by_tag_name("iframe")
        recaptcha_control_frame = None
        recaptcha_challenge_frame = None
        for index, frame in enumerate(frames):
            if re.search('reCAPTCHA', frame.get_attribute("title")):
                recaptcha_control_frame = frame

            if re.search('recaptcha challenge', frame.get_attribute("title")):
                recaptcha_challenge_frame = frame
        if not (recaptcha_control_frame and recaptcha_challenge_frame):
            print("[ERR] Unable to find recaptcha. Abort solver.")
            sys.exit()
        # switch to recaptcha frame
        time.sleep(random.uniform(5, 15))
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(recaptcha_control_frame)

        # click on checkbox to activate recaptcha
        wait.until(presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox-border")))
        driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border").click()

        # switch to recaptcha audio control frame
        time.sleep(random.uniform(5, 15))
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(recaptcha_challenge_frame)

        wait.until(presence_of_element_located((By.ID, "recaptcha-audio-button")))
        # click on audio challenge
        time.sleep(random.uniform(5, 15))
        driver.find_element(By.ID, "recaptcha-audio-button").click()

        # switch to recaptcha audio challenge frame
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(recaptcha_challenge_frame)


        # get the mp3 audio file
        wait.until(presence_of_element_located((By.ID, "audio-source")))
        src = driver.find_element_by_id("audio-source").get_attribute("src")
        print(f"[INFO] Audio src: {src}")

        path_to_mp3 = os.path.normpath(os.path.join(os.path.abspath(os.curdir), "sample.mp3"))
        path_to_wav = os.path.normpath(os.path.join(os.path.abspath(os.curdir), "sample.wav"))

        # download the mp3 audio file from the source
        urllib.request.urlretrieve(src, path_to_mp3)

        # load downloaded mp3 audio file as .wav
        try:
            sound = pydub.AudioSegment.from_mp3(path_to_mp3)
            sound.export(path_to_wav, format="wav")
            sample_audio = sr.AudioFile(path_to_wav)
        except Exception:
            sys.exit(
                "[ERR] Please run program as administrator or download ffmpeg manually, "
                "https://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/"
            )

        # translate audio to text with google voice recognition
        r = sr.Recognizer()
        with sample_audio as source:
            audio = r.record(source)
        key = r.recognize_google(audio)
        print(f"[INFO] Recaptcha Passcode: {key}")

        # key in results and submit
        time.sleep(random.uniform(5, 15))
        driver.find_element_by_id("audio-response").send_keys(key.lower())
        driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)



        driver.switch_to.default_content()
        time.sleep(random.uniform(5, 15))
        wait.until(presence_of_element_located((By.ID, "get-manual-button")))

        driver.find_element_by_id("get-manual-button").click()

        time.sleep(2)

        wait.until(presence_of_element_located((By.CLASS_NAME, "download-url")))
        driver.find_element_by_xpath('//a[normalize-space()="Download PDF"]').click()

        time.sleep(random.uniform(20, 35))  # may needs to be increased, depends on internet speed
        print("downloaded")

        driver.close()

    return


def list_current_files():
    files = set()
    if not os.path.exists(os.path.join(os.path.abspath(os.curdir), "downloads")):
        print("Created output folder")
        os.mkdir(os.path.join(os.path.abspath(os.curdir), "downloads"))
        return files
    for file in os.listdir(os.path.join(os.path.abspath(os.curdir), "downloads")):
        if file.endswith(".pdf"):
            f = file.replace(".pdf", "")
            files.add(f)
    return files


def change_ip(interface_name, ip_address, mask, gateway):
    ip_address = '.'.join(ip_address.split('.')[:-1]) + '.' + str(
        random.randrange(8, 255 - int(mask.split('.')[-1]) - 1))
    result_1 = subprocess.call(
        f'netsh interface ipv4 set address name="{interface_name}" static {ip_address} {mask} {gateway}', shell=True)
    result_2 = subprocess.call(f'netsh interface ipv4 set dns name="{interface_name}" static 8.8.8.8', shell=True)
    if result_1 == 1 or result_2 == 1:
        print("[WARN] Unable to change IP. Run the program with admin rights.")
        sys.exit()
    print(f"[INFO] New IP Address is: {ip_address}")
    return True


def get_default_network_details():
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address

    ip_address = get_ip_address()
    for i in netifaces.interfaces():
        try:
            if str(netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']) == str(ip_address):
                print("[INFO] *Default Network Details*")
                print("[INFO] IP Address: ", ip_address)
                print("[INFO] Mask: ", netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'])
                print("[INFO] Gateway: ", netifaces.gateways()['default'][netifaces.AF_INET][0])
                return ip_address, \
                        netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask'], \
                        netifaces.gateways()['default'][netifaces.AF_INET][0]
        except Exception:
            pass




if __name__ == "__main__":
    print("Initiating the scaper")
    get_download_links()

dict = {1: "147.135.255.62:8278", 2: "195.154.67.61:3128"}
