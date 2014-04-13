KAAS: Keynote as a Service -- Google Glass edition
==========================


Preface
-------

Do you give presentations with Keynote and want to be able to show your speakernotes on your glass as you give a presentation.  If so then this is the app for you.

NOTE:  This app only works if you control the presentation from your Glass or via a small web app that we created to be able to control it via a Logitech R400.  Currently web app responds to the page up and page down keys that this is mapped to,  but can be easilly modified to respond to other actions.

This is a heavilly modified version of the KAAS project originally written by  Christopher Neugebauer.  If you are not trying to use Keynote with Google Glass you are advised to go the the repository that this was forked from.  This is a Proof of Concept that I am going to be testing while giving presentations.  Right now it depends on using the Wearscript app.  If people like this long term I will port this to a native Glass (Android) app,  create a proper installer and explore integrations with other presentation tools like impress.js.  If you have any ideas or want to help out with this send me a message!

Also please note that this is a prototype and that the code is not as clean as my Ruby Gems.  I have tried to clean things up wherever I can,  but I am not a Python programmer.  If you are one and have some ideas on how to make this better and add unit test I would love to pair with you to learn how to make it better.


Installation
------------
You will need to be on OSX,  have Keynote 5.1 (there are some changes that have happened in 6.0 that I didn't have time to figure out),  and will need to be using Wearscript and have the wearscript python packages installed.  See http://www.wearscript.com/en/latest/ for instructions on installing wearscript on your Glass and getting started.  


Usage
-----

The app uses websockets to communicate with the backend service.  To use it make sure that you have installed the server and that it is running on our Mac.  You can run it via "python kaas/remote_server.py server 4000".  Configure your Glass to be on the same network as your Mac via the wifi settings.  You will see a line in the wearscript.html file with WS.connect.  Add in the ip address and the port of your server where it asks for that.  If you use the command above to start it the port will be 4000. You will need to copy the wearscript.html file into your wearscript playground editor,  start up the wearscript app and then execute the script.

On your Mac you will need to have Keynote 5.1 running.  Also you will need to have the presentation loaded that you want to work with and start the presentation.  Because of limitations with the Keynote API you need to make sure that you start the presentation on slide 1.

The first slides notes will not show unless you swipe back and then forward once on your glass.  After that you will see your notes as you swipe through the presentation.  There are two ways to control your presentation.  One is via a swipe motion on your glass.  The other is by going to http://your_server_ip_address:8000/kontroller.html and using a logitech remote or the page up and page down keys on another computer.  

Also,  the app currently doesn't automtically resize the text to fit more on the screen.  I have included a few styles and header options in the wearscript to get you going.  Feel free to modify the css and html to fit your particular use case.  The app uses the document.getElementById to add the speaker notes as text into your view.


Original Documentation
======================


Note
----

Some of the original features in Kaas have been disabled in this version such as the security and the ability to select different versions of Keynote.  The code for doing this has been somewhat left in place for the time being.


Introduction
------------

KAAS is a HTTP server for controlling compatible versions of Apple's Keynote 
presentation software via HTTP. It exposes a JSON API for determining the current
slide and build progress, for starting, pausing, and controlling the current
slide show.

It can also send notes and build previews to client devices.

This functionality is also exposed in a basic HTML client, which will be 
extended and documented in the future.

The server is written in Python 2.6+, and has a dependency on PyObjC & AppKit.
Note that the default interpreter is Python 2.6 as this provices PyObjC 
bindings on most Mac OS X installations with no external dependencies.

It currently has very good support for Keynote version 5 (iWork 2009), and has 
experimental-quality support for Keynote version 6 (iWork 2013) -- the quality
of scripting interface is currently far lower in Keynote 6.

This is the server component of Keymote, my Android Keynote Remote, which can
be found on the [Play Store](https://play.google.com/store/apps/details?id=net.noogz.keymote)
(restricted to approved testing users only).


Basic use -- Command Line
-------------------------

Before you can load the server, you'll need to start Keynote up, and open a
presentation file. If you have multiple presentation files open, make sure the
file you want to present from is front-most.

To load up the server, run

    $ ./kaas/remote_server.py

The server will output the following:

    Generating export from frontmost keynote slideshow...
    Generating build previews...
    Starting server...
    Now serving on: http://192.168.1.71:8000
    The PIN number is: 123456

Direct your Keynote Remote app at the listed server, and enter the PIN number.
The PIN number is used to authenticate API calls made from the app -- this 
means that randoms can't take over your presentation. But you really should be using
this on a private network. Really :)

If you want to present from a different deck of slides, you will need to quit 
the server (Ctrl+C), and restart it. The ability to change slide decks is a
planned feature.

### Troubleshooting

If you get an `ImportError: No module named AppKit` message; try running the following:

    $ sudo easy_install-2.6 pyobjc-framework-Cocoa

And running 

    $ python2.6 kaas/remote_server.py


Basic Use -- GUI
----------------

From your command line, run

    $ ./kaas/remote-gui.py


JSON API Documentation
----------------------

Once API documentation is ready, it'll be available at JSON_API.md.


App & Module Structure
----------------------

### `kaas/`

- keynote_script.py -- Low-level python-to-Applescript bridge for keynote, 
  exposes functions needed for controlling keynote.
- kpfutil.py -- Abstract interface for manipulating Keynote's JSON export formats, 
  including assembling build previews from its degenerate textures. 
- kpfutil_v5.py -- Low-level details for manipulating Keynote 5/iWork '09 JSON exports.
  See kpf-json-format.txt for my notes on how the format works.
- kpfutil_v6.py -- Low-level details for manipulating Keynote 6/iWork 2013 JSON exports.
- remote_handler.py -- The GET request handler for the server.
- remote_gui.py -- TK-based GUI for KAAS.
- remote_json.py -- Handler for JSON API calls.
- remote_server.py -- The HTTP server for KAAS. This also handles authentication
  of requests before passing them off to the handler.
- slideshow.py -- A higher-level API for manipulating KPF files and controlling
  keynote than either kpfutil.py or keynote_script.py respectively.

### `docs/`:

- kpf-json.format.txt -- Vague notes I wrote when trying to understand the KPF
  (Keynote JSON) format that KAAS uses to understand the presentation being 
  played.


Licence
-------

Copyright 2013 Christopher Neugebauer and contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
