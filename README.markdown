# World of Warcraft Python API

This is the starting point for my out-of-process World of Warcraft memory manipulation API, written in Python. Caveats: there is no documentation, the offsets are only compatible with WoW 3.2.0a, and only Mac OS X is supported. It should work on Windows once a suitable virtual memory module is written.

The code is in a state where it has a working object manager and not much else. Certain objects, such as `Unit`, contain much more information than others (e.g. `Node` currently only allows for the name of the node to be read). It also includes a script to extract the unit field offsets from a copy of the WoW.exe executable on Windows - this should be compatible with future versions of the game.

## Credits

Thanks to the author of [Pocket Gnome](http://pg.savorydeviate.com/) - some of the offsets I use are taken from there.

## License

This code is dedicated to the public domain.

## Author

Written by [Greg Hughes](http://ghughes.com/) in September 2009.