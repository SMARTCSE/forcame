import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
import pandas as pd

def abstract_cleaner(abstract):
    """Converts all the sup and sub script when passing the abstract block as html"""
    conversion_tags_sub = BeautifulSoup(str(abstract), 'html.parser').find_all('sub')
    conversion_tags_sup = BeautifulSoup(str(abstract), 'html.parser').find_all('sup')
    abstract_text = str(abstract).replace('<.', '< @@dot@@')
    for tag in conversion_tags_sub:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    for tag in conversion_tags_sup:
        original_tag = str(tag)
        key_list = [key for key in tag.attrs.keys()]
        for key in key_list:
            del tag[key]
        abstract_text = abstract_text.replace(original_tag, str(tag))
    abstract_text = sup_sub_encode(abstract_text)
    abstract_text = BeautifulSoup(abstract_text, 'html.parser').text
    abstract_text = sup_sub_decode(abstract_text)
    abstract_text = re.sub('\\s+', ' ', abstract_text)
    text = re.sub('([A-Za-z])(\\s+)?(:|\\,|\\.)', r'\1\3', abstract_text)
    text = re.sub('(:|\\,|\\.)([A-Za-z])', r'\1 \2', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(</su(p|b)>)', r'\3\1\4\5', text)
    text = re.sub('(<su(p|b)>)(\\w+)(\\s+)(</su(p|b)>)', r'\1\3\5\4', text)
    text = re.sub('(<su(p|b)>)(\\s+)(\\w+)(\\s+)(</su(p|b)>)', r'\3\1\4\6\5', text)
    abstract_text = re.sub('\\s+', ' ', text)
    abstract_text = abstract_text.replace('< @@dot@@', '<.')
    return abstract_text.strip()

def sup_sub_encode(html):
    """Encodes superscript and subscript tags"""
    encoded_html = html.replace('<sup>', 's#p').replace('</sup>', 'p#s').replace('<sub>', 's#b').replace('</sub>',
                                                                                                         'b#s') \
        .replace('<Sup>', 's#p').replace('</Sup>', 'p#s').replace('<Sub>', 's#b').replace('</Sub>', 'b#s')
    return encoded_html


def sup_sub_decode(html):
    """Decodes superscript and subscript tags"""
    decoded_html = html.replace('s#p', '<sup>').replace('p#s', '</sup>').replace('s#b', '<sub>').replace('b#s',
                                                                                                         '</sub>')
    return decoded_html

if __name__ == '__main__':
    all_data = []
    urls = ['https://forcam.com/en/downloads/success-story/foundation-wellness/',
            'https://forcam.com/en/downloads/success-story/peka-metall-ag/',
            'https://forcam.com/en/downloads/success-story/nmh-gmbh/'
            ]
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Response from {url}:")
            # print(response.text)  # or whatever processing you need
        else:
            print(f"Failed to retrieve {url}")

        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.find('div', class_='content')
        title = data.find('h1')
        Title = abstract_cleaner(title)
        all_dict = {'TITLE': Title, 'URL': urls}
        all_data.append(all_dict)
        df = pd.DataFrame(all_data)
        df.to_csv('Forcam_output.csv', index=False)
        print(title)