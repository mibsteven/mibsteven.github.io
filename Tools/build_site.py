#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static discovery pages and shared product sections from data/apps.json."""
from pathlib import Path
from html import escape
import json,re
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/apps.json').read_text())
APPS=sorted(DATA['apps'],key=lambda a:a['rank']); BY_ID={a['id']:a for a in APPS}
CATEGORIES=DATA['categories']; CATS={c['id']:c for c in CATEGORIES}
VERSION='20260905-1'
PLATFORMS={'iphone':'iPhone','ipad':'iPad','mac':'Mac','vision':'Apple Vision Pro','tv':'Apple TV'}
PRICE={'zh':{'paid':'付費下載','free':'免費下載','trial':'免費兩課・後續內購'},'en':{'paid':'Paid download','free':'Free download','trial':'Two free lessons · In-app purchase'}}
def e(s):return escape(str(s),quote=True)
def t(zh,en,lang):return zh if lang=='zh' else en
def name(a,lang):return a['name'][lang]
def product_url(a,lang,prefix=''):return f"{prefix}{a['page']}?lang={lang}"
def catalog_url(lang,category='all',prefix=''):
 return f'{prefix}apps.html?lang={lang}'+(f'&category={category}' if category!='all' else '')
def img(a,lang,prefix='',lazy=True,cover=False):
 if not a['media']:return f'<img src="{prefix}{e(a["icon"])}" alt="{e(name(a,lang))}" width="160" height="160" loading="lazy">'
 m=a['media'][0];ml=lang if lang in m['src'] else next(iter(m['src']));src=m['src'][ml]
 return f'<img src="{prefix}{e(src)}" alt="{e(name(a,lang))} · {t("產品畫面","App view",lang)}" width="{m["width"][ml]}" height="{m["height"][ml]}"'+(' loading="lazy"' if lazy else ' fetchpriority="high"')+' decoding="async">'
def header(prefix=''):
 return f'''<a class="skip-link" href="#main-content">跳至內容 / Skip to content</a>
<header class="site-header"><a class="brand" href="{prefix}index.html" aria-label="Apps by Yu-Hsiang Chang home"><span class="brand-name">Apps by Yu-Hsiang Chang</span><span class="brand-role" data-i18n="brandRole">為學習、創作與空間體驗打造的 Apple App</span></a><div class="nav-area"><nav class="nav" aria-label="Primary navigation"><a href="{prefix}apps.html" data-i18n="navApps">探索 App</a><a href="{prefix}updates.html" data-i18n="navUpdates">最新動態</a><a href="{prefix}support.html" data-i18n="navSupport">關於與支援</a></nav><div class="lang-toggle" aria-label="Language selector"><button type="button" data-lang="zh" aria-pressed="true">繁中</button><button type="button" data-lang="en" aria-pressed="false">EN</button></div></div></header>'''
def footer(prefix=''):
 return f'''<footer class="site-footer"><p data-i18n="footerText">Apps by Yu-Hsiang Chang · 為 iPhone、iPad、Mac 與 Apple Vision Pro 打造的獨立作品。</p><div class="legal-links"><a href="{prefix}privacy.html" data-i18n="privacyPolicy">隱私權政策</a><a href="{prefix}terms.html" data-i18n="termsUse">使用條款</a><a href="{prefix}support.html" data-i18n="support">支援</a><a href="https://www.facebook.com/profile.php?id=61590182079285">Facebook</a></div></footer>'''
def document(titlezh,titleen,description,main,route,bodyclass='',extra=''):
 return f'''<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{e(titlezh)} | Apps by Yu-Hsiang Chang</title><meta name="description" content="{e(description)}"><link rel="canonical" href="https://mibsteven.github.io/{route}"><meta property="og:type" content="website"><meta property="og:site_name" content="Apps by Yu-Hsiang Chang"><meta property="og:title" content="{e(titlezh)} | Apps by Yu-Hsiang Chang"><meta property="og:description" content="{e(description)}"><meta property="og:url" content="https://mibsteven.github.io/{route}"><meta property="og:image" content="https://mibsteven.github.io/assets/social-preview.png"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="assets/site.css?v={VERSION}"></head>
<body class="{bodyclass}"><div class="site-shell" data-title-zh="{e(titlezh)} | Apps by Yu-Hsiang Chang" data-title-en="{e(titleen)} | Apps by Yu-Hsiang Chang">{header()}<main id="main-content">{main}</main>{footer()}</div><script src="assets/site.js?v={VERSION}"></script>{extra}</body></html>\n'''
def topiclinks(lang):
 return '<ul class="topic-links">'+''.join(f'<li><a href="{catalog_url(lang,c["id"])}">{e(c["name"][lang])}<small>{sum(c["id"] in a["categories"] for a in APPS)}</small></a></li>' for c in CATEGORIES)+'</ul>'
