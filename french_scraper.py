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


with open('book_links.txt', 'r', encoding='utf-8') as f:
    book_links = f.read().split('\n')


with open('chapter_links.txt', 'w', encoding='utf-8') as f:
    for book_link in book_links:
        chapter_links = get_chapter_links(book_link)
        for chapter_link in chapter_links:
            f.write(chapter_link + '\n')
        f.write('\n')


