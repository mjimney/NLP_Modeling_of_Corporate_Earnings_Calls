import requests
import re
import pickle
import time
from bs4 import BeautifulSoup
from datetime import datetime

with open('pickle_data/all_urls.pkl', 'rb') as picklefile: 
    all_urls = pickle.load(picklefile)

with open('pickle_data/all_pages.pkl', 'rb') as picklefile: 
    all_pages = pickle.load(picklefile)



def parse_meta_data(urls, pages):
    all_tags = {}
    for i in pages.keys():
        url = urls[i]
        soup = BeautifulSoup(pages[i])

        # Year and Qtr
        try:
            p = re.compile(r'-\w+-q\d-201\d')
            txt = (p.findall(url))[0]
            if bool(txt) == False:
                year = 'error'
                qtr = 'error'
            else:
                year = txt[-4:]
                qtr = txt[-7:-5].upper()
        except:
            year = 'error'
            qtr = 'error'

        # Ticker
        try:
            try:
                tick_str = soup.find(class_ = 'ticker').text
                ticker = re.findall(r":(.*?)\)",tick_str)[0].lstrip()
            except:
                ticker = txt[1:-8].upper()
                if bool(ticker) == False:
                    ticker = 'error'
        except:
            ticker = 'error'

        # Article Post Date
        try:
            p = re.compile(r'20\d+/\d+/\d+')
            post_date = (p.findall(url))[0]
            if bool(post_date) == False:
                post_date = 'error'
        except:
            post_date = 'error'

        # Actual Call Date
        try:
            try:
                call_date = soup.find(id = 'date').text
            except:
                k = 0
                for inx,t in enumerate(soup.find_all('em')):
                    if t.text[:7] != 'Returns' and k == 0:
                        k += 1
                        try:
                            call_date = str(soup.find_all('em')[inx].previous_sibling)
                            if call_date == '' or call_date == ',':
                                raise Exception
                        except:
                            call_date = soup.find_all('em')[inx].previous_sibling.previous_sibling.text
                if k == 0:
                    call_date = 'error'
        except:
            call_date = 'error'

        # Actual Call Time
        try:
            try:
                call_time = soup.find(id = 'time').text
            except:
                k = 0
                for inx,t in enumerate(soup.find_all('em')):
                    if t.text[:7] != 'Returns' and k == 0:
                        k += 1
                        call_time = str(soup.find_all('em')[inx].text)
                        if call_time == '' or call_time == ',':
                            raise Exception
                if k == 0:
                    call_time = 'error'
        except:
            call_time = 'error'
            
        # all_tags[i] = [ticker,post_date,qtr,year]
        all_tags[i] = [ticker,post_date,call_date,call_time,qtr,year]

    return all_tags

def create_datetime_field(tags,error_output=False):
    error_list = []
    tickers = {}
    dates = {}

    for idx in all_tags.keys():
        # Parse Date
        s = all_tags[idx][2]
        s = s.lstrip().rstrip()
        s = s.replace('.','')
        s = s.replace('2017,','2017')
        s = s.replace('2018,','2018')
        s = s.replace('2019,','2019')
        s = s.replace(u'\xa0', ' ')
        s = s.replace('Sept ','Sep ')
        s = s.replace('th,',',')

        try:
            try:
                d = datetime.strptime(s, '%B %d, %Y')
                adj_date = d
            except:
                try:
                    d = datetime.strptime(s, '%b %d, %Y')
                    adj_date = d
                except:
                    d = datetime.strptime(s, '%b, %d, %Y')
                    adj_date = d
        except:
            adj_date = 'error'

        # Parse Time
        t = all_tags[idx][3]
        t = t.lstrip()
        t = t.replace('.','')
        t = t.replace(' ET','')
        t = t.replace(' EST','')
        t = t.replace(' EDT','')

        try:
            u = datetime.strptime(t,'%I:%M %p').time()
            adj_time = u
        except:
            adj_time = 'error'


        if adj_date == 'error' == adj_time == 'error':
            error_list.append((s,t))
        elif adj_date == 'error':
            error_list.append((s,'ok'))
        elif adj_time == 'error':
            error_list.append(('ok',t))
        else:
            tickers[idx] = all_tags[idx][0]
            dates[idx] = datetime.combine(d, u)

    if error_output == True:
        return tickers, dates, error_list
    else:
        return tickers, dates

def text_parse(pages):
    text_log = []
    pharagraph_log = []
    fail_log = []
    for i in pages.keys():
        try:
            soup = BeautifulSoup(pages[i])

            names = [n.text for n in soup.find_all('strong')[1:]]
            # try:
            dur = [k for k in names if 'minute' in k.lower()][0]   # Finds the final line of transcript (Duration: x minutes)
            # except:
            #     if i == '268.19':
            #         dur = [k for k in names if '68 minutes' in k][0]
            end = names.index(dur)
            names = names[:end]

            company_staff = []
            header = ''
            for a in soup.find_all(class_= 'article-content')[0].children:
                if a.name == 'h2':
                    if 'question' in a.text.lower():
                        header = 'Q and A'
                    elif 'prepare' in a.text.lower():
                        header = 'Prepared Remarks'
                elif a.name == 'p' and (header == 'Prepared Remarks' or header == 'Q and A'):
                    if len(names) == 0:
                        pharagraph_log[3] += a.text
                        text_log.append(pharagraph_log)
                        break
                    elif a.text[:len(names[0])] == names[0]:
                        if header == 'Prepared Remarks':
                            company_staff.append(a.text.lower())
                            text_log.append(pharagraph_log)
                            pharagraph_log = [i,header,names[0],'','internal']
                            names.pop(0)
                        else:
                            if a.text.lower() in company_staff:
                                int_ext = 'internal'
                            else:
                                int_ext = 'external'
                            text_log.append(pharagraph_log)
                            pharagraph_log = [i,header,names[0],'',int_ext]
                            names.pop(0)
                    else:
                        pharagraph_log[3] += a.text
                else:
                    pass
            print (i,'Success')
        except:
            text_log.append([i,'error','error','error','error'])
            fail_log.append(i)
            print (i,'FAIL')
    text_log.pop(0)
    print (fail_log)
    return text_log



# Create the all_tags file
all_tags = parse_meta_data(all_urls, all_pages)

# Manual Overrides, 2 entries missing dates
all_tags['256.10'] = ['IIPR', '2019/03/14', 'March 14, 2019', '1:00 p.m. ET', 'Q4', '2018']
all_tags['407.14'] = ['L', '2018/11/05', 'Nov. 05, 2018', '11:00 a.m. ET', 'Q3', '2018']

all_tickers, all_dates = create_datetime_field(all_tags)

all_text = text_parse(all_pages)

with open('pickle_data/all_tags.pkl', 'wb') as picklefile:
    pickle.dump(all_tags, picklefile)

with open('pickle_data/all_tickers.pkl', 'wb') as picklefile:
    pickle.dump(all_tickers, picklefile)

with open('pickle_data/all_dates.pkl', 'wb') as picklefile:
    pickle.dump(all_dates, picklefile)

with open('pickle_data/all_text.pkl', 'wb') as picklefile:
    pickle.dump(all_text, picklefile)