def meta(a,lang):
 return f'<div class="product-meta"><span class="price-label">{e(PRICE[lang][a["pricing"]])}</span><span>{e(" / ".join(PLATFORMS[p] for p in a["platforms"]))}</span></div>'
def sectionhead(title,note,lang,href=None):
 return f'<div class="section-head"><div><h2 class="section-title">{title}</h2><p class="section-note">{note}</p></div>'+ (f'<a class="text-link" href="{href}">{t("查看全部","View all",lang)} →</a>' if href else '')+'</div>'
def homepage():
 panels=[]
 for lang in ['zh','en']:
  intro=f'''<section class="home-intro"><span class="eyebrow">INDEPENDENT APPS · BY YU-HSIANG CHANG</span><h1>{t('找到你的下一個 Apple App。','Find your next Apple app.',lang)}</h1><div class="intro-row"><p class="lead">{t('閱讀、音樂、3D 創作，或一段空間冒險。從你想做的事開始，找到適合的作品。','Reading, music, 3D creation, or a spatial adventure. Start with what you want to do.',lang)}</p><form class="search-entry" action="apps.html"><input type="hidden" name="lang" value="{lang}"><input type="search" name="q" aria-label="{t('搜尋 App 名稱或用途','Search by app name or use',lang)}" placeholder="{t('搜尋 App、用途或關鍵字','Search apps, uses, or keywords',lang)}"><button class="button primary" type="submit">{t('搜尋','Search',lang)}</button></form></div><div class="platform-entry"><span>{t('我使用','For my',lang)}</span>{''.join(f'<a href="apps.html?lang={lang}&platform={p}">{"Vision Pro" if p == "vision" else label}</a>' for p,label in PLATFORMS.items() if p != 'tv')}</div><div id="{'apps' if lang=='zh' else 'apps-en'}"><span id="{'audiences' if lang=='zh' else 'audiences-en'}"></span>{topiclinks(lang)}</div></section>'''
  stories=''
  for i,ident in enumerate([a['id'] for a in APPS if a['featured']]):
   a=BY_ID[ident];url=product_url(a,lang)
   stories+=f'<article class="story-card"><a class="story-image" href="{url}" aria-label="{e(name(a,lang))}">{img(a,lang,lazy=i>0)}</a><div class="story-copy">{meta(a,lang)}<h3><a href="{url}">{e(name(a,lang))}</a></h3><p>{e(a["summary"][lang])}</p><a class="text-link" href="{url}">{t("看看怎麼使用","See how it works",lang)} →</a></div></article>'
  featured=f'<section id="{t("featured","featured-en",lang)}">'+sectionhead(t('值得認識的作品','A few places to begin',lang),t('從生活情境出發，看看 App 真正能做什麼。','Real uses, with a closer look at what each app can do.',lang),lang,catalog_url(lang))+f'<div class="featured-stories">{stories}</div></section>'
  lab=BY_ID['spatial-electronics-lab'];recent=[]
  for ident in ['realm-atlas','musheetcreator']:
   a=BY_ID[ident];recent.append(f'<article class="recent-link"><a class="recent-image" href="{product_url(a,lang)}" aria-label="{e(name(a,lang))}">{img(a,lang)}</a><div><small>{e(CATS[a["category"]]["name"][lang])} · {e(PRICE[lang][a["pricing"]])}</small><h3><a href="{product_url(a,lang)}">{e(name(a,lang))} →</a></h3><p>{e(a["summary"][lang])}</p></div></article>')
  new=f'<section id="{t("updates","updates-en",lang)}">'+sectionhead(t('新的體驗，正在展開','New experiences to explore',lang),t('看看近期作品，也可以從兩堂免費的電路課開始。','Discover recent work, or start with two free circuit lessons.',lang),lang,f'updates.html?lang={lang}')+f'''<div class="new-work"><article class="trial-story">{img(lab,lang)}<div class="trial-copy"><span class="eyebrow">{t('免費體驗兩課','TWO FREE LESSONS',lang)}</span><h3>{e(name(lab,lang))}</h3><p>{t('在 Apple Vision Pro 接上第一條電路。前兩課免費，後續四課一次性內購解鎖。','Wire your first circuit on Apple Vision Pro. Try two lessons free, then unlock four more with a one-time purchase.',lang)}</p><a href="{product_url(lab,lang)}">{t('看學習方式與課程','Explore the lessons',lang)} →</a></div></article><div class="recent-links">{''.join(recent)}</div></div></section>'''
  finish=f'<div class="home-finish"><p>{t("我是 Yu-Hsiang Chang，從日常需要與好奇心出發，製作這些 Apple App。所有作品都能在目錄中依用途、裝置與收費方式尋找。","I’m Yu-Hsiang Chang. I make these Apple apps from everyday needs and curiosity. Explore the full collection by use, device, and download type.",lang)}</p><a class="button" href="support.html?lang={lang}">{t("關於與支援","About & support",lang)}</a></div>'
  panels.append(f'<div data-lang-panel="{lang}">{intro}{featured}{new}{finish}</div>')
 (ROOT/'index.html').write_text(document('獨立 Apple App 作品集','Independent Apple apps','依用途與裝置探索 Yu-Hsiang Chang 的 Apple App：閱讀、音樂、3D 創作、遊戲、文化與日常工具。',''.join(panels),'','portfolio-home'))
