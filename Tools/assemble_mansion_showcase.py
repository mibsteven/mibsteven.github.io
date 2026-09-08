#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a 40-second exterior, furnished-interior, and artwork showcase.

python3 Tools/assemble_mansion_showcase.py --renders OUTPUT --project MANSION_PROJECT
Requires Pillow and ffmpeg. --graphics-only builds review graphics without the edit.
The source project's own generated breeze/water soundscapes supply the audio.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

p = argparse.ArgumentParser()
p.add_argument('--renders', type=Path, required=True)
p.add_argument('--project', type=Path, required=True)
p.add_argument('--graphics-only', action='store_true')
p.add_argument('--reuse-exterior-clips', action='store_true', help='Reuse the reviewed 7.2-second clips only when exterior renders/titles are unchanged')
args = p.parse_args()
ROOT = Path(__file__).resolve().parent.parent
OUT = args.renders
WEB = ROOT / 'assets/mansion-generator-1.1'
WEB.mkdir(exist_ok=True)
STYLES = [
    ('modernResort', '現代度假宅', 'MODERN RESORT'),
    ('japaneseCourtyard', '日式庭院', 'JAPANESE COURTYARD'),
    ('mediterraneanCourtyard', '地中海庭院', 'MEDITERRANEAN COURTYARD'),
    ('palladianVilla', '帕拉第奧別墅', 'PALLADIAN VILLA'),
]
FPS = 30
DISSOLVE = .4
DURATION = 40
INTERIOR_TITLES = {
    'modernResort': ('幾何浮雕與金屬線條', 'GEOMETRIC RELIEF & METAL DETAILS'),
    'japaneseCourtyard': ('炭黑陶器與小型銅藝品', 'CHARCOAL CERAMIC & BRONZE'),
    'mediterraneanCourtyard': ('暖色陶器與石材基座', 'TERRACOTTA & STONE'),
    'palladianVilla': ('石拱雕塑與銅製底座', 'STONE ARCH & BRONZE BASE'),
}
FONTS = Path('/System/Library/Fonts/Supplemental')
COLOR = ['-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']
def font(size, bold=False, cjk=False):
    return ImageFont.truetype(str(FONTS / ('Arial Unicode.ttf' if cjk else 'Arial Bold.ttf' if bold else 'Arial.ttf')), size)

def text(draw, xy, value, size, bold=False, cjk=False, fill='white', anchor=None):
    draw.text(xy, value, font=font(size,bold,cjk), fill=fill, anchor=anchor)

def still(style):
    full = OUT/style/'frames/frame-0108.png'
    return Image.open(full if full.exists() else OUT/style/'preview-0108.png').convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS)

