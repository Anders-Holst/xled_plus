# XLED Plus - Addons to the XLED package, to create nice effects for Twinkly LED lights

This package relies on the XLED package managed by @scrool, which
provides a python interface to Twinkly lights.

This XLED Plus packade provides addons to XLED, for making it easier
to produce various still or animated, simple or advanced, prerecorded
or created in real time, effects on the lights. 

Some of the features in this package may eventually make their way
into the XLED package, once they fulfil the stricter requirements of
quality and stability of XLED. It means that XLED Plus may contain
more experimental features, features that only work on some devices,
features that changes unpredictably from one day to another, or even
outright bugs. On the other hand the development speed might be higher
here, and if there is a bug it might be fixed quicker. As usual, all
code herein are provided as-is with absolutely no guarantee of its
function for any specific purpose. The code in this package is under
the MIT license.

There is currently no general command line interface provided, but you
need to give commands to `python`. Using this package typically goes
with these steps: 

1. Make sure your leds are on-line (connected to you WiFi or your computer connected to them).

2. Either you know the ip-address of your lights already, or the `discover` functionality provided in `xled` is used to find it.
```
from xled.discover import discover
host = discover()['host']
```

3. Create a HighControlInterface object, connected to that ip-address.
```
from xled_plus.highcontrol import HighControlInterface
ctr = HighControlInterface(host)
```

4. Create one of a number of defined effects, adapted to you leds through the control object. 
```
from xled_plus.effects import *
eff = Fire(ctr)
```

5. Launch the effect, which uploads it on your lights and starts it.
```
eff.launch_movie()
```

To install it, either download it from github, or do `pip install
xled_plus`.

Contributions, suggestions, and feedback are welcome. There is a
discussion forum connected to these github pages.