def select(key,label,options,lang):
 return f'<label>{label}<select name="{key}">'+''.join(f'<option value="{e(value)}">{e(text)}</option>' for value,text in options)+'</select></label>'
def collection(lang):
 notes={
 'music':('從音樂課到自己的作品','From a lesson to your own work','Notelyra 記下課堂，Melody Journal 整理練習，MuSheetCreator 草擬樂譜，MagicStage 為演出換個舞台。依你現在需要的步驟選擇。','Remember lessons with Notelyra, organise practice with Melody Journal, draft a score with MuSheetCreator, or set the stage with MagicStage.'),
 'creating':('先想想，你想製作什麼？','What would you like to make?','地形選 DioramaMapMaker；街景選 DioramaTownBuilder；建築與平面選 MansionGenerator。想收藏實體物件，從 ObjectifyAR 開始。','Choose DioramaMapMaker for landscapes, DioramaTownBuilder for streets, and MansionGenerator for buildings and plans. Start with ObjectifyAR to collect real objects.'),
 'games':('選擇你的玩法','Choose your way to play','生肖適合短局配對；黑暗入侵使用空間手勢；一個普通人的冒險在 Vision Pro 需要控制器；RealmAtlas 則讓你指揮戰略沙盤。','Zodiac offers quick matching, Dark Invasion uses spatial gestures, OrdinaryAdventure requires a controller on Vision Pro, and RealmAtlas puts you in command of a strategy map.')}
 return ''.join(f'<aside class="collection-note" data-collection="{ident}" hidden><h2>{t(z,en,lang)}</h2><p>{t(d,de,lang)}</p></aside>' for ident,(z,en,d,de) in notes.items())