def graphics():
    collage=Image.new('RGB',(1920,1080),'#16201e')
    for index,(style,zh,en) in enumerate(STYLES):
        source=still(style)
        small=source.resize((960,540),Image.Resampling.LANCZOS)
        small.save(WEB/f'{style}.webp',quality=86,method=6)
        tile = small
        if index in (1,2):
            tile = Image.open(OUT/'interiors'/f'{style}-living.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS)
        collage.paste(tile,((index%2)*960,(index//2)*540))
        layer=Image.new('RGBA',(1920,1080),(0,0,0,0))
        draw=ImageDraw.Draw(layer)
        for y in range(250):
            draw.line([(0,y),(1920,y)],fill=(8,18,17,int(118*(1-y/250)**2)))
        for y in range(760,1080):
            draw.line([(0,y),(1920,y)],fill=(8,18,17,int(175*((y-760)/320)**.8)))
        text(draw,(92,66),'MansionGenerator',32,bold=True)
        text(draw,(92,108),'1.1  /  FOUR COLLECTIONS',20)
        draw.line([(92,828),(152,828)],fill='#dfba83',width=4)
        text(draw,(92,850),zh,52,cjk=True)
        text(draw,(94,926),en,27)
        text(draw,(1800,940),f'0{index+1} / 04',24,anchor='ra')
        layer.save(OUT/style/'titles.png')
    end=collage.convert('RGBA')
    tint=Image.new('RGBA',end.size,(8,20,17,167));end=Image.alpha_composite(end,tint)
    draw=ImageDraw.Draw(end)
    text(draw,(960,332),'FOUR COLLECTIONS  /  VERSION 1.1',27,anchor='ma',fill='#e0c9a4')
    text(draw,(960,403),'MansionGenerator',94,bold=True,anchor='ma')
    text(draw,(960,535),'四種風格，從庭園走進生活。',42,cjk=True,anchor='ma')
    text(draw,(960,620),'iPhone · iPad · Mac · Apple Vision Pro',29,anchor='ma')
    draw.rounded_rectangle((770,700,1150,778),radius=39,fill='#f1eee5')
    text(draw,(960,720),'View on the App Store',27,bold=True,anchor='ma',fill='#142320')
    text(draw,(960,952),'Apps by Yu-Hsiang Chang  ·  mibsteven.github.io',24,anchor='ma',fill='#e2e5dd')
    end.convert('RGB').save(OUT/'end-card.png')
    # Poster keeps the architecture brighter than the final call-to-action card.
    poster=collage.convert('RGBA')
    shade=Image.new('RGBA',poster.size,(0,0,0,0));sd=ImageDraw.Draw(shade)
    for y in range(400):
        sd.line([(0,y),(1920,y)],fill=(8,20,17,int(210*(1-y/400)**.65)))
    poster=Image.alpha_composite(poster,shade);draw=ImageDraw.Draw(poster)
    text(draw,(64,50),'MansionGenerator 1.1',62,bold=True)
    text(draw,(68,139),'EXTERIORS · INTERIORS · ART  /  40 SECONDS',27)
    poster.convert('RGB').save(WEB/'poster.webp',quality=88,method=6)
    social=ImageOps.fit(poster.convert('RGB'),(1200,630),method=Image.Resampling.LANCZOS,centering=(.5,.2))
    social.save(WEB/'social.jpg',quality=90,optimize=True)

def run(command):
    subprocess.run(command,check=True)

graphics()
if args.graphics_only:
    raise SystemExit(0)

# Exterior clips are kept as source masters. Retiming makes room for the new
# interiors while retaining each camera's full travel rather than cutting it off.
edit = OUT / 'interior-edit'
edit.mkdir(exist_ok=True)
shots = []

def encode_args():
    return ['-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart','-an',*COLOR]

def label(style, view, zh, en):
    layer = Image.new('RGBA',(1920,1080),(0,0,0,0))
    draw = ImageDraw.Draw(layer)
    for y in range(235):
        draw.line([(0,y),(1920,y)],fill=(8,18,17,int(166*(1-y/235)**1.25)))
    title, subtitle = (zh+'・客廳',en+' / LIVING ROOM') if view == 'living' else INTERIOR_TITLES[style]
    draw.line([(80,58),(124,58)],fill='#dfba83',width=3)
    text(draw,(80,77),title,37,cjk=True)
    text(draw,(82,133),subtitle,22)
    text(draw,(1838,81),'MansionGenerator 1.1',25,bold=True,anchor='ra')
    path = edit / f'{style}-{view}-title.png'
    layer.save(path)
    return path

for index,(style,zh,en) in enumerate(STYLES):
    original = OUT/style/(style+'.mp4')
    if not (args.reuse_exterior_clips and original.exists()):
        frames = sorted((OUT/style/'frames').glob('frame-*.png'))
        if len(frames) != 216:
            raise RuntimeError(f'{style}: expected 216 completed frames, found {len(frames)}')
        run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-framerate','30',
             '-i',str(OUT/style/'frames/frame-%04d.png'),'-loop','1','-i',str(OUT/style/'titles.png'),
             '-filter_complex','[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv444p,eq=contrast=1.035:saturation=1.07[v];[v][1:v]overlay=0:0:shortest=1:format=yuv444,format=yuv420p[out]',
             '-map','[out]','-frames:v','216',*encode_args(),str(original)])
    clip = edit / f'{style}-exterior.mp4'
    run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(original),
         '-vf','setpts=PTS*4/7.2,fps=30','-frames:v','120',*encode_args(),str(clip)])
    shots.append({'style':style,'view':'exterior','duration':4,'clip':str(clip),
                  'motion':'Original 7.2-second 3D camera move retimed to 4 seconds'})
    for view,duration in [('living',3.8),('art',2.5)]:
        source = OUT/'interiors'/f'{style}-{view}.png'
        frames = round(duration*FPS)
        n = frames-1
        if view == 'art':
            z,x,y = f'1.015+0.045*on/{n}', '(iw-iw/zoom)*.5', '(ih-ih/zoom)*.42'
            motion = 'Slow push in toward the artwork'
        elif index == 0:
            z,x,y = f'1.01+0.04*on/{n}', '(iw-iw/zoom)*.35', '(ih-ih/zoom)*.4'
            motion = 'Slow push in toward seating and wall art'
        elif index == 1:
            z,x,y = '1.055', f'(iw-iw/zoom)*(.15+.7*on/{n})', '(ih-ih/zoom)*.5'
            motion = 'Gentle left-to-right pan'
        elif index == 2:
            z,x,y = f'1.06-0.05*on/{n}', '(iw-iw/zoom)*.5', '(ih-ih/zoom)*.42'
            motion = 'Slow pull back to reveal furniture and ceramic display'
        else:
            z,x,y = '1.055', f'(iw-iw/zoom)*(.85-.7*on/{n})', '(ih-ih/zoom)*.45'
            motion = 'Gentle right-to-left pan across the seating arrangement'
        title = label(style,view,zh,en)
        clip = edit / f'{style}-{view}.mp4'
        effect = f"[0:v]scale=3840:2160:flags=lanczos,zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s=1920x1080:fps=30,scale=out_color_matrix=bt709:out_range=tv,format=yuv444p[v];[v][1:v]overlay=0:0:shortest=1:format=yuv444,format=yuv420p[out]"
        run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(source),'-loop','1','-i',str(title),
             '-filter_complex',effect,'-map','[out]','-frames:v',str(frames),*encode_args(),str(clip)])
        shots.append({'style':style,'view':view,'duration':duration,'clip':str(clip),
                      'source':str(source.relative_to(OUT)),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
                      'motion':motion,'technique':'Pan/zoom animation of an authentic exported-model still'})

