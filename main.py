import requests
import sys
from bs4 import BeautifulSoup as bs

def printUrlInfo(infoUrl):
    print()
    r = requests.get(infoUrl)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        titleWrapper = soup.find('h1', {'class':''})
        plotSummary = soup.find('div', {'class':'summary_text'})
        if titleWrapper is not None:
            print(titleWrapper.get_text())
        else:
            print('Failed to retrieve title and date.')
        if plotSummary is not None:
            print('Summary: ' + str(plotSummary.get_text()).strip())
        else:
            print('Failed to retrieve movie plot summary.')
    else:
        print('Did not receive a 200 response code. Check network connection.')
    print('Url: ' + infoUrl)
    print()


def main():
    site = 'https://www.imdb.com/'
    query = 'find?q='
    queryStr = sys.argv[1]
    queryUrl = ''.join(list([site, query, queryStr]))
    r = requests.get(queryUrl)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        findSection = soup.find('div', {'class':'findSection'})
        resultTexts = findSection.find_all('td','result_text')
        for idx, text in enumerate(resultTexts):
            printUrlInfo(''.join([site, text.find('a').get('href')]))
            if idx + 1 != len(resultTexts):
                userContinue = input("Continue?(enter/q) ")
                if userContinue == 'q':
                    break
    else:
        print('Did not receive a 200 response code. Check network connection.')
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Search string required. Please provide a value to search.')
    else:
        main()
