import requests
from bs4 import BeautifulSoup as bs

def main():
    site = 'https://www.imdb.com/'
    query = 'find?q='
    queryStr = 'xmen'
    queryUrl = ''.join(list([site, query, queryStr]))
    r = requests.get(queryUrl)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        findSection = soup.find('div', {'class':'findSection'})
        resultTexts = findSection.find_all('td','result_text')
        for text in resultTexts:
            print(''.join([site, text.find('a').get('href')]))
    else:
        print('Did not receive a 200 response code. Check network connection.')
    
if __name__ == "__main__":
    main()
