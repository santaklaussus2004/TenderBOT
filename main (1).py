import requests 
from urllib.parse import urljoin
from pdf import extract_text_from_file, extract_docx_text, extract_pdf_text,extract_pdf_text_ocr
from llm import ChatGPTClient
import re
import json
from urllib.parse import quote
import time
from pathlib import Path
from dateutil.relativedelta import relativedelta
import json
from safe_get import safe_get
from search import search
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from parsing_company import parse_company_info
from set_dates import set_end_dates

from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import time
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from generate_search_queries import generate 

# base_urls = ["https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%A1%D0%BF%D0%BE%D1%80%D1%82+%D0%BF%D0%BE%D0%BA%D1%80%D1%8B%D1%82%D0%B8%D0%B5&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=&smb=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D0%BF%D0%BE%D1%80%D1%82+%D0%BF%D0%BB%D0%BE%D1%89%D0%B0%D0%B4%D0%BA%D0%B0&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%B8%D1%81%D0%BA%D1%83%D1%81%D1%81%D1%82%D0%B2%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9+%D0%B3%D0%B0%D0%B7%D0%BE%D0%BD&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%BC%D0%B0%D1%84&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%B4%D0%B5%D1%82%D1%81%D0%BA%D0%B0%D1%8F+%D0%BF%D0%BB%D0%BE%D1%89%D0%B0%D0%B4%D0%BA%D0%B0&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D0%BF%D0%BE%D1%80%D1%82+%D0%B7%D0%B0%D0%BB&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%82%D1%80%D0%B5%D0%BD%D0%B0%D0%B6%D0%B5%D1%80%D0%BD%D1%8B%D0%B9+%D0%B7%D0%B0%D0%BB&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%82%D1%80%D0%B5%D0%BD%D0%B0%D0%B6%D0%B5%D1%80&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%BC%D1%83%D0%BB%D1%8C%D1%82%D0%B8%D0%BC%D0%B5%D0%B4%D0%B8%D1%8F&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%B1%D0%BB%D0%B0%D0%B3%D0%BE%D1%83%D1%81%D1%82%D1%80%D0%BE%D0%B9%D1%81%D1%82%D0%B2%D0%BE&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%BF%D0%B0%D1%80%D0%BA%D0%B5%D1%82&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%BA%D1%80%D0%B5%D1%81%D0%BB%D0%B0&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D0%B8%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D0%BF%D0%BE%D1%80%D1%82+%D0%B8%D0%BD%D0%B2%D0%B5%D0%BD%D1%82%D0%B0%D1%80%D1%8C&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%82%D0%B5%D0%B0%D1%82%D1%80%D1%8B&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D0%BA%D0%B8%D0%BD%D0%BE%D1%82%D0%B5%D0%B0%D1%82%D1%80%D1%8B&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D1%82%D0%B0%D0%B4%D0%B8%D0%BE%D0%BD%D1%8B&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%88%D0%BA%D0%BE%D0%BB%D1%8B&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%81%D0%BF%D0%BE%D1%80%D1%82+%D0%BA%D0%BE%D0%BC%D0%BF%D0%BB%D0%B5%D0%BA%D1%81&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D=","https://goszakup.gov.kz/ru/search/announce?filter%5Bname%5D=%D1%82%D1%80%D0%B8%D0%B1%D1%83%D0%BD%D1%8B&search=&filter%5Bcustomer%5D=&filter%5Bnumber%5D=&filter%5Byear%5D=&filter%5Bstatus%5D%5B%5D=350&filter%5Bamount_from%5D=6000000&filter%5Bamount_to%5D=&filter%5Btrade_type%5D=&filter%5Btype%5D=&filter%5Bstart_date_from%5D=&filter%5Bstart_date_to%5D=&filter%5Bend_date_from%5D=&filter%5Bend_date_to%5D=&filter%5Bitog_date_from%5D=&filter%5Bitog_date_to%5D="]



from bs4 import BeautifulSoup
llm = ChatGPTClient()
magic_base_url = "https://goszakup.gov.kz/ru/announce/actionAjaxModalShowFiles"

base_url = "https://goszakup.gov.kz/"

_,base_urls = generate()
print(base_urls)

