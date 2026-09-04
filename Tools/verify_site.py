#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate the public catalogue, generated pages, local links, and media budgets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from collections import Counter
from datetime import date
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.tags = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attributes):
        self.tags.append((tag, dict(attributes)))

    def matching(self, tag=None, **attributes):
        return [attrs for name, attrs in self.tags
                if (tag is None or name == tag)
                and all(attrs.get(key) == value for key, value in attributes.items())]


data = json.loads((ROOT / 'data/apps.json').read_text())
apps = data['apps']
ids = [a['id'] for a in apps]
categories = {c['id'] for c in data['categories']}
check(len(ids) == len(set(ids)), 'Duplicate app ids')
check(len({a['rank'] for a in apps}) == len(apps), 'Recommendation ranks must be unique')
check(set(a['page'] for a in apps) == {str(p.relative_to(ROOT)) for p in (ROOT / 'apps').glob('*.html') if not p.stem.endswith(('-privacy', '-terms'))}, 'Catalogue and product pages differ')
check(categories == {a['category'] for a in apps}, 'A primary category is empty or unknown')
for app in apps:
    check(app['category'] in app['categories'], f'{app["id"]}: primary category missing from browse categories')
    check(set(app['categories']) <= categories, f'{app["id"]}: unknown category')
    check(set(app['platforms']) <= {'iphone', 'ipad', 'mac', 'vision', 'tv'} and app['platforms'], f'{app["id"]}: invalid platforms')
    check(app['pricing'] in {'paid', 'free', 'trial'}, f'{app["id"]}: invalid pricing')
    check(urlsplit(app['store']).hostname == 'apps.apple.com', f'{app["id"]}: store destination must be Apple')
    date.fromisoformat(app['updated'])
    check(app['media'], f'{app["id"]}: missing product imagery')
    for field in ['name', 'summary', 'notes']:
        check(set(app[field]) == {'zh', 'en'}, f'{app["id"]}: incomplete {field} translations')
    check(set(app.get('related', [])) <= set(ids) - {app['id']}, f'{app["id"]}: invalid related app')
    for media in app['media']:
        for lang, src in media['src'].items():
            check((ROOT / src).is_file(), f'Missing media: {src}')
            check(media['width'][lang] > 0 and media['height'][lang] > 0, f'Missing image dimensions: {src}')

files = list(ROOT.glob('*.html')) + list((ROOT / 'apps').glob('*.html'))
pages = {p.resolve(): Page(p) for p in files}
for path, page in pages.items():
    page_ids = [attrs['id'] for _, attrs in page.tags if 'id' in attrs]
    check(len(page_ids) == len(set(page_ids)), f'{path.name}: duplicate HTML ids')
    check(len(page.matching('main', id='main-content')) == 1, f'{path.name}: expected one main landmark')
    check(len(page.matching('a', href='#main-content')) == 1, f'{path.name}: missing skip link')
    check(len(page.matching('meta', name='description')) == 1, f'{path.name}: description missing or duplicated')
    for _, attrs in page.tags:
        for attribute in ['href', 'src', 'poster']:
            if attribute not in attrs:
                continue
            target = urlsplit(attrs[attribute])
            if target.scheme or target.netloc:
                continue
            local = (ROOT / unquote(target.path.lstrip('/')) if target.path.startswith('/')
                     else path.parent / unquote(target.path)) if target.path else path
            local = local.resolve()
            check(local.exists(), f'{path.name}: missing {attribute}={attrs[attribute]}')
            if target.fragment and local in pages:
                check(any(a.get('id') == unquote(target.fragment) for _, a in pages[local].tags), f'{path.name}: missing fragment {attrs[attribute]}')
    for img in page.matching('img'):
        check('alt' in img, f'{path.name}: image without alternative text')

