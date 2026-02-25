import requests
from bs4 import BeautifulSoup


def get_book_links():

    link = 'https://www.wordproject.org/bibles/fr/index.htm#1'
    domen = 'https://www.wordproject.org/bibles/fr/'

    page = BeautifulSoup(requests.get(link, 'lxml').text)
    page = page.find_all('div', class_='ym-g50 ym-gr')[0]

    book_links = [domen + book.find('a')['href'] for book in page.find_all('li')]

    return book_links


def get_chapter_links(book_link):

    domen = book_link[:-5]

    page = requests.get(book_link, 'lxml').text
    page = BeautifulSoup(page).find('p', class_='ym-noprint')

    chapters = page.find_all('a', class_='chap')
    chapter_links = [domen + link['href'] for link in chapters]
    chapter_links = [book_link] + chapter_links

    return chapter_links


def get_verses(chapter_link):

    page = requests.get(chapter_link, 'lxml')
    page = BeautifulSoup(page.text)

    verses = '1' + page.find('div', class_='textBody').find('p').text

    return verses