# i = 0
while True:
    print("I am awake!")
    today = datetime.now()
    for i,url in enumerate(base_urls):

        date_from = today.strftime("%d.%m.%Y")
        # date_from = (today - relativedelta(months=6)).strftime("%d.%m.%Y")
        
        filename = Path(today.strftime("%d.%m.%Y") + ".json")
        if not filename.exists():
            with filename.open("w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=2)
        forward_url = set_end_dates(url,date_from)
        print(forward_url)
        # one_tender = False
        for page in range(1,1001):
            current_url = f"{forward_url}&count_record=50&page={page}"

            response = safe_get(current_url, timeout=(10, 120), retries=3)
            if response is None:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.select('#search-result a[href*="/ru/announce/index/"]')
            print("FINAL URL:", response.url)
            print("STATUS:", response.status_code)
            print("LINKS:", len(links))
            if len(links) == 0:
                print(f"URL NUMBER {i} ON PAGE {page} HAS NOTHING")
                break
            




            for link in links:
                tender_url = urljoin(base_url,link["href"])
                tender = {
                    "source":current_url,
                    "url":tender_url,
                    "general":{},
                    "documents":[],
                    "winners":[],


                }
                full_url = urljoin(base_url,link["href"])
                response_general = safe_get(full_url)
                with open(filename,'r',encoding='utf8') as file:
                    data = json.load(file)
                already = False
                for obj in data:
                    if obj["url"] == tender_url:
                        already = True
                if already == True:
                    print(f"Пропускаем {tender_url}, он уже есть")
                    continue

                    



                full_url = urljoin(base_url,link["href"])
                response_general = safe_get(full_url, timeout=(10, 120), retries=3)
                soup_general = BeautifulSoup(response_general.text,"html.parser")
                panel = soup_general.select_one(".panel-body")
                if response_general is None:
                    continue

                for group in panel.select(".form-group"):
                    label = group.select_one("label")
                    input_tag = group.select_one("input")
                    if not label or not input_tag:
                        continue 
                        
                    key = label.get_text(" ", strip=True).lower()
                    value = input_tag.get("value", "").strip()
                    tender["general"][key] = value

                trash = llm.ask("ВОТ НАША КОМПАНИЯ  -  ТОО «ASTANA TECH-GROUP» занимается проектированием, строительством и комплексным оснащением спортивных, культурных и образовательных объектов под ключ. Компания поставляет и монтирует спортивные покрытия, паркет, искусственный газон, тартан, спортивное оборудование и тренажёры, трибуны и кресла, мультимедийное, звуковое и слаботочное оборудование. Также выполняет устройство футбольных и спортивных площадок, ледовых арен, воздухоопорных сооружений, ограждений, МАФ и благоустройство территорий, а также оснащает учебные и актовые залы.Посмотри по нашей ли теме этот тендер, и ответь одним словом - да или нет,твой лимит 1 слово ВСЕГДА", json.dumps(tender["general"], ensure_ascii=False)).lower()
                print(f"ОТВЕТ ЛЛМКИ - {trash}")
                if trash == "нет":
                    # trash = llm.ask("Посмотри по нашей ли теме этот тендер, и ответь одним словом - да или нет,твой лимит 1 слово ВСЕГДА", value).lowercase()
                    trash = True 
                    print(f"Мусор - {link}")
                    filename = Path("trash.json")
                    if not filename.exists():
                        with filename.open("w", encoding="utf-8") as file:
                            json.dump([], file, ensure_ascii=False, indent=2)
                    with open(filename,'r',encoding='utf8') as file:
                        garbages = json.load(file)
                    already = False
                    for garbage in garbages:
                        if garbage["general"]["номер объявления"] == garbage["general"]["номер объявления"]:
                            already = True
                            break 
                    if already == False:
                        garbages.append(tender)
                        with open(filename,'w',encoding='utf8') as file:
                            json.dump(garbages, file, ensure_ascii=False, indent=2)


                    continue
                else:
                    print(f"НЕ МУСОР")
                    tender["general"]["Подходит?"] = trash

                    trash = False
                # if trash == True:
                #     print(f"Мусор - {link}")
                #     break 

                
                


                url_document = full_url + "?tab=documents"

                url_winner = full_url + "?tab=winners"
                
                response_document = safe_get(url_document, timeout=(10, 120), retries=3)

                response_winner = safe_get(url_winner, timeout=(10, 120), retries=3)
                soup_document = BeautifulSoup(response_document.text,"html.parser")
                soup_winner = BeautifulSoup(response_winner.text,'html.parser')
                rows_document = soup_document.select("tr")
                # response_general = safe_get(full_url, timeout=(10, 120), retries=3)
                # soup_general = BeautifulSoup(response_general.text,"html.parser")
                # panel = soup_general.select_one(".panel-body")
                # if response_general is None:
                #     continue

                # for group in panel.select(".form-group"):
                #     label = group.select_one("label")
                #     input_tag = group.select_one("input")
                #     if not label or not input_tag:
                #         continue 
                        
                #     key = label.get_text(" ", strip=True).lower()
                #     value = input_tag.get("value", "").strip()
                #     tender["general"][key] = value
                

                rows_winner = soup_winner.select("tbody tr")
                # print(soup_winner)
                # break
                # print(rows_winner)
                no_winner = False
                for lot_a in soup_winner.select("a.lot-links"):
                    row = lot_a.find_parent("tr")
                    if not row:
                        continue
                    cells = row.find_all("td", recursive=False)

                    if len(cells) < 5:
                        continue
                    lot_number = cells[0].get_text(" ",strip=True)
                    lot_name = cells[1].get_text(" ",strip=True)
                    lot_amount = cells[2].get_text(" ",strip=True)
                    lot_status = cells[3].get_text(" ",strip=True)
                    lot_winner = cells[4].get_text(" ",strip=True)
                    match = re.search(r"\d{12}", lot_winner)

                    if match:
                        winner_iin = match.group(0)
                    else:
                        winner_iin = None
                    
                    lot_second_winner = cells[5].get_text(" ",strip=True)
                    
                    winner_data = {
                "lot_number": lot_number,
                "lot_name": lot_name,
                "amount": lot_amount,
                "status": lot_status,
                "winner_name": lot_winner,
                "second_place_name": lot_second_winner
            }

                    if winner_iin:
                        winner_data["winner_iin"] = winner_iin
                        
                    #заметка - доббавлять те web links которые совпали по иину и сохранять их как список в ключе winners.
                    if lot_winner:


                        daddy_yes = False
                        query = winner_iin or lot_winner
                        search_url = (
                            "https://ba.prg.kz/list/"
                            f"?page=1&pageSize=10&text={quote(query)}"
                        )

                        response = safe_get(search_url, timeout=(10, 30), retries=3)
                        if response is not None:
                            soup = BeautifulSoup(response.text, "html.parser")
                        else:
                            soup = None
                        # soup = BeautifulSoup(response.text,'html.parser')
                        company_url = None

                        for a in soup.select("a[href]"):
                            href = a.get("href", "")

                            if winner_iin and winner_iin in href:
                                company_url = urljoin("https://ba.prg.kz", href)
                                break

                        if company_url:
                            company_response = safe_get(
                                company_url,
                                timeout=(10, 30),
                                retries=3
                            )

                            company_soup = BeautifulSoup(
                                company_response.text,
                                "html.parser"
                            )
                            daddy_yes = True
                        else:
                            print("Компания на Daddy не найдена")
                            daddy_yes = False
                        
                        if daddy_yes == True:
                            
                            contacts_section = company_soup.select_one("#contacts")
                            print(f"CONTACTS SECTION:{contacts_section}")

                            phone = None
                            email = None
                            is_active = None 
                            has_violations = None
                            if contacts_section:
                                phone_tag = contacts_section.select_one('a[href^="tel:"]')
                                email_tag = contacts_section.select_one('a[href^="mailto:"]')

                                if phone_tag:
                                    phone = phone_tag.get_text(strip=True)

                                if email_tag:
                                    email = email_tag.get_text(strip=True)
                            winner_data["phone_number"] = phone 
                            winner_data["email"] = email
                            about_section = company_soup.select_one("#about")

                            if about_section:
                                about_text = about_section.get_text(" ", strip=True).lower()

                                # По твоему правилу:
                                # если есть дата окончания регистрации — компания неактивна
                                is_active = "дата окончания регистрации" not in about_text
                            else:
                                is_active = None


                            # -------------------------
                            # НАРУШЕНИЯ
                            # -------------------------

                            registry_section = company_soup.select_one("#registry")

                            has_violations = False
                            violations = []

                            if registry_section:
                                for entry in registry_section.select(".registry-entry"):
                                    entry_text = entry.get_text(" ", strip=True)

                                    value_tag = entry.select_one(".name .capitalize")
                                    value = (
                                        value_tag.get_text(" ", strip=True).lower()
                                        if value_tag
                                        else ""
                                    )

                                    classes = entry.get("class", [])

                                    # На плохих записях обычно будет "Да"
                                    # либо красный/оранжевый класс
                                    if (
                                        value == "да"
                                        or "red" in classes
                                        or "orange" in classes
                                    ):
                                        has_violations = True
                                        violations.append(entry_text)


                            winner_data["is_active"] = is_active
                            winner_data["has_violations"] = has_violations
                            winner_data["violations"] = violations
                            winner_data["web_link"] = company_url
                            if winner_data["phone_number"] != None or winner_data["email"] != None:
                                daddy_yes = True
                                message = llm.ask("""Твоя задача писать сообщения рекламу нашей компании основываясь на инфе о нашей компании, и об инфе о выигранном тендере, и об инфе о победителях тендера. Сообщение адресовано победителям. Если тендер закончился давно, то просто предложи им наши услуги в будущих их начинаниях. Если недавно, спроси нужно ли им еще что-то. Наша компания:ASTANA TECH-GROUP
                Целью нашей компании является совершенствование работ по 
                управлению процессов в сфере строительства. Наша команда объединяет 
                в себе группу компаний в различных направлениях строительной 
                отрасли, а именно:
                • Строительство и комплексное оснащение, а также проектирование 
                спортивных объектов.
                • Поставка спортивных покрытий, сопутствующих материалов для 
                открытых и закрытых спортивных сооружений.
                • Поставка и монтаж театральных и спортивных кресел
                • Поставка и монтаж мультимедийного и слаботочного оборудования
                • Поставка и монтаж телескопических три
                Комплексное оснащение строительных объектов товарами 
                технологического направления (ТХ) 
                • Поставка и устройство профессионального спортивного покрытия для 
                футбола и легкой атлетики (сертификация FIFA и IAAF)
                • Поставка МАФ (малых архитектурных форм) для терских площадок 
                скверов и парков
                                        ТОО «ASTNA TECH-GROUP» БИН 260340004451 010000, РК, г. Астана, ул. Рыскулов, 22. АО «Банк ЦентрКредит» БИК KCJBKZKX ИИК KZ7818562203153343992 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ ТОО «ASTANA TECH-GROUP» выражает Вам свое уважение и предлагает комплексные решения по оснащению спортивных, и культурно образовательных объектов «под ключ». Мы обеспечиваем полный цикл работ, от подбора оборудования и проектирования до поставки, монтажа и ввода в эксплуатацию в том числе: портивные покрытия и оборудование - Системы спортивного паркета — профессиональные покрытия для спортивных залов, соответствующие международным стандартам, обеспечивающие амортизацию, безопасность и долговечность. - Спортивные сиденья и телескопические трибуны для стадионов открытого и закрытого вида, спортивных манежей и спортивных арен. -Спортивные покрытия для фитнесса залов, легкой атлетики, залов для различных видов единоборств. - Напольные покрытия (коммерческий и спортивный линолеум) — качественные решения для учебных и общественных помещений с высокой проходимостью. - Полное оснащение спортивных залов — поставка всего необходимого инвентаря (ворота, щиты, сетки, маты и др.) с учетом специфики объекта. - Оснащение залов всех видов единоборств (борьба, бокс, мма, легкая атлетика, тяжелая атлетика и др…), как для тренировок, так и для профессиональных игр.  - Тренажеры — профессиональные и любительские тренажеры для оснащения залов различного уровня. снащение актовых залов и культурных пространств - Театральные кресла — эргономичные и износостойкие кресла для актовых залов, конференц-залов, кинозалов и театров с возможностью индивидуальной комплектации. - Звуковое оборудование и акустика — профессиональные аудиосистемы, мультимедиа, обеспечивающие качественное звучание для театральных и актовых залов, стадионов и арен любого масштаба. - Музыкальные инструменты — поставка инструментов для образовательных учреждений и культурных центров. снащение образовательных учреждений - Оснащение классов оргтехникой — современные решения для учебного процесса (компьютеры, принтеры, периферия). - Интерактивные панели — инновационные средства обучения, повышающие вовлеченность и эффективность образовательного процесса. лагоустройство территории - Малые архитектурные формы (МАФы) — детские комплексы, скамейки, урны, навесы и другие элементы для комфортного обустройства общественных пространств и территорий. - Уличные покрытия для спортивных площадок — износостойкие и погодоустойчивые покрытия для открытых площадок (резиновая крошка, полиуретан и др.). - Поставка и монтаж покрытий для футбола, легкой атлетики и других видов дисциплин.   - Ограждения спортивных площадок — надежные металлические конструкции для обеспечения безопасности и зонирования территории. Будем рады взаимовыгодному сотрудничеству и готовы предоставить индивидуальное коммерческое предложение с учетом Ваших задач и бюджета.          
                Имея опыт более 16 лет в данном направлении, выполнял работы по поставке и монтажу спортивных покрытий и спортивного инвентаря, спортивных и театральных кресел на таких объектах как:
        1.	Жекпе Жек Сарайы (дворец единоборств) в г. Астана. Оснащение и монтаж спортивных трибун, спортивного паркета (3500м2), спорт инвентаря, рингов, помостов, татами, маты, футбольного поля итд. 
        2.	ЛАСК «Казахстан» (легкоатлетический спортивный комплекс) в г. Астана. Проектирование. Устройство бетонного основания под беговую дорожку (вираж), поставка и монтаж спортивного покрытия для беговой дорожки. Поставка спортивного оборудования и инвентаря для легкой атлетики. Получения сертификата 1 категории ИААФ.
        3.	Конгресс центр на 2045 мест в г. Шымкент. Поставка и монтаж театральных кресел.
        4.	Работа по оснащению комфортных школ (Биайгрупп, Базис, Интегра и др…). Актовый зал (кресла), спорт зал (инвентарь), МАФы, кабинеты. По Казахстану. Более 50 школ за два года.
        5.	ДС Алатау в г. Астана. Поставка и монтаж профессионального спортивного паркета.
        6.	Стадион футбольный в г. Туркестан. Поставка и монтаж беговой дорожки вокруг поля.
        7.	Олимпийская деревня. Каскелен. Поставка и монтаж беговой дорожки.
        8.	Теннисный центр в г. Кызылорда. Поставка и монтаж спортивного паркета 1800 м2.
        9.	СК им. Б. Саттарханова в г. Астана. Поставка и монтаж спортивного паркета 800 м2. Оснащение тренажерного зала.
        10.	Кокшетау Арена в г. Кокшетау. Полное оснащение спортивным инвентарем в залах бокса, борьбы, фитнесс, также в залах для игр в футбол, баскетбол, волейбол. Поставка и монтаж спортивного паркета 2500 м2, трибуны, спортивные сиденья, скалодром.
        11.	Шабыт в г. Астана. Поставка и монтаж спортивного инвентаря, монтаж театральных кресел большого и малого зала.
        12.	Стадион Мунайтпасова в г. Астана. Поставка и монтаж спортивных сидений.  
        13.	 Школы «НИШ». В 2010-2017 гг.. уличные спортивные площадки, 
        стадионы. Оснащение спортзалов, спортивное покрытие для спортзалов (паркет, линолеум).
        14.	 Школы «Бином».  В 2020 – 2023 гг. Телескопические трибуны, кресла для кинозалов.
        Пиши будто ты общаешься с победителем тендера. Только с ним
                                        
                                                
                                                """,f"""Инфа о тендере:{tender},инфа о победителях:{winner_data}""")
                                # message = "Временно нет"
                                winner_data["message"] = message
                                # result = parse_company_info(response.text)
                                # winner_data.update(result)
                                winner_data["message"] = message
                                tender["winners"].append(winner_data)   
                            else:
                                daddy_yes = False                     






                        # for web_link in web_links:
                        #     if "https://ba.prg.kz/" in web_link and winner_iin in web_link:
                        #         daddy_yes = True
                        #         daddy_url = web_link 
                        #         break
                        # if daddy_yes == True:
                        #     print(f"Dadddy is here")
                        #     response = safe_get(daddy_url,timeout=(10, 120), retries=3) 
                        #     soup = BeautifulSoup(response.text,'html.parser')

    #                         contacts_section = soup.select_one("#contacts")
    #                         print(f"CONTACTS SECTION:{contacts_section}")

    #                         phone = None
    #                         email = None

    #                         if contacts_section:
    #                             phone_tag = contacts_section.select_one('a[href^="tel:"]')
    #                             email_tag = contacts_section.select_one('a[href^="mailto:"]')

    #                             if phone_tag:
    #                                 phone = phone_tag.get_text(strip=True)

    #                             if email_tag:
    #                                 email = email_tag.get_text(strip=True)
    #                         winner_data["phone_number"] = phone 
    #                         winner_data["email"] = email
    #                         message = llm.ask("""Твоя задача писать сообщения рекламу нашей компании основываясь на инфе о нашей компании, и об инфе о выигранном тендере, и об инфе о победителях тендера. Сообщение адресовано победителям. Если тендер закончился давно, то просто предложи им наши услуги в будущих их начинаниях. Если недавно, спроси нужно ли им еще что-то. Наша компания:ASTANA TECH-GROUP
    #         Целью нашей компании является совершенствование работ по 
    #         управлению процессов в сфере строительства. Наша команда объединяет 
    #         в себе группу компаний в различных направлениях строительной 
    #         отрасли, а именно:
    #         • Строительство и комплексное оснащение, а также проектирование 
    #         спортивных объектов.
    #         • Поставка спортивных покрытий, сопутствующих материалов для 
    #         открытых и закрытых спортивных сооружений.
    #         • Поставка и монтаж театральных и спортивных кресел
    #         • Поставка и монтаж мультимедийного и слаботочного оборудования
    #         • Поставка и монтаж телескопических три
    #         Комплексное оснащение строительных объектов товарами 
    #         технологического направления (ТХ) 
    #         • Поставка и устройство профессионального спортивного покрытия для 
    #         футбола и легкой атлетики (сертификация FIFA и IAAF)
    #         • Поставка МАФ (малых архитектурных форм) для терских площадок 
    #         скверов и парков
    #                                 ТОО «ASTNA TECH-GROUP» БИН 260340004451 010000, РК, г. Астана, ул. Рыскулов, 22. АО «Банк ЦентрКредит» БИК KCJBKZKX ИИК KZ7818562203153343992 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ ТОО «ASTANA TECH-GROUP» выражает Вам свое уважение и предлагает комплексные решения по оснащению спортивных, и культурно образовательных объектов «под ключ». Мы обеспечиваем полный цикл работ, от подбора оборудования и проектирования до поставки, монтажа и ввода в эксплуатацию в том числе: портивные покрытия и оборудование - Системы спортивного паркета — профессиональные покрытия для спортивных залов, соответствующие международным стандартам, обеспечивающие амортизацию, безопасность и долговечность. - Спортивные сиденья и телескопические трибуны для стадионов открытого и закрытого вида, спортивных манежей и спортивных арен. -Спортивные покрытия для фитнесса залов, легкой атлетики, залов для различных видов единоборств. - Напольные покрытия (коммерческий и спортивный линолеум) — качественные решения для учебных и общественных помещений с высокой проходимостью. - Полное оснащение спортивных залов — поставка всего необходимого инвентаря (ворота, щиты, сетки, маты и др.) с учетом специфики объекта. - Оснащение залов всех видов единоборств (борьба, бокс, мма, легкая атлетика, тяжелая атлетика и др…), как для тренировок, так и для профессиональных игр.  - Тренажеры — профессиональные и любительские тренажеры для оснащения залов различного уровня. снащение актовых залов и культурных пространств - Театральные кресла — эргономичные и износостойкие кресла для актовых залов, конференц-залов, кинозалов и театров с возможностью индивидуальной комплектации. - Звуковое оборудование и акустика — профессиональные аудиосистемы, мультимедиа, обеспечивающие качественное звучание для театральных и актовых залов, стадионов и арен любого масштаба. - Музыкальные инструменты — поставка инструментов для образовательных учреждений и культурных центров. снащение образовательных учреждений - Оснащение классов оргтехникой — современные решения для учебного процесса (компьютеры, принтеры, периферия). - Интерактивные панели — инновационные средства обучения, повышающие вовлеченность и эффективность образовательного процесса. лагоустройство территории - Малые архитектурные формы (МАФы) — детские комплексы, скамейки, урны, навесы и другие элементы для комфортного обустройства общественных пространств и территорий. - Уличные покрытия для спортивных площадок — износостойкие и погодоустойчивые покрытия для открытых площадок (резиновая крошка, полиуретан и др.). - Поставка и монтаж покрытий для футбола, легкой атлетики и других видов дисциплин.   - Ограждения спортивных площадок — надежные металлические конструкции для обеспечения безопасности и зонирования территории. Будем рады взаимовыгодному сотрудничеству и готовы предоставить индивидуальное коммерческое предложение с учетом Ваших задач и бюджета.          
    #         Имея опыт более 16 лет в данном направлении, выполнял работы по поставке и монтажу спортивных покрытий и спортивного инвентаря, спортивных и театральных кресел на таких объектах как:
    # 1.	Жекпе Жек Сарайы (дворец единоборств) в г. Астана. Оснащение и монтаж спортивных трибун, спортивного паркета (3500м2), спорт инвентаря, рингов, помостов, татами, маты, футбольного поля итд. 
    # 2.	ЛАСК «Казахстан» (легкоатлетический спортивный комплекс) в г. Астана. Проектирование. Устройство бетонного основания под беговую дорожку (вираж), поставка и монтаж спортивного покрытия для беговой дорожки. Поставка спортивного оборудования и инвентаря для легкой атлетики. Получения сертификата 1 категории ИААФ.
    # 3.	Конгресс центр на 2045 мест в г. Шымкент. Поставка и монтаж театральных кресел.
    # 4.	Работа по оснащению комфортных школ (Биайгрупп, Базис, Интегра и др…). Актовый зал (кресла), спорт зал (инвентарь), МАФы, кабинеты. По Казахстану. Более 50 школ за два года.
    # 5.	ДС Алатау в г. Астана. Поставка и монтаж профессионального спортивного паркета.
    # 6.	Стадион футбольный в г. Туркестан. Поставка и монтаж беговой дорожки вокруг поля.
    # 7.	Олимпийская деревня. Каскелен. Поставка и монтаж беговой дорожки.
    # 8.	Теннисный центр в г. Кызылорда. Поставка и монтаж спортивного паркета 1800 м2.
    # 9.	СК им. Б. Саттарханова в г. Астана. Поставка и монтаж спортивного паркета 800 м2. Оснащение тренажерного зала.
    # 10.	Кокшетау Арена в г. Кокшетау. Полное оснащение спортивным инвентарем в залах бокса, борьбы, фитнесс, также в залах для игр в футбол, баскетбол, волейбол. Поставка и монтаж спортивного паркета 2500 м2, трибуны, спортивные сиденья, скалодром.
    # 11.	Шабыт в г. Астана. Поставка и монтаж спортивного инвентаря, монтаж театральных кресел большого и малого зала.
    # 12.	Стадион Мунайтпасова в г. Астана. Поставка и монтаж спортивных сидений.  
    # 13.	 Школы «НИШ». В 2010-2017 гг.. уличные спортивные площадки, 
    # стадионы. Оснащение спортзалов, спортивное покрытие для спортзалов (паркет, линолеум).
    # 14.	 Школы «Бином».  В 2020 – 2023 гг. Телескопические трибуны, кресла для кинозалов.

                                    
                                            
    #                                         """,f"""Инфа о тендере:{tender},инфа о победителях:{winner_data}""")
    #                         # message = "Временно нет"
    #                         winner_data["message"] = message
    #                         result = parse_company_info(response.text)
    #                         winner_data.update(result)
    #                         winner_data["message"] = message
    #                         tender["winners"].append(winner_data)






                        if daddy_yes == False:
                            company_html = ""
                            web_links = search(lot_winner)
                            print(f"Daddy is not here")
                            web_links_to_save = []
                            for web_link in web_links:
                                
                                if winner_iin not in web_link:
                                    continue
                                print(f"FOUND WEBSITE:{web_link}")
                                
                                web_links_to_save.append(web_link)
                            

                                response = safe_get(web_link, timeout=(10, 120), retries=3)
                                if response is None:
                                    print(f"SKIPPED WEBSITE: {web_link}")
                                    continue
                                soup = BeautifulSoup(response.text, "html.parser")
                                company_section = soup.select_one("main") or soup.body or soup
                                company_text = company_section.get_text("\n", strip=True)
                                company_html += company_text
                                # company_html += str(company_section)
                            print(f"LENGHT OF COMPANY HTML:{len(company_html)}")
                            prompt = """
        Извлеки информацию о компании из HTML.

        Верни только корректный JSON следующего вида:
        {
            "status": "",
            "registration_end_date": ,
            "has_violations": ,
            "violations": [],
            "phone_number": ,
            "email": 
        }


        Если информации нет, укажи null.
        Не добавляй пояснения и Markdown.
        """
                            if not company_html.strip():
                                print("Текст о компании не найден — LLM не вызываем")

                                company_data = {
                                    "status": None,
                                    "registration_end_date": None,
                                    "has_violations": None,
                                    "violations": [],
                                    "phone_number": None,
                                    "email": None
                                }
                            else:
                                
                                result_text = llm.ask(prompt, company_html)
                                company_data = json.loads(result_text)

                            company_data["winner_websites"] = web_links_to_save
                            winner_data.update(company_data)
                            # result_text = llm.ask(prompt, company_html)
                            # company_data = json.loads(result_text)
                            company_data.update({"winner_websites":web_links_to_save})

                            # winner_data.update(company_data)






                            

                            message = llm.ask("""Твоя задача писать сообщения рекламу нашей компании основываясь на инфе о нашей компании, и об инфе о выигранном тендере, и об инфе о победителях тендера. Сообщение адресовано победителям. Если тендер закончился давно, то просто предложи им наши услуги в будущих их начинаниях. Если недавно, спроси нужно ли им еще что-то. Наша компания:ASTANA TECH-GROUP
            Целью нашей компании является совершенствование работ по 
            управлению процессов в сфере строительства. Наша команда объединяет 
            в себе группу компаний в различных направлениях строительной 
            отрасли, а именно:
            • Строительство и комплексное оснащение, а также проектирование 
            спортивных объектов.
            • Поставка спортивных покрытий, сопутствующих материалов для 
            открытых и закрытых спортивных сооружений.
            • Поставка и монтаж театральных и спортивных кресел
            • Поставка и монтаж мультимедийного и слаботочного оборудования
            • Поставка и монтаж телескопических три
            Комплексное оснащение строительных объектов товарами 
            технологического направления (ТХ) 
            • Поставка и устройство профессионального спортивного покрытия для 
            футбола и легкой атлетики (сертификация FIFA и IAAF)
            • Поставка МАФ (малых архитектурных форм) для терских площадок 
            скверов и парков
                                    ТОО «ASTNA TECH-GROUP» БИН 260340004451 010000, РК, г. Астана, ул. Рыскулов, 22. АО «Банк ЦентрКредит» БИК KCJBKZKX ИИК KZ7818562203153343992 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ ТОО «ASTANA TECH-GROUP» выражает Вам свое уважение и предлагает комплексные решения по оснащению спортивных, и культурно образовательных объектов «под ключ». Мы обеспечиваем полный цикл работ, от подбора оборудования и проектирования до поставки, монтажа и ввода в эксплуатацию в том числе: портивные покрытия и оборудование - Системы спортивного паркета — профессиональные покрытия для спортивных залов, соответствующие международным стандартам, обеспечивающие амортизацию, безопасность и долговечность. - Спортивные сиденья и телескопические трибуны для стадионов открытого и закрытого вида, спортивных манежей и спортивных арен. -Спортивные покрытия для фитнесса залов, легкой атлетики, залов для различных видов единоборств. - Напольные покрытия (коммерческий и спортивный линолеум) — качественные решения для учебных и общественных помещений с высокой проходимостью. - Полное оснащение спортивных залов — поставка всего необходимого инвентаря (ворота, щиты, сетки, маты и др.) с учетом специфики объекта. - Оснащение залов всех видов единоборств (борьба, бокс, мма, легкая атлетика, тяжелая атлетика и др…), как для тренировок, так и для профессиональных игр.  - Тренажеры — профессиональные и любительские тренажеры для оснащения залов различного уровня. снащение актовых залов и культурных пространств - Театральные кресла — эргономичные и износостойкие кресла для актовых залов, конференц-залов, кинозалов и театров с возможностью индивидуальной комплектации. - Звуковое оборудование и акустика — профессиональные аудиосистемы, мультимедиа, обеспечивающие качественное звучание для театральных и актовых залов, стадионов и арен любого масштаба. - Музыкальные инструменты — поставка инструментов для образовательных учреждений и культурных центров. снащение образовательных учреждений - Оснащение классов оргтехникой — современные решения для учебного процесса (компьютеры, принтеры, периферия). - Интерактивные панели — инновационные средства обучения, повышающие вовлеченность и эффективность образовательного процесса. лагоустройство территории - Малые архитектурные формы (МАФы) — детские комплексы, скамейки, урны, навесы и другие элементы для комфортного обустройства общественных пространств и территорий. - Уличные покрытия для спортивных площадок — износостойкие и погодоустойчивые покрытия для открытых площадок (резиновая крошка, полиуретан и др.). - Поставка и монтаж покрытий для футбола, легкой атлетики и других видов дисциплин.   - Ограждения спортивных площадок — надежные металлические конструкции для обеспечения безопасности и зонирования территории. Будем рады взаимовыгодному сотрудничеству и готовы предоставить индивидуальное коммерческое предложение с учетом Ваших задач и бюджета.          
            Имея опыт более 16 лет в данном направлении, выполнял работы по поставке и монтажу спортивных покрытий и спортивного инвентаря, спортивных и театральных кресел на таких объектах как:
    1.	Жекпе Жек Сарайы (дворец единоборств) в г. Астана. Оснащение и монтаж спортивных трибун, спортивного паркета (3500м2), спорт инвентаря, рингов, помостов, татами, маты, футбольного поля итд. 
    2.	ЛАСК «Казахстан» (легкоатлетический спортивный комплекс) в г. Астана. Проектирование. Устройство бетонного основания под беговую дорожку (вираж), поставка и монтаж спортивного покрытия для беговой дорожки. Поставка спортивного оборудования и инвентаря для легкой атлетики. Получения сертификата 1 категории ИААФ.
    3.	Конгресс центр на 2045 мест в г. Шымкент. Поставка и монтаж театральных кресел.
    4.	Работа по оснащению комфортных школ (Биайгрупп, Базис, Интегра и др…). Актовый зал (кресла), спорт зал (инвентарь), МАФы, кабинеты. По Казахстану. Более 50 школ за два года.
    5.	ДС Алатау в г. Астана. Поставка и монтаж профессионального спортивного паркета.
    6.	Стадион футбольный в г. Туркестан. Поставка и монтаж беговой дорожки вокруг поля.
    7.	Олимпийская деревня. Каскелен. Поставка и монтаж беговой дорожки.
    8.	Теннисный центр в г. Кызылорда. Поставка и монтаж спортивного паркета 1800 м2.
    9.	СК им. Б. Саттарханова в г. Астана. Поставка и монтаж спортивного паркета 800 м2. Оснащение тренажерного зала.
    10.	Кокшетау Арена в г. Кокшетау. Полное оснащение спортивным инвентарем в залах бокса, борьбы, фитнесс, также в залах для игр в футбол, баскетбол, волейбол. Поставка и монтаж спортивного паркета 2500 м2, трибуны, спортивные сиденья, скалодром.
    11.	Шабыт в г. Астана. Поставка и монтаж спортивного инвентаря, монтаж театральных кресел большого и малого зала.
    12.	Стадион Мунайтпасова в г. Астана. Поставка и монтаж спортивных сидений.  
    13.	 Школы «НИШ». В 2010-2017 гг.. уличные спортивные площадки, 
    стадионы. Оснащение спортзалов, спортивное покрытие для спортзалов (паркет, линолеум).
    14.	 Школы «Бином».  В 2020 – 2023 гг. Телескопические трибуны, кресла для кинозалов.

                                    
                                            
                                            """,f"""Инфа о тендере:{tender},инфа о победителях:{winner_data}""")
                            # message = "Временно нет"
                            winner_data["message"] = message
                            tender["winners"].append(winner_data)
                            # break
                    else:
                        print("No winner")
                        no_winner = True
                if no_winner:
                    continue
                        

                for row in rows_document:
                    text = row.get_text(" ", strip=True).lower()
                    
                    # if "тех" in text and "перейти" in text:
                    # if "перейти" in text and "тех" in text:
                    if "перейти" in text:
                        # print(text)
                        button = row.select_one("button[onclick]")
                        numbers = button["onclick"]
                        match = re.search(r"actionModalShowFiles\((\d+),\s*(\d+)\)", numbers)

                        announce_id = match.group(1)
                        group_id = match.group(2)
                        magic_window = magic_base_url + "/" + announce_id + "/" + group_id
                        # tech.append([announce_id,group_id])
                        # print(magic_window)
                        response = safe_get(magic_window, timeout=(10, 120), retries=3)
                        if response is None:
                            continue
                        magic_soup = BeautifulSoup(response.text,'html.parser')
                        # print(magic_soup)
                        for a in magic_soup.select("a[href]"):
                            link_text = a.get_text(" ",strip=True).lower()
                            if "скачать подпись" in link_text:
                                continue


                            file_url = urljoin("https://goszakup.gov.kz", a["href"])
                            file_name = a.get_text(" ", strip=True)

                            file_response = safe_get(file_url, timeout=(10, 120), retries=3)
                            # print(f"ХТМЛ ИЛИ ЧТО ТО ТАКОЕ ФАЙЛА:{file_response}")
                            if file_response is None:
                                print("Файл не скачался:", file_url)
                                continue

                            file_bytes = file_response.content
                            print(f"Reading file:{file_url}")
                            document_text = extract_text_from_file(file_bytes, file_name)

                            if not document_text:
                                file_description = "Не удалось извлечь текст из файла."
                            else:
                                print(f"Рельаня длина документа:{len(document_text)}")
                                MAX_DOCUMENT_CHARS = 30_000

                                document_text = document_text[:MAX_DOCUMENT_CHARS]
                                file_description = llm.ask(
                                    "Сделай краткое описание самого основного из документа. Кратко, по делу.",
                                    document_text
                                )
                                # file_description = "Временно нет"

                            tender["documents"].append({
                                "name": file_name,
                                "url": file_url,
                                "summary": file_description
                            })



                    
                    
                filename = Path(today.strftime("%d.%m.%Y") + ".json")

                if not filename.exists():
                    with filename.open("w", encoding="utf-8") as file:
                        json.dump([], file, ensure_ascii=False, indent=2)

                with open(filename,'r',encoding='utf8') as file:
                    data = json.load(file)
                
                
                data.append(tender)
                with open(filename, "w", encoding="utf-8") as file:
                    print(f"идет запись...")
                    json.dump(data, file, ensure_ascii=False, indent=2)
        #         one_tender = True
        #         break
        #     break
        # if one_tender == True:
        #     break
            

        


        # tomorrow = datetime.now().date() + timedelta(days=1)
        # next_midnight = datetime.combine(
        #     tomorrow,
        # datetime.min.time()
        #     )
    print("Sleeping for 3 hours...")
    time.sleep(
        10800
    )
    





##заметка - доббавлять те web links которые совпали по иину и сохранять их как список в ключе winners.
 #Почему нормально не пишет номер телефона не может найти?

#Сделать если есть ба прг - тогда отдельно прям внутрь него сделаем запрос, без серпапи. 
#но что если серпапи долбоеб и не может найти ба прг? Тогда с САМОГО НАЧАЛА МЫ БУДЕМ ДЕЛАТЬ ТАК - кидать запрос в ба прг без серпапи, и если нихуя, тогда дадди фолз, и только тогда прибегаем к ллмке


