from lxml import etree
import aiohttp
import asyncio
import curses
import logging
import itertools
import re
import webbrowser

logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s',
)

SITE = 'https://www.imdb.com/'

async def get_webpage(url):
    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                code = response.status
                html = await response.text()
                return {'code':code,'html':html}

async def idleAnimation(task):
    for frame in itertools.cycle(r'-\|/-\|/'):
        if task.done():
            print('\r', '', sep='', end='', flush=True)
            break
        print('\r', frame, sep='', end='', flush=True)
        await asyncio.sleep(0.2)

def interactive_console(screen, data):
    pos = 0
    while pos < len(data):
        screen.clear()
        screen.addstr("({0}/{1})\n".format(pos+1, len(data)))
        for key in data[pos]:
            if key != 'url':
                screen.addstr(data[pos][key] + '\n')
        screen.addstr("Next, Previous, Open, or Quit? (j, k, o, q)")
        user_response = screen.getkey()
        valid_response = False
        while not valid_response:
            if user_response == 'j':
                valid_response = True
                pos += 1
            elif user_response == 'k':
                if pos != 0:
                    valid_response = True
                    pos  -= 1
                else:
                    user_response = screen.getkey()
            elif user_response == 'o':
                webbrowser.open(data[pos]['url'])
                user_response = screen.getkey()
            elif user_response == 'q':
                valid_response = True
                pos = len(data)
            else:
                user_response = screen.getkey()

def getTitleInfo(html, url):
    content = {}
    content['url'] = url
    content['title'] = ''.join(html.xpath("//h1[@data-testid='hero-title-block__title']/text()"))
    metadata = html.xpath("//ul[contains(@data-testid,'hero-title-block')]")[0]
    for a in metadata.xpath(".//a"):
        a.getparent().remove(a)
    content['metadata'] = []
    for data in metadata.xpath("./li"):
        content['metadata'].append(''.join(data.xpath("./descendant-or-self::*/text()")))
    content['metadata'] = ' | '.join(content['metadata'])
    content['summary'] = ''.join(html.xpath(".//span[contains(@class,'GenresAndPlot')][1]/text()"))
    content['tags'] = ', '.join(html.xpath("//span[@class='ipc-chip__text']/text()")[:3])
    content['trailers'] = SITE + ''.join(html.xpath("//a[@aria-label='Watch {VideoTitle}']/@href"))[1::]
    return content

def getNameInfo(html, url):
    content = {}
    content['url'] = url
    content['name'] = ''.join(html.xpath("//div[@class='parent']/h3/a/text()"))
    content['overview'] = []
    tableRows = html.xpath("//table[@id='overviewTable']/tr")
    for row in tableRows:
        rowText = row.xpath("./descendant-or-self::*/text()")
        for idx in range(len(rowText)):
            rowText[idx] = re.sub('[^0-9a-zA-Z ,]+', '', rowText[idx])
        content['overview'].append(' '.join([item.strip() for item in rowText if item.strip()]))
    content['overview'] = '\n'.join(content['overview'])
    return content

async def search(query_string):
    query = 'find?q='
    queryUrl = ''.join(list([SITE, query, query_string]))
    webRequestTask = asyncio.create_task(get_webpage(queryUrl))
    await idleAnimation(webRequestTask)
    if webRequestTask.result()['code'] == 200:
        page_html = etree.HTML(webRequestTask.result()['html'])
        sections = page_html.xpath("//div[@class='findSection']")
        if sections:
            section = sections[0]
            sectionType = ''.join(section.xpath("./h3/descendant-or-self::*/text()"))
            if sectionType == 'Titles':
                urlTasks = []
                titleUrls = section.xpath(".//td[contains(@class,'result_text')]/a/@href")
                for url in titleUrls:
                    urlTasks.append(asyncio.create_task(get_webpage(SITE + url[1::])))
                await idleAnimation(asyncio.gather(*urlTasks))
                data = []
                for idx in range(len(urlTasks)):
                    if urlTasks[idx].result()['code'] == 200:
                        data.append(getTitleInfo(etree.HTML(urlTasks[idx].result()['html']), SITE + titleUrls[idx][1::]))
                curses.wrapper(interactive_console, data)
            elif sectionType == 'Names':
                urlTasks = []
                nameUrls = section.xpath(".//td[contains(@class,'result_text')]/a/@href")
                for url in nameUrls:
                    urlTasks.append(asyncio.create_task(get_webpage(SITE + url[1::] + 'bio')))
                await idleAnimation(asyncio.gather(*urlTasks))
                data = []
                for idx in range(len(urlTasks)):
                    if urlTasks[idx].result()['code'] == 200:
                        data.append(getNameInfo(etree.HTML(urlTasks[idx].result()['html']), SITE + nameUrls[idx][1::] + 'bio'))
                curses.wrapper(interactive_console, data)
            else:
                print(f'The results that are returned are not currenlty handled.')
        else:
            print(f'No Results.')
    else:
        print(f'Recieved {webRequestTask.result()["code"]} response code.')