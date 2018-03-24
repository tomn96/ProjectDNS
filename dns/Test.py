import MissconfigurationInfo as MI
import pandas as PD

DEFUALT_URLS_FILE = "C:\\Users\\Tomeriq\\Documents\\Visual Code\\Python\\ProjectDNS\\dns\\URLs.csv"

GET_URL = 0

def getURLsFromCSV():
    raw_data = PD.read_csv(DEFUALT_URLS_FILE, names=['URL'])
    return raw_data

if __name__ == '__main__':
    url_list = getURLsFromCSV()
    misconfigurations_for_urls = list()
    for url_data in url_list.values:
        misconfigurations_for_urls.append(
            MI.MisconfigurationInfo(url_data[GET_URL]))
    misconfigurations_for_urls[0].find_misconfigurations()
        # print(url.find_misconfigurations(...))
