#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create titles, a 30-second edit, and web assets from the Blender camera renders.

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
        collage.paste(small,((index%2)*960,(index//2)*540))
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
    text(draw,(960,535),'四種風格，生成你的豪宅。',42,cjk=True,anchor='ma')
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
    text(draw,(68,139),'FOUR HOMES IN MOTION  ·  30 SECONDS',27)
    poster.convert('RGB').save(WEB/'poster.webp',quality=88,method=6)
    social=ImageOps.fit(poster.convert('RGB'),(1200,630),method=Image.Resampling.LANCZOS,centering=(.5,.2))
    social.save(WEB/'social.jpg',quality=90,optimize=True)

def run(command):
    subprocess.run(command,check=True)

graphics()
if args.graphics_only:
    raise SystemExit(0)

clips=[]
for style,zh,en in STYLES:
    frames=sorted((OUT/style/'frames').glob('frame-*.png'))
    if len(frames)!=216:
        raise RuntimeError(f'{style}: expected 216 completed frames, found {len(frames)}')
    clip=OUT/style/(style+'.mp4');clips.append(clip)
    run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-framerate','30',
         '-i',str(OUT/style/'frames/frame-%04d.png'),'-loop','1','-i',str(OUT/style/'titles.png'),
         '-filter_complex','[0:v]scale=out_color_matrix=bt709:out_range=tv,format=yuv444p,eq=contrast=1.035:saturation=1.07[v];[v][1:v]overlay=0:0:shortest=1:format=yuv444,format=yuv420p[out]',
         '-map','[out]','-frames:v','216','-c:v','libx264','-preset','slow','-crf','17',
         '-pix_fmt','yuv420p','-movflags','+faststart','-an',*COLOR,str(clip)])
end=OUT/'end-card.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-loop','1','-framerate','30',
     '-i',str(OUT/'end-card.png'),'-t','3.6','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-preset','slow','-crf','17',
     '-pix_fmt','yuv420p',*COLOR,str(end)])
clips.append(end)
audio=args.project/'Sources/PlatformUI/Shared/Resources/Soundscapes'
cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y']
for clip in clips:cmd+=['-i',str(clip)]
for name in ['mansion-breeze.m4a','mansion-water.m4a']:
    cmd+=['-i',str(audio/name)]
filters=[]
for i in range(5):filters.append(f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS[v{i}]')
last='v0'
for i,offset in enumerate([6.6,13.2,19.8,26.4],1):
    filters.append(f'[{last}][v{i}]xfade=transition=fade:duration=0.6:offset={offset}[x{i}]');last=f'x{i}'
filters += [f'[{last}]fade=t=in:st=0:d=0.4,fade=t=out:st=29.5:d=0.5,format=yuv420p[video]',
            '[5:a]atrim=end_sample=384000,asetpts=PTS-STARTPTS,aloop=loop=-1:size=384000,volume=0.65[breeze]',
            '[6:a]atrim=end_sample=384000,asetpts=PTS-STARTPTS,aloop=loop=-1:size=384000,volume=0.24[water]',
            '[breeze][water]amix=inputs=2:normalize=0,afade=t=in:st=0:d=1.5,afade=t=out:st=28:d=2,alimiter=limit=0.8[audio]']
master=OUT/'MansionGenerator-1.1-Showcase-1080p.mp4'
cmd+=['-filter_complex',';'.join(filters),'-map','[video]','-map','[audio]',
      '-t','30','-r','30','-c:v','libx264','-preset','slow','-crf','17','-profile:v','high',
      '-level','4.1','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2',
      '-movflags','+faststart','-metadata','title=MansionGenerator 1.1 — Four homes in motion',
      '-metadata','artist=Apps by Yu-Hsiang Chang','-metadata','comment=Camera animation of authentic MansionGenerator 1.1 exports. Original app soundscapes.',*COLOR,str(master)]
run(cmd)
web=ROOT/'assets/videos/mansion-generator-1-1-showcase.mp4'
run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(master),'-t','30','-c:v','libx264',
     '-preset','slow','-crf','23','-profile:v','high','-level','4.1','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','96k','-movflags','+faststart',*COLOR,str(web)])
report={'title':'MansionGenerator 1.1 — Four homes in motion','durationSeconds':30,
        'width':1920,'height':1080,'fps':30,'renderer':'Blender 5.1 Eevee',
        'generatorVersion':'2026.09.07.1','seed':1101,
        'cameraAnimation':'Four real 3D camera moves; 0.6-second dissolves and a closing card',
        'rasterGlass':'Exported glass opacity mapped to Eevee alpha transparency',
        'sourceGeometry':'Unmodified complete USDZ exports from the 1.1 project validation set',
        'audio':['MansionGenerator/Sources/PlatformUI/Shared/Resources/Soundscapes/'+n for n in ['mansion-breeze.m4a','mansion-water.m4a']],
        'styles':[s for s,_,_ in STYLES],
        'video':str(web.relative_to(ROOT)), 'bytes':web.stat().st_size,
        'sha256':hashlib.sha256(web.read_bytes()).hexdigest()}
(WEB/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