end = OUT/'end-card.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-loop','1','-framerate','30',
     '-i',str(OUT/'end-card.png'),'-t','3.6','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',*encode_args(),str(end)])
shots.append({'view':'closing','duration':3.6,'clip':str(end)})
# Derive offsets and fades from the timeline. 4 × (4 + 3.8 + 2.5) + 3.6
# minus 12 × .4-second dissolves = exactly 40 seconds / 1200 frames.
next_start = 0
for shot in shots:
    shot['start'] = round(next_start,3)
    shot['end'] = round(next_start + shot['duration'],3)
    next_start = shot['end'] - DISSOLVE
assert abs(shots[-1]['end'] - DURATION) < .001
(OUT/'timeline-interiors.json').write_text(json.dumps(shots,ensure_ascii=False,indent=2)+'\n')
audio = OUT/'audio'
if not all((audio/n).exists() for n in ['mansion-breeze.m4a','mansion-water.m4a']):
    audio = args.project/'Sources/PlatformUI/Shared/Resources/Soundscapes'
cmd = ['ffmpeg','-hide_banner','-loglevel','warning','-y','-filter_complex_threads','4']
for shot in shots: cmd += ['-i',shot['clip']]
for name in ['mansion-breeze.m4a','mansion-water.m4a']: cmd += ['-i',str(audio/name)]
filters = [f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]' for i in range(len(shots))]
last = 'v0'
for i,shot in enumerate(shots[1:],1):
    filters.append(f'[{last}][v{i}]xfade=transition=fade:duration={DISSOLVE}:offset={shot["start"]}[x{i}]')
    last = f'x{i}'
count = len(shots)
filters += [f'[{last}]fade=t=in:st=0:d=0.4,fade=t=out:st={DURATION-.5}:d=0.5,format=yuv420p[video]',
            f'[{count}:a]atrim=end_sample=384000,asetpts=PTS-STARTPTS,aloop=loop=-1:size=384000,volume=0.65[breeze]',
            f'[{count+1}:a]atrim=end_sample=384000,asetpts=PTS-STARTPTS,aloop=loop=-1:size=384000,volume=0.24[water]',
            f'[breeze][water]amix=inputs=2:normalize=0,afade=t=in:st=0:d=1.5,afade=t=out:st={DURATION-2}:d=2,alimiter=limit=0.8[audio]']
master = OUT/'MansionGenerator-1.1-Showcase-Interiors-1080p.mp4'
cmd += ['-filter_complex',';'.join(filters),'-map','[video]','-map','[audio]',
        '-t',str(DURATION),'-r','30','-c:v','libx264','-preset','slow','-crf','17','-profile:v','high',
        '-level','4.1','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2',
        '-movflags','+faststart','-metadata','title=MansionGenerator 1.1 — Outside and within',
        '-metadata','artist=Apps by Yu-Hsiang Chang','-metadata',
        'comment=Authentic MansionGenerator 1.1 exports: exterior camera animation and interior/artwork stills animated with pan and zoom. Original app soundscapes.',*COLOR,str(master)]
run(cmd)
web = ROOT/'assets/videos/mansion-generator-1-1-showcase.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(master),'-t',str(DURATION),'-c:v','libx264',
     '-preset','slow','-crf','23','-profile:v','high','-level','4.1','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','96k','-movflags','+faststart',*COLOR,str(web)])
interior_sources = []
for style,_,_ in STYLES:
    interior_sources.extend(json.loads((OUT/'interiors'/f'{style}-sources.json').read_text()))
report = {'title':'MansionGenerator 1.1 — Outside and within','edition':'Interiors and artwork',
          'durationSeconds':DURATION,'width':1920,'height':1080,'fps':FPS,
          'renderer':'Blender 5.1: Eevee exterior animations, Cycles interior stills',
          'generatorVersion':'2026.09.07.1','seed':1101,
          'cameraAnimation':'Four exterior 3D camera moves, four furnished-room stills and four artwork stills with pan/zoom, 0.4-second dissolves, closing card',
          'rasterGlass':'Exported glass opacity mapped to Eevee alpha transparency in the shared scenes',
          'sourceGeometry':'Unmodified complete USDZ exports from the 1.1 project validation set; presentation cameras and lighting added in Blender',
          'audio':['MansionGenerator/Sources/PlatformUI/Shared/Resources/Soundscapes/'+n for n in ['mansion-breeze.m4a','mansion-water.m4a']],
          'styles':[s for s,_,_ in STYLES], 'interiorSources':interior_sources,
          'timeline':[{k:v for k,v in shot.items() if k != 'clip'} for shot in shots],
          'video':str(web.relative_to(ROOT)),'bytes':web.stat().st_size,'sha256':hashlib.sha256(web.read_bytes()).hexdigest()}
(WEB/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['title','durationSeconds','bytes','sha256']},ensure_ascii=False,indent=2))
