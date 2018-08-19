#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_new_articles(board_url, board_name, visited_urls):
	with requests.Session() as s:
		s.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

		p = s.get(board_url)
		soup = BeautifulSoup(p.text, "html.parser")

		for elem in soup.find_all('a', class_='link_cafe make-list-uri #article_list'):
			href = urljoin(board_url, elem['href'])

			if not board_url in href: continue
			if href in visited_urls: continue

			# get title
			title = elem.find_all('span', class_='txt_detail')
			if len(title) < 1:
				title = ""
			else:
				title = title[0].text

			# get a date that this article is uploaded
			date = elem.find_all('span', class_='num_info')
			if len(date) < 1:
				date = ""
			else:
				date = date[0].text

			# notice article
			notice = elem.find_all('span', class_='txt_state')
			if len(notice) < 1:
				notice = None
			else:
				notice = notice[0].text

			if notice:
				msg = "[%s %s]: %s - %s\n%s" % (board_name, notice, title, date, href)
			else:
				msg = "[%s] %s - %s\n%s" % (board_name, title, date, href)

			json = {'channel': '#news', 'username': 'brian', 'text': msg, 'icon_emoji': ':smile:'}
			r = requests.post('https://hooks.slack.com/services/[SET_YOUR_API_KEY_HERE]', json=json)

			if r.status_code == 200:
				with open(os.path.join(base_dir, 'visited.db'), 'a+') as fhndl:
					fhndl.write(href+'\n')

if __name__ == '__main__':
	base_dir = os.path.dirname(os.path.realpath(__file__))
	
	visited_urls = []

	try:
		with open(os.path.join(base_dir, 'visited.db'), 'r') as fhndl:
			for line in fhndl:
				line = line.strip()
				visited_urls.append(line)
	except FileNotFoundError:
			pass

	with open(os.path.join(base_dir, "boards.json"), "r") as fhndl:
		j = json.load(fhndl)
		for board in j['boards']:
			check_new_articles(board['url'], board['name'], visited_urls)
