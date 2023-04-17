#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os.path
import time

import requests
from bs4 import BeautifulSoup
import urllib3
from urllib import parse

from requests import exceptions
from tqdm import tqdm

urllib3.disable_warnings()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
u1 = 'https://efi.igb.illinois.edu/efi-gnt/get_gnd_data.php?gnn-id=%s&key=%s&window=%d&query=%d&stats=1'
u2 = 'https://efi.igb.illinois.edu/efi-gnt/get_gnd_data.php?gnn-id=%s&key=%s&window=%d&scale-factor=%s&range=%s-%s&id-type=uniprot'
p1 = 'https://rest.uniprot.org/uniprotkb/%s'
p2 = 'https://www.ncbi.nlm.nih.gov/nuccore/%s'
p3 = 'https://www.ncbi.nlm.nih.gov/sviewer/viewer.fcgi?id=%s&db=nuccore&report=genbank&conwithfeat=on&basic_feat=on&hide-sequence=off&hide-cdd=on&from=%d&to=%d&retmode=genebank&withmarkup=on&tool=portal'
url = ''
window = 10
query_start = 1
query_end = 1
skip = 0
params = {}
dw = False


def main():
    init()
    gnn_id = params['gnn-id'][0]
    gnn_key = params['key'][0]
    for query in range(query_start, query_end + 1):
        print("Step 1: gnn-id[%s] key[%s] query(%d) window(%d)..." % (gnn_id, gnn_key, query, window), end='',
              flush=True)
        res = get(url)
        if res == '':
            print('Query(%d) Step(1) failed.' % query)
            continue
        bf = BeautifulSoup(res, 'html.parser')
        title = bf.find("td", {'id': 'header-body-title'}).find("i").text
        title = '[%s][%s]%s' % (gnn_id, window, title)
        print('Ok.')
        print('Step 2: init query...', end='', flush=True)
        res = get(u1 % (gnn_id, gnn_key, window, query))
        if res == '':
            print('Query(%d) Step(2) failed.' % query)
            continue
        m = json.loads(res)
        if m['error']:
            print('Query(%d) Step(2) failed: %s.' % (query, res))
            continue
        if m['stats']['num_checked'] == 0:
            print('Query(%d) Step(2) failed: no item.' % query)
            continue
        print('Ok.')
        print('Step 3: query page...')
        min = m['stats']['index_range'][0][0]
        max = m['stats']['index_range'][0][-1]
        scale_factor = m['stats']['scale_factor']
        arr = []
        items = []
        for i in tqdm(range(min, max + 1)):
            arr.append(i)
            if len(arr) == 10 or i == max:
                res = get(u2 % (gnn_id, gnn_key, window, scale_factor, arr[0], arr[-1]))
                if res == '':
                    print('Query(%d) Step(3) failed.' % query)
                    continue
                m = json.loads(res)
                items += m['data']
                arr = []
        print('> Success get [%d] items.' % len(items))
        if not os.path.exists(title):
            os.makedirs(title)
            print('Create folder：%s' % title)
        fo = open("%s/[0]sequence.txt" % title, "a")
        print('Step 4: query detail ', end='')
        if dw:
            print('and download gb file...')
        else:
            print('without download gb file...')
        for i, v in enumerate(items):
            n = i + 1
            if i < skip:
                print('[%d] skip.' % n)
                continue
            t = v['attributes']
            ed = '' if dw else '\n'
            print('[%d] %s %s %s...' % (n, t['accession'], t['id'], t['organism']), end=ed, flush=True)
            res = get(p1 % t['accession'])
            if res == '':
                print('[%d] failed.' % n)
                continue
            m = json.loads(res)
            name = m['organism']['scientificName']
            name = name.replace('/', ' ')
            txt = '> %s %s\n%s\n' % (t['accession'], m['organism']['scientificName'], m['sequence']['value'])
            fo.write(txt)
            if not dw:
                continue
            print(' Find id...', end='', flush=True)
            res = get(p2 % t['id'])
            if res == '':
                print('[%d] find id failed.' % n)
                continue
            bf = BeautifulSoup(res, 'html.parser')
            id = bf.find("meta", {'name': 'ncbi_uidlist'})['content']
            if len(v['neighbors']) > 0:
                start = v['neighbors'][0]['start']
                stop = v['neighbors'][-1]['stop']
            else:
                start = t['start']
                stop = t['stop']
            print('Ok. Id is %s, downloading range(%d-%d)...' % (id, start, stop), end='', flush=True)
            res = get(p3 % (id, start, stop))
            if res == '':
                print('[%d] download failed.' % n)
                continue
            gb = open("%s/%s.gb" % (title, '[%d][%d][%s]%s' % (query, n, t['id'], name)), "w")
            gb.write(res)
            gb.close()
            print('Ok.')
        fo.write('\n')
        fo.close()
        print('Query(%d) done.' % query)
    print('All done, have a nice day!')
    n = 5
    while n >= 0:
        time.sleep(1)
        print('%d' % n)
        n -= 1


def init():
    global url, query_start, query_end, window, params, skip, dw
    while url == '':
        url = input('Input url: ')
    q = input('Input query number or range [1 or 1-10, default: 1]: ')
    if q != '':
        arr = q.split('-')
        try:
            query_start = int(arr[0])
        except ValueError:
            query_start = 1
        try:
            query_end = int(arr[1])
        except IndexError:
            query_end = query_start
    window = input('Input window size [default: 10]: ')
    if window == '':
        window = 10
    else:
        try:
            window = int(window)
        except ValueError:
            window = 10
    # skip = input('Input a skip number if you want: ')
    # if skip == '':
    #     skip = 0
    # else:
    #     try:
    #         skip = int(skip)
    #     except ValueError:
    #         skip = 0
    gb = input('Do you want to download gb files? [y/n, default: n]: ')
    if gb == 'y':
        dw = True
    params = parse.parse_qs(parse.urlparse(url).query)
    while 'gnn-id' not in params or 'key' not in params:
        print('Url invalid.')
        url = input('Please input an url: ')
        params = parse.parse_qs(parse.urlparse(url).query)


def get(u):
    try:
        response = requests.get(u, headers=headers, verify=False)
    except exceptions.Timeout:
        print('[ERROR] request timeout')
    except exceptions.HTTPError:
        print('[ERROR] http error')
    except:
        print('[ERROR] unknown error')
    else:
        if response.status_code == 200:
            return response.text
    return ''


if __name__ == "__main__":
    main()
