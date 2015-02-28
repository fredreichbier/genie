genie
=====

A Python module to access Genie engine (Age of Empires etc) files.

How to test
-----------

 * Install `Python`_, `construct`_ and `pyglet`_.
 * Run `python browse_slp.py path/to/your/AOE/directory`
 * This automatically loads `graphics.drs`.
 * You can now enter `ls` to see all available files,
   `play ID` to play a WAV file, `show ID` to display a SLP
   file and, if you're feeling lucky, `showanim ID` to display
   an animated SLP file.

Resources
---------

Kudos to the people who wrote documentation about the proprietary
DRS and SLP formats and the Age of Empires SLP files:

 * http://alexander-jenkins.co.uk/blog/?p=9
 * http://www.digitization.org/wiki/index.php/SLP
 * http://artho.com/age/files/drs.html
 * http://aoe.heavengames.com/downsnew/dlfiles/misc/slplist.zip
 * http://www.ferazelhosting.net/~bryce/re.html (dead)
 * http://www.boekabart.net/aoe2wide/hg/slp.txt (or http://old.zaynar.co.uk/misc2/slp.txt)   
 * http://www.cryer.co.uk/file-types/p/pal.htm

Thank you very much!

License
-------

As stated in the LICENSE file, this Python package is BSD-licensed (2-clause).

.. _python: http://python.org
.. _construct: http://construct.readthedocs.org
.. _pyglet: http://pyglet.org