catalog = pages[(ROOT / 'apps.html').resolve()]
for lang in ['zh', 'en']:
    cards = [attrs for _, attrs in catalog.tags if 'data-catalog-card' in attrs and attrs.get('id', '').endswith('-' + lang)]
    check({c['id'] for c in cards} == {f'card-{ident}-{lang}' for ident in ids}, f'{lang}: catalogue is incomplete')
    for app in apps:
        card = next(c for c in cards if c['id'] == f'card-{app["id"]}-{lang}')
        check(set(card['data-categories'].split()) == set(app['categories']), f'{app["id"]}: incorrect category membership')
        check(card['data-price'] == app['pricing'], f'{app["id"]}: wrong price label')
        check(set(card['data-platforms'].split()) == set(app['platforms']), f'{app["id"]}: wrong platforms')
    support = pages[(ROOT / 'support.html').resolve()]
    values = [a['value'] for a in support.matching('option')]
    check(all(values.count(ident) == 2 for ident in ids), 'Support selector does not cover every app in both languages')

home = pages[(ROOT / 'index.html').resolve()]
featured = [a for a in apps if a['featured']]
check(2 <= len(featured) <= 4, 'Keep homepage selection focused')
check(len(home.matching('article', **{'class': 'story-card'})) == 2 * len(featured), 'Homepage featured cards do not match catalogue data')
check(len(home.matching('form', action='apps.html')) == 2, 'Homepage needs search in both languages')
for app in featured:
    check(any(a.get('href', '').startswith(app['page']) for a in home.matching('a')), f'Featured app missing: {app["id"]}')

sitemap = ET.parse(ROOT / 'sitemap.xml')
locations = {element.text for element in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
check(all('https://mibsteven.github.io/' + app['page'] in locations for app in apps), 'Sitemap misses products')
check('Sitemap: https://mibsteven.github.io/sitemap.xml' in (ROOT / 'robots.txt').read_text(), 'Missing sitemap discovery')

# Keep purchase promises and existing legal/media content intact.
lab = (ROOT / 'apps/spatial-electronics-lab.html').read_text()
check('前兩課免費' in lab and 'Foundation Course Pack' in lab and 'Code Studio' in lab, 'Trial or curriculum copy lost')
check(next(a for a in apps if a['id'] == 'spatial-electronics-lab')['pricing'] == 'trial', 'Lab must be labelled as a trial')
for ident in ['zodiac-memory-match', 'taipei-veggie-price']:
    check(next(a for a in apps if a['id'] == ident)['pricing'] == 'free', f'{ident}: must remain free')
privacy = (ROOT / 'privacy.html').read_text()
terms = (ROOT / 'terms.html').read_text()
check('Foundation Course Pack is not a subscription' in privacy, 'Existing IAP privacy statement lost')
check('non-consumable in-app purchase' in terms, 'Existing purchase terms lost')
realm = pages[(ROOT / 'apps/realm-atlas.html').resolve()]
check(len(realm.matching('video')) == 2, 'RealmAtlas gameplay video lost')
check((ROOT / 'assets/videos/realm-atlas-gameplay.mp4').stat().st_size < 6 * 1024 * 1024, 'Gameplay video exceeds 6 MB')
updates = (ROOT / 'updates.html').read_text()
for archive in re.findall(r'<section class="updates-archive"[^>]*>.*?</section>', updates, re.S):
    dates = re.findall(r'<time datetime="([\d-]+)">', archive)
    check(dates == sorted(dates, reverse=True), 'Updates are not chronological')

media = list((ROOT / 'assets/showcase').glob('*.webp'))
check(all(p.stat().st_size < 500 * 1024 for p in media), 'A showcase image exceeds 500 KB')
check(sum(p.stat().st_size for p in media) < 8 * 1024 * 1024, 'Showcase image total exceeds 8 MB')
provenance = json.loads((ROOT / 'data/media-sources.json').read_text())
check({p['asset'] for p in provenance} == {str(p.relative_to(ROOT)) for p in media}, 'Image provenance is incomplete')
check(all(not p['source'].startswith('/Users/') for p in provenance), 'Local private paths leaked into provenance')
print(f'PASS: {len(apps)} apps, {len(categories)} categories, {len(files)} HTML pages, all internal links, bilingual catalogue/support, purchase copy, sitemap, and {len(media)} images verified.')
