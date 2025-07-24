import re
import requests
from bs4 import BeautifulSoup

def steamtape_get_dl_link(link):
    try:
        if "/e/" in link:
            link = link.replace("/e/", "/v/")

        response = requests.get(link)
        response.raise_for_status() 
        html_source = response.text

        norobot_link_pattern = re.compile(r"document\.getElementById\('norobotlink'\)\.innerHTML = (.+?);")
        norobot_link_matcher = norobot_link_pattern.search(html_source)

        if norobot_link_matcher:
            norobot_link_content = norobot_link_matcher.group(1)

            token_pattern = re.compile(r"token=([^&']+)")
            token_matcher = token_pattern.search(norobot_link_content)

            if token_matcher:
                token = token_matcher.group(1)

                soup = BeautifulSoup(html_source, 'html.parser')
                div_element = soup.select_one("div#ideoooolink[style='display:none;']")

                if div_element:
                    streamtape = div_element.get_text()
                    full_url = f"https:/{streamtape}&token={token}"
                    return f"{full_url}&dl=1s"

    except Exception as exception:
        print(f"An error occurred: {exception}")

    return None