def catalog():
 panels=[]
 for lang in ['zh','en']:
  intro=f'<div class="catalog-intro"><span class="eyebrow">THE COLLECTION</span><h1>{t("探索所有 App","Explore the collection",lang)}</h1><p>{t("先選你想做的事，再找適合手上裝置的 App。免費下載、付費作品與課程試用，都有清楚的標示。","Start with what you want to do, then choose your device. Paid apps, free downloads, and lesson trials are clearly marked.",lang)}</p></div>'
  form=f'<form class="catalog-form" role="search"><label>{t("搜尋名稱或用途","Search by name or use",lang)}<input type="search" name="q" maxlength="160" placeholder="{t("例如：樂譜、電路、旅行","Try: music, circuits, travel",lang)}" autocomplete="off"></label>'
  form+=select('platform',t('使用裝置','Device',lang),[('all',t('所有裝置','Any device',lang))]+list(PLATFORMS.items()),lang)
  form+=select('price',t('下載方式','Download type',lang),[('all',t('全部','All',lang)),('paid',t('付費下載','Paid download',lang)),('free',t('免費下載／體驗','Free download / trial',lang))],lang)
  form+=select('sort',t('排序','Sort by',lang),[('recommended',t('精選順序','Recommended',lang)),('updated',t('最近更新','Recently updated',lang)),('name',t('名稱','Name',lang))],lang)+'</form>'
  buttons='<div class="category-controls" aria-label="'+t('依用途篩選','Filter by use',lang)+'">'
  for ident,label in [('all',t('全部','All',lang))]+[(c['id'],c['name'][lang]) for c in CATEGORIES]:
   count=sum(ident=='all' or ident in a['categories'] for a in APPS)
   buttons+=f'<button class="category-button" type="button" data-category="{ident}" aria-pressed="{str(ident=="all").lower()}">{e(label)} <span data-count>{count}</span></button>'
  buttons+='</div>'
  cards=[]
  for a in APPS:
   search=' '.join(list(a['name'].values())+list(a['summary'].values())+a['aliases']+[label for cat in a['categories'] for label in CATS[cat]['name'].values()])
   attrs=f'id="card-{a["id"]}-{lang}" data-catalog-card data-category-id="{a["category"]}" data-categories="{" ".join(a["categories"])}" data-platforms="{" ".join(a["platforms"])}" data-price="{a["pricing"]}" data-rank="{a["rank"]}" data-updated="{a["updated"]}" data-name="{e(name(a,lang))}" data-search="{e(search)}"'
   url=product_url(a,lang)
   cards.append(f'<article class="catalog-card" {attrs}><a class="catalog-cover{" icon-cover" if not a["media"] else ""}" data-product-link href="{url}" aria-label="{e(name(a,lang))}">{img(a,lang)}</a><div class="catalog-card-copy">{meta(a,lang)}<h2><a data-product-link href="{url}">{e(name(a,lang))}</a></h2><p>{e(a["summary"][lang])}</p>'+ (f'<p class="card-note">{e(a["notes"][lang])}</p>' if a['notes'][lang] else '')+f'<div class="app-links"><a class="text-link" data-product-link href="{url}">{t("了解功能","Explore features",lang)} →</a><a class="text-link" href="{e(a["store"])}">App Store ↗</a></div><p class="updated-date">{t("商店版本更新","Store version updated",lang)} <time datetime="{a["updated"]}">{a["updated"]}</time></p></div></article>')
  empty=f'<div class="empty-results" data-empty hidden><h2>{t("還沒有符合的 App","No matching apps",lang)}</h2><p>{t("試試其他關鍵字，或放寬裝置與用途條件。","Try another keyword or a different device or category.",lang)}</p><button class="reset-button" data-reset type="button">{t("清除篩選","Clear filters",lang)}</button></div>'
  panels.append(f'<section data-lang-panel="{lang}" data-catalog="{lang}">{intro}{form}{buttons}{collection(lang)}<div class="result-toolbar"><p data-result-count role="status" aria-live="polite">{t(f"找到 {len(APPS)} 款 App",f"{len(APPS)} apps found",lang)}</p><button class="reset-button" data-reset type="button" hidden>{t("清除篩選","Clear filters",lang)}</button></div>{empty}<noscript><p>{t("目前顯示完整目錄。啟用 JavaScript 即可使用搜尋與篩選。","The complete collection is shown below. Enable JavaScript to use search and filters.",lang)}</p></noscript><div class="catalog-grid" data-results>{"".join(cards)}</div></section>')
 (ROOT/'apps.html').write_text(document('探索所有 App','Explore all apps','搜尋與篩選 Apple App，依用途、裝置及下載方式找到適合的作品。',''.join(panels),'apps.html','catalog-page',f'<script src="assets/catalog.js?v={VERSION}"></script>'))
