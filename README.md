# Yiffdex

### Description

Yiffdex is a python program for adding e621 or inkbunny tags to your favorite fox and kitten pictures. Its work by searching the md5 of each pictures on e621 and inkbunny API.


### Requirements

* Python 3.5+
* Piexif
* Tkinter

If you're on Windows you can download a standalone executable build in releases section.


### Usage

With GUI, just launch yiffdex.exe if you use the standalone build or yiffdex.py if you use python directly. Add your files and folders, optionally setup your credentials and click on Run.

You can also use console mode, for that you need to add `--nogui` tag in launch params. See the list below for all params :

```
usage: yiffdex.py [-h] [--nogui] [-f FILE] [-d DIR] [--force] [--e621]
                  [--e621_u E621_U] [--inkbunny] [--inkbunny_u INKBUNNY_U]
                  [--inkbunny_p INKBUNNY_P] [--interval INTERVAL]

optional arguments:
  -h, --help            show this help message and exit
  --nogui               Toggle cmd mode (not show gui)
  -f FILE, --file FILE  Image to tag (multiple file allowed separated by a
                        coma)
  -d DIR, --dir DIR     Folder containing images (multiple folder allowed
                        separated by a coma)
  --force               Force information check even if image is already
                        tagged
  --e621                Enable e621 search
  --e621_u E621_U       e621 username (recommended but not required)
  --inkbunny            Enable inkbunny search
  --inkbunny_u INKBUNNY_U
                        inkbunny username (required for fetching image where
                        artist disallow guest)
  --inkbunny_p INKBUNNY_P
                        inkbunny password
  --interval INTERVAL   Limit time between two search request
```

### Changelog

**version 1.0b**
* Add GUI

**version 0.2a**
* Add Inkbunny support
* Fix bugs when filename contains non ascii caracters

**version 0.1a**
* Initial version


### License

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
SOFTWARE.