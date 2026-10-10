# encoding: utf-8
"""Compact Han reference grid for Glyphs 3."""
import math
import os
import re
import subprocess
import threading
import time
from collections import defaultdict

import objc
from AppKit import (NSApp, NSButton, NSFont, NSImage, NSImageAbove,
                    NSImageScaleProportionallyUpOrDown, NSMakeRect, NSScrollView, NSSlider,
                    NSTextAlignmentCenter, NSTextField, NSView, NSViewWidthSizable,
                    NSViewHeightSizable, NSViewMaxYMargin, NSViewFrameDidChangeNotification)
from PyObjCTools.AppHelper import callAfter
from Foundation import NSNotificationCenter
from GlyphsApp import Glyphs, GSEditViewController, GSGlyph, UPDATEINTERFACE
from GlyphsApp.plugins import PalettePlugin

DATA_FILE = os.path.join(os.path.dirname(__file__), 'IVD_Sequences.txt')
CACHE_DIR = os.path.expanduser('~/Library/Caches/HanVariantReference')
SIZE_DEFAULTS_KEY = 'com.palf.HanVariantReference.gridSize'
MIN_GRID_SIZE = 40
MAX_GRID_SIZE = 156
DEFAULT_GRID_SIZE = 104
REGIONS = [('JP', 'j'), ('CN', 'g'), ('TW', 't'), ('HK', 'h'), ('KR', 'k')]

STRINGS = {
    'name': {'en': 'Han Variant Reference', 'ja': '漢字字形リファレンス', 'zh-Hans': '汉字字形参考', 'zh-Hant': '漢字字形參考', 'ko': '한자 자형 참고'},
    'regional': {'en': 'Regional forms', 'ja': '地域別字形', 'zh-Hans': '地区字形', 'zh-Hant': '地區字形', 'ko': '지역별 자형'},
    'slider': {'en': 'Grid size', 'ja': 'グリッドサイズ', 'zh-Hans': '网格大小', 'zh-Hant': '網格大小', 'ko': '격자 크기'},
    'insert': {'en': 'Double-click to insert %s', 'ja': 'ダブルクリックで %s を追加', 'zh-Hans': '双击插入 %s', 'zh-Hant': '按兩下插入 %s', 'ko': '두 번 클릭하여 %s 삽입'},
}

def tr(key):
    return Glyphs.localize(STRINGS[key])

def restored_grid_size(value):
    try:
        size = float(value)
    except (TypeError, ValueError):
        return DEFAULT_GRID_SIZE
    if not math.isfinite(size):
        return DEFAULT_GRID_SIZE
    return max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, int(round(size))))

def load_ivd():
    result = defaultdict(list)
    with open(DATA_FILE, encoding='utf-8') as source:
        for line in source:
            line = line.split('#', 1)[0].strip()
            if line:
                sequence, collection, identifier = [part.strip() for part in line.split(';')]
                base, selector = [int(value, 16) for value in sequence.split()]
                result[base].append((selector, collection, identifier))
    return result


def glyphwiki_name(base, selector=None, region=None):
    stem = 'u%x' % base
    return '%s-u%x' % (stem, selector) if selector is not None else '%s-%s' % (stem, region)


def reference_for_glyph(font, glyph):
    """Resolve a suffixed glyph to its unsuffixed reference character."""
    if glyph is None:
        return None, None
    base_name = glyph.name.split('.', 1)[0]
    source = glyph
    if base_name != glyph.name:
        try:
            source = font.glyphs[base_name] or glyph
        except KeyError:
            source = glyph
    unicode_hex = getattr(source, 'unicode', None) or getattr(glyph, 'unicode', None)
    if unicode_hex:
        try:
            return int(unicode_hex, 16), base_name
        except ValueError:
            pass
    match = re.fullmatch(r'uni([0-9A-Fa-f]{4})|u([0-9A-Fa-f]{5,6})', base_name)
    if match:
        return int(match.group(1) or match.group(2), 16), base_name
    return None, base_name


def variant_glyph_name(base_name, selector):
    return '%s.uv%03d' % (base_name.split('.', 1)[0], selector - 0xE0100 + 17)


def append_variant_to_tab(tab, font, base_name, selector):
    target = variant_glyph_name(base_name, selector)
    try:
        glyph = font.glyphs[target]
    except KeyError:
        glyph = None
    if glyph is None:
        glyph = GSGlyph(target)
        font.glyphs.append(glyph)
    layers = list(tab.layers)
    index = min(max(int(tab.layersCursor), 0), len(layers))
    active = tab.activeLayer()
    master_id = getattr(active, 'associatedMasterId', None)
    try:
        layer = glyph.layers[master_id] if master_id else glyph.layers[0]
    except (KeyError, IndexError):
        layer = glyph.layers[0]
    layers.insert(index, layer)
    tab.layers = layers
    tab.layersCursor = index
    tab.redraw()