def support():
 panels=[]
 for lang in ['zh','en']:
  opts=''.join(f'<option value="{a["id"]}">{e(name(a,lang))}</option>' for a in sorted(APPS,key=lambda a:name(a,lang)))
  links=''.join(f'<li><a href="{product_url(a,lang)}">{e(name(a,lang))}</a></li>' for a in sorted(APPS,key=lambda a:name(a,lang)))
  panels.append(f'''<section class="panel content-card" data-lang-panel="{lang}"><span class="eyebrow">ABOUT & SUPPORT</span><h1 class="page-title">{t('關於與支援','About & support',lang)}</h1><p class="lead">{t('我是 Yu-Hsiang Chang，這些 App 的獨立開發者。從教學、閱讀、音樂與日常需要出發，也持續探索 Apple Vision Pro 能帶來的新體驗。','I’m Yu-Hsiang Chang, the independent developer behind these apps. I build around teaching, reading, music, and everyday needs, and explore new experiences on Apple Vision Pro.',lang)}</p><div class="actions"><a class="button" href="apps.html?lang={lang}">{t('探索作品','Explore the apps',lang)}</a><a class="button" href="https://www.facebook.com/profile.php?id=61590182079285">Facebook</a></div><h2>{t('需要協助？','Need a hand?',lang)}</h2><p>{t('選擇 App，開啟郵件草稿。請附上裝置、系統版本、遇到的問題與重現步驟。','Choose your app to open an email draft. Include your device, OS version, the issue, and steps to reproduce it.',lang)}</p><form class="support-form" data-support-form="{lang}" action="mailto:mibsteven.chang@gmail.com"><label>{t('選擇 App','Choose an app',lang)}<select name="app">{opts}</select></label><button class="button primary" type="submit">{t('開啟支援郵件','Open support email',lang)}</button></form><p><a href="mailto:mibsteven.chang@gmail.com">mibsteven.chang@gmail.com</a></p><h2>{t('下載、購買與相容性','Downloads, purchases, and compatibility',lang)}</h2><p>{t('各產品頁標示可用裝置與下載方式。實際價格、系統需求及可用版本請以所在地區的 App Store 為準。空間電子實驗室可免費體驗前兩課，後續四課以一次性內購解鎖，並提供恢復購買。','Each product page lists devices and download options. Check your local App Store for current prices, requirements, and available versions. Spatial Electronics Lab includes two free lessons; a one-time purchase unlocks the remaining four, with Restore Purchases available.',lang)}</p><h2>{t('所有支援中的作品','All supported apps',lang)}</h2><ul class="support-index">{links}</ul></section>''')
 (ROOT/'support.html').write_text(document('關於與支援','About & support','聯絡獨立開發者 Yu-Hsiang Chang，取得 Apple App 支援、購買與裝置資訊。',''.join(panels),'support.html'))
