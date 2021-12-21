from re import M
from typing import ContextManager
from lxml import etree
import aiohttp
import asyncio
import curses
import logging
import itertools
import webbrowser

logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s',
)

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
            break;
        print('\r', frame, sep='', end='', flush=True)
        await asyncio.sleep(0.2)

def displayTitleInfo(html):
    content = {}
    content['title'] = ''.join(html.xpath("//h1[@data-testid='hero-title-block__title']/text()"))
    metadata = html.xpath("//ul[contains(@data-testid,'hero-title-block')]")[0]
    for a in metadata.xpath("//a"):
        a.getparent().remove(a)
    content['metadata'] = []
    for data in metadata.xpath("./li"):
        content['metadata'].append(''.join(data.xpath("./descendant-or-self::*/text()")))
    content['metadata'] = ' | '.join(content['metadata'])
#    content['runtine'] = 
#    content['score'] = 
#    content['summary'] = 
#    content['trailers'] = 
#    content[''] = 
#    content[''] = 
#    content[''] = 
#    content[''] = 
    for key in content:
        print(f'{content[key]}')

async def search(query_string):
    site = 'https://www.imdb.com/'
    query = 'find?q='
    queryUrl = ''.join(list([site, query, query_string]))
    webRequestTask = asyncio.create_task(get_webpage(queryUrl))
    await idleAnimation(webRequestTask)
    if webRequestTask.result()['code'] == 200:
        page_html = etree.HTML(webRequestTask.result()['html'])
        # TODO write code to either scrape actor information or a title information
        # for title information for each title get and display title, year of publication, content rating, runtime, imdb score, summary, and trailers

        sections = page_html.xpath("//div[@class='findSection']")
        if sections:
            section = sections[0]
            sectionType = ''.join(section.xpath("./h3/descendant-or-self::*/text()"))
            if sectionType == 'Titles':
                urlTasks = []
                titleUrls = section.xpath(".//td[contains(@class,'result_text')]/a/@href")
                for url in titleUrls:
                    urlTasks.append(asyncio.create_task(get_webpage(site + url[1::])))
                await idleAnimation(asyncio.gather(*urlTasks))
                for task in urlTasks:
                    if task.result()['code'] == 200:
                        displayTitleInfo(etree.HTML(task.result()['html']))
            elif sectionType == 'Names':
                pass
            else:
                print(f'The results that are returned are not currenlty handled.')
        else:
            print(f'No Results.')
    else:
        print(f'Recieved {webRequestTask.result()["code"]} response code.')