class HanVariantReference(PalettePlugin):
    @objc.python_method
    def settings(self):
        self.name = tr('name')
        self.ivd = load_ivd()
        self.current_base = None
        self.current_tab = None
        self.base_name = None
        self.images = {}
        self.missing = set()
        self.loading = set()
        self.last_width = 0
        self.last_variant_click = None
        self.size = restored_grid_size(Glyphs.defaults.get(SIZE_DEFAULTS_KEY))
        self.dialog = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 250, 350))
        self.scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(0, 30, 250, 320))
        self.scroll.setHasVerticalScroller_(True)
        self.scroll.setDrawsBackground_(False)
        self.scroll.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        self.scroll.setPostsFrameChangedNotifications_(True)
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self, 'scrollFrameChanged:', NSViewFrameDidChangeNotification, self.scroll)
        self.content = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 250, 320))
        self.scroll.setDocumentView_(self.content)
        self.dialog.addSubview_(self.scroll)
        self.slider = NSSlider.alloc().initWithFrame_(NSMakeRect(14, 3, 222, 23))
        self.slider.setMinValue_(MIN_GRID_SIZE)
        self.slider.setMaxValue_(MAX_GRID_SIZE)
        self.slider.setDoubleValue_(self.size)
        self.slider.setContinuous_(True)
        self.slider.setAutoresizingMask_(NSViewWidthSizable | NSViewMaxYMargin)
        self.slider.setTarget_(self)
        self.slider.setAction_('sizeChanged:')
        self.slider.setAccessibilityLabel_(tr('slider'))
        self.dialog.addSubview_(self.slider)
        self.render()

    @objc.python_method
    def start(self):
        Glyphs.addCallback(self.update, UPDATEINTERFACE)

    @objc.python_method
    def __del__(self):
        try:
            Glyphs.removeCallback(self.update)
            NSNotificationCenter.defaultCenter().removeObserver_(self)
        except Exception:
            pass

    def minHeight(self):
        return 180

    def maxHeight(self):
        return 650

    @objc.python_method
    def update(self, sender):
        try:
            tab = sender.object()
            if not isinstance(tab, GSEditViewController):
                tab = None
            layer = tab.activeLayer() if tab else None
            glyph = layer.parent if layer else None
            base, base_name = reference_for_glyph(tab.parent, glyph) if tab else (None, None)
            width = self.available_width()
            if base != self.current_base or base_name != self.base_name or tab is not self.current_tab:
                self.current_base = base
                self.current_tab = tab
                self.base_name = base_name
                self.request_images()
                self.render()
            elif abs(width - self.last_width) > 2:
                self.render()
        except Exception as error:
            print('Han Variant Reference update:', error)

    @objc.python_method
    def available_width(self):
        return max(120, int(self.scroll.contentView().bounds().size.width))

    @objc.python_method
    def request_images(self):
        base = self.current_base
        if base is None:
            return
        names = [glyphwiki_name(base, region=region) for _, region in REGIONS]
        names += [glyphwiki_name(base, selector=selector) for selector, _, _ in self.ivd.get(base, [])]
        for name in set(names):
            if name not in self.images and name not in self.missing and name not in self.loading:
                self.loading.add(name)
                threading.Thread(target=self.fetch_image, args=(name,), daemon=True).start()

    @objc.python_method
    def label(self, title, x, y, width, size=11, bold=False, center=False):
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, width, 18))
        field.setStringValue_(title)
        field.setBezeled_(False)
        field.setDrawsBackground_(False)
        field.setEditable_(False)
        field.setSelectable_(False)
        if center:
            field.setAlignment_(NSTextAlignmentCenter)
        field.setFont_(NSFont.boldSystemFontOfSize_(size) if bold else NSFont.systemFontOfSize_(size))
        self.content.addSubview_(field)

    @objc.python_method
    def visible_items(self):
        base = self.current_base
        if base is None:
            return [], []
        regions = [(label, glyphwiki_name(base, region=region), None)
                   for label, region in REGIONS
                   if glyphwiki_name(base, region=region) in self.images]
        seen = set()
        variants = []
        for selector, collection, identifier in self.ivd.get(base, []):
            name = glyphwiki_name(base, selector=selector)
            if selector not in seen and name in self.images:
                variants.append(('VS%d' % (selector - 0xE0100 + 17), name, selector))
                seen.add(selector)
        return regions, variants

    @objc.python_method
    def tile(self, title, image_name, selector, x, y, size):
        button = NSButton.alloc().initWithFrame_(NSMakeRect(x, y, size, size + 18))
        button.setBordered_(False)
        button.setTitle_(title)
        button.setFont_(NSFont.systemFontOfSize_(11))
        button.setImagePosition_(NSImageAbove)
        button.cell().setImageScaling_(NSImageScaleProportionallyUpOrDown)
        button.setImage_(self.images[image_name])
        button.setTarget_(self)
        button.setAction_('tileClicked:')
        button.setTag_(selector if selector is not None else -1)
        if selector is not None:
            button.setToolTip_(tr('insert') % title)
        self.content.addSubview_(button)

    @objc.python_method
    def render(self):
        for subview in list(self.content.subviews()):
            subview.removeFromSuperview()
        width = self.available_width()
        self.last_width = width
        size = int(self.size)
        for image in self.images.values():
            image.setSize_((size, size))
        gap = 4 if size < 64 else 6
        cols = max(1, int((width - 16 + gap) // (size + gap)))
        regions, variants = self.visible_items()
        sections = []
        if regions:
            sections.append((tr('regional'), regions))
        if variants:
            sections.append(('IVD', variants))
        tile_height = size + 18
        height = 8
        for _, items in sections:
            rows = (len(items) + cols - 1) // cols
            height += 20 + rows * (tile_height + gap) + 4
        viewport_height = max(100, int(self.scroll.contentView().bounds().size.height))
        height = max(height, viewport_height)
        self.content.setFrame_(NSMakeRect(0, 0, width, height))
        y = height - 8
        for heading, items in sections:
            y -= 18
            self.label(heading, 8, y, width - 16, bold=True)
            y -= 4
            for index, (title, name, selector) in enumerate(items):
                row, col = divmod(index, cols)
                x = 8 + col * (size + gap)
                tile_y = y - (row + 1) * (tile_height + gap) + gap
                self.tile(title, name, selector, x, tile_y, size)
            y -= ((len(items) + cols - 1) // cols) * (tile_height + gap) + 4
        self.scroll.contentView().scrollToPoint_((0, max(0, height - viewport_height)))
        self.scroll.reflectScrolledClipView_(self.scroll.contentView())

    def scrollFrameChanged_(self, notification):
        if abs(self.available_width() - self.last_width) > 2:
            self.render()

    def sizeChanged_(self, sender):
        self.size = restored_grid_size(sender.doubleValue())
        Glyphs.defaults[SIZE_DEFAULTS_KEY] = self.size
        self.render()

    @objc.python_method
    def fetch_image(self, name):
        try:
            os.makedirs(CACHE_DIR, exist_ok=True)
            path = os.path.join(CACHE_DIR, name + '.svg')
            if not os.path.exists(path):
                url = 'https://glyphwiki.org/glyph/%s.svg' % name
                result = subprocess.run(['/usr/bin/curl', '-fLsS', '--max-time', '12', url], capture_output=True, timeout=15)
                if result.returncode or b'<svg' not in result.stdout[:512]:
                    callAfter(self.image_missing, name)
                    return
                with open(path, 'wb') as output:
                    output.write(result.stdout)
            callAfter(self.image_ready, name, path)
        except Exception as error:
            print('Han Variant Reference image %s: %s' % (name, error))
            callAfter(self.image_missing, name)

    @objc.python_method
    def image_ready(self, name, path):
        self.loading.discard(name)
        image = NSImage.alloc().initWithContentsOfFile_(path)
        if image:
            image.setSize_((self.size, self.size))
            self.images[name] = image
            if self.current_base is not None and name.startswith('u%x-' % self.current_base):
                self.render()
        else:
            self.missing.add(name)

    @objc.python_method
    def image_missing(self, name):
        self.loading.discard(name)
        self.missing.add(name)

    def tileClicked_(self, sender):
        selector = int(sender.tag())
        if selector < 0:
            return
        now = time.monotonic()
        previous = self.last_variant_click
        event = NSApp.currentEvent()
        is_double_click = bool(event and event.clickCount() >= 2)
        if previous and previous[0] == selector and now - previous[1] <= 0.5:
            is_double_click = True
        if not is_double_click:
            self.last_variant_click = (selector, now)
            return
        self.last_variant_click = None
        try:
            if self.current_tab is not None:
                append_variant_to_tab(self.current_tab, self.current_tab.parent, self.base_name, selector)
        except Exception as error:
            Glyphs.showNotification(tr('name'), str(error))

    @objc.python_method
    def __file__(self):
        return __file__
