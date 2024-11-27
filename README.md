# XLED Plus - Addons to the XLED package, to create nice effects for Twinkly LED lights

This package relies on the [XLED](https://github.com/scrool/xled) package, which
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


### Getting started

The easiest way to get started is:

1. Make sure you have Python installed on your computer.

2. Download the XLED Plus package, either through GitHub, or by doing
```
pip install xled_plus
```

3. Make sure your Twinkly lights are on-line, i.e connected to the same WiFi as your computer.

4. Try out some of the sample effects in the "xled_plus/samples/" directory: 
```
python -m xled_plus.samples.spectrumlight
```
where "spectrumlight" can be replaced by another filename in that
directory minus the ".py" suffix. It should find your Twinkly lights,
upload the effect, and start playing it.

5. Also, check out the discussion under the "Discussions" tab in this
repository on GitHub, where the "Daily effects" thread contains
comments on the samples and gives some hints on how the effects can be
modified.

6. You can also try the interactive GUI for creating dynamic color
effects, based on the 3D color picker:

You need first to download the latest version of the "colorsphere" package:
```
pip install -U colorsphere
```
Then you can start it with
```
python -m xled_plus.xled_colorcontrol
```
which should bring up a window on your computer with a spherical color
body in the middle, where you can select your own color scheme, and then
use it in one of several included effect types, and upload it to your leds.