CAPTIONS={
'vectrafin':[('從帳戶、交易與分類整理收支。','Organise accounts, transactions, and categories. Traditional Chinese interface shown.')],
'buddha-hall':[('在佛堂閱讀經文、記錄祈願與修習。','Read sutras and keep a prayer journal.')],
'sticker-vault':[('集中管理貼圖與匯入的素材。','Keep stickers and imported assets together. Traditional Chinese interface shown.')],
'shiji':[('整理課堂與出缺勤紀錄。','Organise lessons and attendance. Traditional Chinese interface shown.')],
'taipei-veggie-price':[('搜尋蔬果，查看市場行情與價格。','Look up produce and market prices. Traditional Chinese interface shown.'),('從市場資訊了解當日供應情況。','Explore the day’s market information. Traditional Chinese interface shown.')],
 'taiwan-animals':[('在台灣地景裡，從眼前的動物開始自然觀察。','Start a wildlife observation in a Taiwan-inspired landscape. Traditional Chinese interface shown.')],
'musheetcreator':[('把錄音與樂譜草稿放在一起，逐步修正音符。','Keep recordings with score drafts and refine each note.'),('先設定拍號、速度與調號，再開始演奏。','Set the time signature, tempo, and key before playing.')],
'mansion-generator':[('從參數調整建築量體，也能查看平面與動線。','Adjust the building through parameters and inspect its plans and routes.'),('在 Apple Vision Pro 查看生成的建築方案。','Inspect a generated building on Apple Vision Pro.')],
 'the-book-of-tea':[('經文、解釋與朗讀留在同一個閱讀畫面。','Read the classic alongside explanations and listening controls.'),('在沉浸式茶園裡認識製茶的過程。','Explore tea making inside an immersive tea garden.')],
'diorama-map-maker':[('調整地形與材質，預覽生成結果。','Adjust terrain and materials while previewing the result.'),('把生成的微縮景觀放到空間中查看。','Inspect the generated landscape in your space.')],
'diorama-town-builder':[('調整街景配置，建立可重複生成的小鎮。','Adjust a street layout and create a repeatable town.'),('在 Apple Vision Pro 查看立體街景。','Explore the 3D streets on Apple Vision Pro.')],
'home-edu-assistance':[('從家庭儀表板整理每日安排。','Organise the day from the family dashboard.'),('把家庭約定與獎勵契約放在一起。','Keep family agreements and reward contracts together.')],
'swim-power':[('從成績與下一秒的目標，回看訓練進度。','Review progress through results and a next-second goal.'),('用分析結果討論訓練方向。','Use the analysis to discuss training priorities.')],
'zodiac-memory-match':[('記住卡片的位置，找出相同的生肖。','Remember the cards and find matching zodiac animals.')],
'knowmenote':[('在簡單的編輯畫面留下日常文字。','Keep everyday writing in a simple editor.')],
'notelyra':[('錄下音樂課，留下可以回到關鍵片段的記號。','Record a lesson and mark the moments worth returning to.'),('從課程、錄音與筆記開始複習。','Return to lessons, recordings, and notes when reviewing.')]
}
def generated(a,lang,kind):
 if kind=='overview':
  result=f'<div class="product-facts"><dl><div><dt>{t("可用裝置","Devices",lang)}</dt><dd>{e(" / ".join(PLATFORMS[p] for p in a["platforms"]))}</dd></div><div><dt>{t("下載方式","Download",lang)}</dt><dd>{e(PRICE[lang][a["pricing"]])}</dd></div></dl>'
  if a['notes'][lang]:result+=f'<p>{e(a["notes"][lang])}</p>'
  result+=f'<p><a class="text-link" href="{e(a["store"])}">{t("查看 App Store 的價格與相容性","See prices and compatibility on the App Store",lang)} ↗</a></p></div>'
  media=[m for m in a['media'] if not m.get('existing')]
  if media:
   result+='<div class="product-gallery">'
   for i,m in enumerate(media):
    ml=lang if lang in m['src'] else next(iter(m['src']));src='../'+m['src'][ml]
    cap=t(*CAPTIONS.get(a['id'],[(name(a,'zh')+' 產品畫面',name(a,'en')+' app view')]*len(media))[i],lang)
    result+=f'<figure><a href="{e(src)}" aria-label="{e(t("放大畫面：","Enlarge image: ",lang)+cap)}"><img src="{e(src)}" alt="{e(cap)}" width="{m["width"][ml]}" height="{m["height"][ml]}" loading="lazy" decoding="async"></a><figcaption>{e(cap)}</figcaption></figure>'
   result+='</div>'
  return result
 related=[x for x in APPS if x['category']==a['category'] and x['id']!=a['id']][:3]
 if a.get('related'):related=[BY_ID[ident] for ident in a['related']]
 if a['id']=='taiwan-animals':related=[BY_ID['diorama-map-maker']]+related[:2]
 cards=''.join(f'<a href="{product_url(x,lang,"../")}"><small>{e(PRICE[lang][x["pricing"]])} · {e(" / ".join(PLATFORMS[p] for p in x["platforms"]))}</small><strong>{e(name(x,lang))} →</strong><p>{e(x["summary"][lang])}</p></a>' for x in related)
 return f'<div class="related-apps"><h2>{t("接著探索","Keep exploring",lang)}</h2><div class="related-grid">{cards}</div><a class="text-link" data-back-catalog="{a["id"]}" href="{catalog_url(lang,a["category"],"../")}">{t("回到","Back to",lang)} {e(CATS[a["category"]]["name"][lang])} →</a></div>'
