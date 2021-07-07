import requests
import sys
import webbrowser
from bs4 import BeautifulSoup as bs
import logging

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s',
)

def printUrlInfo(infoUrl):
    logging.info(locals())
    r = requests.get(infoUrl)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        titleWrapper = soup.find('h1', {'class':''})
        subtext = soup.find('div', {'class':'subtext'})
        plotSummary = soup.find('div', {'class':'summary_text'})
        print(titleWrapper.get_text().strip(), end=' |') if titleWrapper is not None else print('Failed to retrieve title.')
        printSubtext(subtext.get_text())
        print('Summary: ' + str(plotSummary.get_text()).strip()) if plotSummary is not None else print('Failed to retrieve movie plot summary.')  
    else:
        print('Did not receive a 200 response code. Check network connection.')

def printSubtext(subtext):
    if subtext is None:
        print('Faile to retrieve subtext data.')
        return
    subtext = subtext.split('\n')
    for idx in range(len(subtext)):
        subtext[idx] = subtext[idx].strip()
    subtext = ' '.join(subtext)
    print(subtext)

def printActorUrlInfo(infoUrl):
    logging.info(locals())
    r = requests.get(infoUrl)
    if r.status_code == 200:
        soup = bs(r.content, 'html.parser')
        actorName = soup.find('h3', {'class':''}).get_text().strip()
        bio = soup.find('table', {'id':'overviewTable'})
        actorSummaryText = soup.find('p', {'class':''}).get_text().strip()
        print(actorName) if actorName is not None else print('Error: No name found.')
        printBio(bio) if bio is not None else print('Error: No bio found.')
        print(f'Summary: {actorSummaryText}') if actorSummaryText is not None else print('Error: No summary found.')
    else:
        print('Did not receive a 200 response code. Check network connection.')

def printBio(bio):
    tableRows = bio.find_all('tr')
    for row in tableRows:
        if row.td.string == 'Birth Name':
            print(f'{row.td.string}: {row.td.next_sibling.string}')
            continue
        rowText = row.get_text().split('\n')
        rowText = list(filter(None, rowText))
        for idx in range(len(rowText)):
            rowText[idx] = rowText[idx].strip()
        rowText[0] = rowText[0] + ':'
        rowText = ' '.join(rowText)
        print(rowText)

def main():
    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print('Error: Not enough arguments provided. Please provide a search term.')
            return
        else:
            print('Error: Too many arguments provided.')
            return
    
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
            partialUrl = text.find('a').get('href')
            splitPartialUrl = partialUrl.split('/')
            urlType = splitPartialUrl[1]
            if urlType == 'name':
                splitPartialUrl[3] = 'bio' + splitPartialUrl[3]
                url_info = ''.join([site, '/'.join(splitPartialUrl)])
                printActorUrlInfo(url_info)
            else:
                url_info = ''.join([site, partialUrl])
                printUrlInfo(url_info)
            if idx + 1 != len(resultTexts):
                userResponse = input("Open, Next, Quit? (o/n/q) ")
                if userResponse == 'o':
                    webbrowser.open(url_info)
                    userResponse = input("Next or Quit? (n/q) ")
                    if userResponse == 'q':
                        break
                elif userResponse == 'n':
                    pass
                else:
                    break
            else:
                userResponse = input("Open or Quit? (o/q) ")
                if userResponse == 'o':
                    webbrowser.open(url_info)
    else:
        print('Did not receive a 200 response code. Check network connection.')

if __name__ == "__main__":
    main()
