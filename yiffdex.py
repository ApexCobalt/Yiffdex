# coding: utf8

"""
MIT License

Copyright (c) 2018, Noryx your fluffy dev ^w^

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import hashlib
import json
import os
import re
import argparse
import time
import urllib.request
import urllib.error
import piexif
import threading

import gui

# MD5 Functions ---------------------------------

def get_file_hash(file_in):
    with open(file_in, 'rb') as f:
        r = f.read()
    return hashlib.md5(r).hexdigest()

def get_name_hash(input):
    filename = os.path.basename(input)
    m = re.match(r"^([A-Fa-f0-9]{32})\..+$", filename)
    return m.group(1) if m is not None else ''

def get_meta_hash(file):
    try:
        exif = piexif.load(file)
    except piexif._exceptions.InvalidImageDataError:
        return ''

    if piexif.ImageIFD.XPComment not in exif["0th"]:
        return ''

    m = re.match(r"md5:([A-Fa-f0-9]{32})", exif_str_decode(exif["0th"][piexif.ImageIFD.XPComment]))
    return m.group(1) if m is not None else ''
        
# Metadata Functions ----------------------------

# Transform extracted image metadata string to unicode python string
def exif_str_decode(input):
    return ''.join([chr(_) for _ in input if _ != 0])

# Transform unicode python string to image metadata string
def exif_str_encode(input):
    output = []
    for _ in input:
        car = ord(_)
        output.append(car if car <= 255 else 32)
        output.append(0)
    return tuple(output)

def is_marked(file):
    try:
        exif = piexif.load(file)
    except piexif._exceptions.InvalidImageDataError:
        return False

    if piexif.ImageIFD.XPComment not in exif["0th"]:
        return False

    return exif_str_decode(exif["0th"][piexif.ImageIFD.XPComment]).split('|')[0] == 'yiffdex'

def set_metadata(file, keywords = '', authors = '', comment = ''):
    try:
        exif = piexif.load(file)
    except piexif._exceptions.InvalidImageDataError:
        return

    exif["0th"][piexif.ImageIFD.XPKeywords] = exif_str_encode(keywords)
    exif["0th"][piexif.ImageIFD.XPAuthor] = exif_str_encode(authors)
    exif["0th"][piexif.ImageIFD.XPComment] = exif_str_encode(comment)

    piexif.remove(file)
    piexif.insert(piexif.dump(exif), file)

# Cache Class -----------------------------------

class YiffdexCache:

    def __init__(self, file):
        self.data = {}
        self.path = file

    def load(self):
        if os.path.isfile(self.path) is False:
            try:
                f = open(self.path, 'wb+')
                f.close()
            except IOError:
                print("Unable to create cache file !")
            
            return

        with open(self.path, 'rb') as f:
            for line in f:
                item = line.decode('utf-8').split('|')
                self.data[item[0]] = item[1]
    
    def append(self, file, status):
        self.data[file] = status
        with open(self.path, 'ab+') as f:
            data = file + "|" + str(status) + "\n"
            f.write(data.encode('utf-8'))

# API Function ----------------------------------

# Use e621 API for retrieving image information using md5 hash
# see : https://e621.net/help/show/api for more information
def e621_search(md5, username = 'guest'):
    request = urllib.request.build_opener()
    request.addheaders = [('User-agent', 'Yiffdex/0.2a used by ' + username)]

    try:
        f = request.open("https://e621.net/post/show.json?md5=" + md5)
        if f is not None:
            data = json.loads(f.read())

            info = {}
            info['tags'] = data['tags'].split(" ")
            info['author'] = ';'.join(data['artist']) if 'artist' in data else ''
            info['src'] = data['source'] if 'source' in data and data['source'] is not None else ''

            return info
    except urllib.error.HTTPError:
        pass
    except urllib.error.URLError:
        pass
    except json.JSONDecodeError:
        pass

    return None

# Inkbunny API for retrieving image information using md5
# see : https://wiki.inkbunny.net/wiki/API for more information
class YiffdexInkbunnyAPI:

    def __init__(self):
        self.api_url = 'https://inkbunny.net/'
        self.sid = ''

    def login(self, username = 'guest', password = ''):
        request = urllib.request.build_opener()
        request.addheaders = [('User-agent', 'Yiffdex/0.2a'),('Content-type','multipart/form-data')]
        
        # Login and get sid
        try:
            params = urllib.parse.urlencode({'username':username,'password':password}).encode('ascii')
            f = request.open(self.api_url + 'api_login.php', params)
            if f is not None:
                data = json.loads(f.read())
                self.sid = data['sid'] if 'sid' in data else ''
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        except json.JSONDecodeError:
            pass

        if self.sid == '':
            print('Unable to login on inkbunny !')
            return False

        # Modify rating option
        try:
            params = urllib.parse.urlencode({'sid':self.sid,'tag[2]':'yes','tag[3]':'yes','tag[4]':'yes','tag[5]':'yes'}).encode('ascii')
            f = request.open(self.api_url + 'api_userrating.php', params)
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass

        return True

    def logout(self):
        request = urllib.request.build_opener()
        request.addheaders = [('User-agent', 'Yiffdex/0.2a')]
        
        try:
            f = request.open(self.api_url + 'api_logout.php?sid=' + self.sid)
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass

    def search(self, md5):
        request = urllib.request.build_opener()
        request.addheaders = [('User-agent', 'Yiffdex/0.2a'),('Content-type','multipart/form-data')]
        
        data = None

        # Search file
        try:
            params = urllib.parse.urlencode({'sid':self.sid,'text':md5,'md5':'yes','submission_ids_only':'yes','keywords':'no'}).encode('ascii')
            f = request.open(self.api_url + 'api_search.php', params)
            if f is not None:
                data = json.loads(f.read())
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        except json.JSONDecodeError:
            pass

        # Not found
        if int(data['results_count_all']) == 0:
            return None

        # Get submission information
        try:
            params = urllib.parse.urlencode({'sid':self.sid,'submission_ids':data['submissions'][0]['submission_id']}).encode('ascii')
            f = request.open(self.api_url + 'api_submissions.php', params)
            if f is not None:
                data = json.loads(f.read())
        except urllib.error.HTTPError:
            pass
        except urllib.error.URLError:
            pass
        except json.JSONDecodeError:
            pass

        # Not found (protection but not possible)
        if data['results_count'] == 0:
            return None

        info = {}
        info['tags'] = [k['keyword_name'] for k in data['submissions'][0]['keywords']]
        info['author'] = data['submissions'][0]['username']
        info['src'] = 'https://inkbunny.net/s/' + data['submissions'][0]['submission_id']

        return info

# Yiffdex class ---------------------------------

class Yiffdex(threading.Thread):

    def __init__(self, cache=None, inkbunny_api = None):
        super().__init__()

        self.stop = False
        self.progress_counter = 0

        self.prescan_callback = []
        self.scan_callback = []

        self.files = []
        self.force = False
        self.cache = cache

        self.e621 = True
        self.e621_username = "guest"

        self.inkbunny = inkbunny_api

        self.interval = 1

    def run(self):
        self.progress_counter = 0

        for f in self.files:
            # Force thread stop
            if self.stop:
                break
            
            # Pre-scan callback
            for c in self.prescan_callback:
                c(f)

            print('[' + str(int(self.get_percent_progress())) + '%] ' + f + ' - ', end='')

            # Continue if we already check the file
            if self.force is False and f in self.cache.data:
                print("CACHED.")
                self.progress_counter += 1
                self.call_scan_callback(f, self.cache.data[f] == '1')
                continue

            if self.force is False and is_marked(f):
                print("PASS.")
                self.progress_counter += 1
                self.call_scan_callback(f, True)
                continue

            # Try to retrieve image information
            print("md5 : ", end='')

             # Get md5 hash
            file_md5 = get_meta_hash(f)
            if file_md5 == '':
                file_md5 = get_name_hash(f)
            if file_md5 == '':
                file_md5 = get_file_hash(f)
            print(file_md5)

            file_info = None

            if self.e621:
                print("Fetching e621 ... ", end='')
                file_info = e621_search(file_md5, self.e621_username)
                print("SUCCESS") if file_info is not None else print("NOT FOUND")
            
            if file_info is None and self.inkbunny is not None:
                print("Fetching inkbunny ...", end='')
                file_info = self.inkbunny.search(file_md5)
                print("SUCCESS") if file_info is not None else print("NOT FOUND")

            # Save result
            if file_info is not None:
                file_comment = 'yiffdex|md5:' + file_md5 + '|' + file_info['src']
                file_keyword = ';'.join(file_info['tags'])

                set_metadata(f, file_keyword, file_info['author'], file_comment)

                if f not in self.cache.data:
                    self.cache.append(f, 1)
            else:
                self.cache.append(f, 0)

            self.progress_counter += 1

            # Scan callback
            self.call_scan_callback(f, file_info is not None)

            time.sleep(self.interval)

    def get_percent_progress(self):
        return self.progress_counter / len(self.files) * 100.0

    def call_scan_callback(self, filename, status):
        for c in self.scan_callback:
            c((filename, status))

# Main ------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--nogui", help="Toggle cmd mode (not show gui)", action='store_true')
    parser.add_argument("-f", "--file", help="Image to tag (multiple file allowed separated by a coma)")
    parser.add_argument("-d", "--dir", help="Folder containing images (multiple folder allowed separated by a coma)")

    parser.add_argument("--force", help="Force information check even if image is already tagged", action='store_true')

    parser.add_argument("--e621", help="Enable e621 search", action='store_true')
    parser.add_argument("--e621_u", help="e621 username (recommended but not required)")

    parser.add_argument("--inkbunny", help="Enable inkbunny search", action='store_true')
    parser.add_argument("--inkbunny_u", help="inkbunny username (required for fetching image where artist disallow guest)")
    parser.add_argument("--inkbunny_p", help="inkbunny password")

    parser.add_argument("--interval", help="Limit time between two search request", type=int, default=1)

    args = parser.parse_args()

    if args.nogui:
        # Initialize caching
        cache = YiffdexCache('yiffdex.cache')
        cache.load()

        # initialize yiffdex
        yiffdex_app = Yiffdex(cache=cache)
        yiffdex_app.interval = args.interval
        yiffdex_app.force = args.force
        yiffdex_app.e621 = args.e621

        # Accounts credentials
        yiffdex_app.e621_username = args.e621_u if args.e621_u else 'guest'
        inkbunny_credentials = (args.inkbunny_u, args.inkbunny_p) if args.inkbunny_u and args.inkbunny_p else ('guest', '')

        # API Initialization
        inkbunny_api = None
        if args.inkbunny:
            inkbunny_api = YiffdexInkbunnyAPI()
            login_result = inkbunny_api.login(inkbunny_credentials[0], inkbunny_credentials[1])

            inkbunny_credentials = ('','') # Do not keep username and password in memory
            args.inkbunny_u = ''
            args.inkbunny_p = ''

            if login_result is False:
                print("Can't connect to Inkbunny with the specified credentials.")
                exit(-1)

        yiffdex_app.inkbunny = inkbunny_api

        # Get list of all files that will be tagged
        file_list = []
        if args.file:
            file_list = [f for f in args.file.split(',') if os.path.splitext(f)[1].lower() == '.jpg' or os.path.splitext(f)[1].lower() == '.jpeg']
        if args.dir:
            tmp_dir = args.dir.split(',')
            for d in tmp_dir:
                if os.path.isdir(d) is False:
                    print(d + " isn't a valid folder !")
                    continue
                file_list.extend([os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and (os.path.splitext(f)[1].lower() == '.jpg' or os.path.splitext(f)[1].lower() == '.jpeg')])
        
        yiffdex_app.files = file_list

        # Run
        yiffdex_app.start()
        yiffdex_app.join()

        if yiffdex_app.inkbunny is not None:
            yiffdex_app.inkbunny.logout()
    else:
        yiffdex_gui = gui.YiffdexFrame()
        yiffdex_gui.mainloop()

    # END