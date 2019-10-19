
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import csv
import time



#to handle ajax load more button
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')
#chromedriver should be in same directory of this file; otherwise, specify path of chromedriver
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://www.smartmobil.de/handys")
load_more_button = driver.find_elements_by_xpath('//*[@id="smartmobil.de"]/div[1]/div[7]/div/div/div[4]/div/div')[0]
button = load_more_button.text
print(button)
driver.execute_script("arguments[0].click();", load_more_button)
time.sleep(2)
page_source = driver.page_source


#parsing HTML
soup = BeautifulSoup(page_source, 'html.parser')
brand_phone = soup.find(class_='l-content')
links = brand_phone.select('.c-panel-headline.p-confi-smartphone-panel-headline')
phone_links = {l.find('a')['href'] for l in links}


#creating empty lists and appending instead of concat dataframes b/c concat O(n^2) time
phone_names_list = []
phone_storages_list = []
phone_plans_list = []
phone_datas_list = []
phone_monthlyprice_list = []
phone_unlimited_talk_list = []
phone_unlimited_sms_list = []

#looping through the different links from home page (only smartphones and not tablets)
for i in range(len(phone_links)):
	if("handys" in list(phone_links)[i]):
		page = requests.get('https://www.smartmobil.de' + list(phone_links)[i])
		#to check the response
		print(page.status_code)

		soup = BeautifulSoup(page.content, 'html.parser')
		four_type = soup.find(class_= 'row l-row-padding--small p-confi-matching-tarif')

		names = four_type.select('.cute-3-tablet .p-confi-tarif-panel-smartphone-headline')
		item_storages = soup.find("a", class_= 'p-confi-memory_picker p-confi-memory_picker--active').get_text()
		for n in names:
			phone_names_list.append(n.get_text()) 
			phone_storages_list.append(int("".join(filter(str.isdigit, item_storages))))
	
		plan_names = four_type.select('.cute-3-tablet .c-panel-headline')
		for p in plan_names:
			phone_plans_list.append(p.get_text().replace('smartmobil.de', ''))

		datas = four_type.select('.cute-3-tablet .e-tarifbox-details-internetVolume')
		for d in datas:
			phone_datas_list.append(int("".join(filter(str.isdigit, d.get_text()))))

		monthlyprice_dollar = four_type.select('.cute-3-tablet .c-price-before_decimal')
		phone_dollars = [float("".join(filter(str.isdigit, d.get_text()))) for d in monthlyprice_dollar]
		monthlyprice_cents = four_type.select('.cute-3-tablet .c-price-after_decimal')
		phone_cents = [float("".join(filter(str.isdigit, c.get_text()))) for c in monthlyprice_cents]
		for i in range(len(phone_dollars)):
			phone_monthlyprice_list.append(phone_dollars[i] + phone_cents[i]/100)

		unlimits = four_type.select('.cute-3-tablet .e-tarifbox-bulletpoints-phone')
		for ul in unlimits:
			phone_unlimited_talk_list.append('Flat Telefonie' in ul.get_text())
			phone_unlimited_sms_list.append('SMS' in ul.get_text())


phones_smartmobil_de = pd.DataFrame({
		'device_name': phone_names_list,
		'Device_storage': phone_storages_list,
		'Plan_name': phone_plans_list,
		'Plan_data': phone_datas_list,
		'Monthly_price': phone_monthlyprice_list,
		'Unlimited_talk': phone_unlimited_talk_list,
		'Unlimited_sms': phone_unlimited_sms_list
		})


#save to csv
phones_smartmobil_de.to_csv("phones_smartmobil_de.csv")