def update_products():
 for a in APPS:
  path=ROOT/a['page'];h=path.read_text()
  h=re.sub(r'<!-- generated:(overview|related|breadcrumb)-[^>]+ -->.*?<!-- /generated -->','',h,flags=re.S)
  # Keep authored product copy; refresh shared facts, media, and contextual links.
  for lang in ['zh','en']:
   pattern=r'(<section\b[^>]*data-lang-panel="'+lang+r'"[^>]*>)(.*?)(</section>)'
   def render(match):
    opening,body,closing=match.groups()
    crumb=f'<nav class="breadcrumb" aria-label="{t("所在位置","Breadcrumb",lang)}"><a data-back-catalog="{a["id"]}" href="../apps.html?lang={lang}">{t("探索 App","Explore apps",lang)}</a><span aria-hidden="true">/</span><a href="{catalog_url(lang,a["category"],"../")}">{e(CATS[a["category"]]["name"][lang])}</a></nav>'
    overview='<!-- generated:overview-'+lang+' -->'+generated(a,lang,'overview')+'<!-- /generated -->'
    pos=body.find('<h2')
    if pos<0:pos=len(body)
    body=body[:pos]+overview+body[pos:]
    return opening+'<!-- generated:breadcrumb-'+lang+' -->'+crumb+'<!-- /generated -->'+body+'<!-- generated:related-'+lang+' -->'+generated(a,lang,'related')+'<!-- /generated -->'+closing
   h=re.sub(pattern,render,h,flags=re.S)
  # Old icons are unnecessarily large for their rendered size.
  h=re.sub(r'src="\.\./assets/apps/([^"/]+-icon\.png)"',r'src="../assets/apps/thumbs/\1"',h)
  if 'rel="canonical"' not in h:h=h.replace('</head>',f'<link rel="canonical" href="https://mibsteven.github.io/{a["page"]}">\n</head>')
  if 'og:image' not in h and a['media']:
   m=a['media'][0];src=m['src'].get('en',next(iter(m['src'].values())))
   h=h.replace('</head>',f'<meta property="og:type" content="website"><meta property="og:title" content="{e(name(a,"zh"))}"><meta property="og:description" content="{e(a["summary"]["zh"])}"><meta property="og:image" content="https://mibsteven.github.io/{e(src)}"><meta name="twitter:card" content="summary_large_image">\n</head>')
  h=re.sub(r'<meta name="description" content="[^"]*">',f'<meta name="description" content="{e(a["summary"]["zh"])}">',h)
  path.write_text(h)
def shared_chrome():
 for path in list(ROOT.glob('*.html'))+list((ROOT/'apps').glob('*.html')):
  prefix='../' if path.parent.name=='apps' else '';h=path.read_text()
  h=re.sub(r'<a class="skip-link".*?</a>\s*','',h,flags=re.S)
  h=re.sub(r'<header class="site-header">.*?</header>',header(prefix),h,flags=re.S)
  h=re.sub(r'<footer class="site-footer">.*?</footer>',footer(prefix),h,flags=re.S)
  h=re.sub(r'<main(?![^>]*id=)([^>]*)>',r'<main id="main-content"\1>',h)
  h=re.sub(r'assets/site\.(css|js)(?:\?[^"\s]*)?',lambda m:'assets/site.'+m[1]+'?v='+VERSION,h)
  h=h.replace('href="../index.html#apps"','href="../apps.html"').replace('href="index.html#apps"','href="apps.html"')
  h=h.replace('回到全部 App','探索全部 App').replace('Back to All Apps','Explore all apps')
  path.write_text(h)
def sitemap():
 routes=['','apps.html','support.html','updates.html','privacy.html','terms.html']+[a['page'] for a in APPS]
 content='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 for route in routes:content+=f'<url><loc>https://mibsteven.github.io/{route}</loc></url>\n'
 (ROOT/'sitemap.xml').write_text(content+'</urlset>\n')
 (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://mibsteven.github.io/sitemap.xml\n')
if __name__=='__main__':
 homepage();catalog();support();update_products();shared_chrome();sitemap()
 print(f'Built homepage, catalogue, support, shared navigation, and {len(APPS)} product sections.')
