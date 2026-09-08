#!/usr/bin/env python3
"""Photograph furnished rooms and artwork in the existing showcase scenes.

Blender --background --factory-startup --python Tools/render_mansion_interiors.py -- \
  --packages EXPORT_ROOT --renders RENDER_OUTPUT [--preview] [--style STYLE]

Uses the same complete USDZ models as the exterior film. Only cameras and
presentation lighting change; no walls, furnishings, or artwork are removed.
The resulting stills receive gentle pan/zoom effects during video assembly.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

p = argparse.ArgumentParser()
p.add_argument('--packages', type=Path, required=True)
p.add_argument('--renders', type=Path, required=True)
p.add_argument('--preview', action='store_true')
p.add_argument('--style', default='all')
args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
styles = ['modernResort', 'japaneseCourtyard', 'mediterraneanCourtyard', 'palladianVilla']
dest = args.renders / 'interiors'
dest.mkdir(exist_ok=True)

for style in styles if args.style == 'all' else [args.style]:
    package = args.packages / f'collection-{style}-library-1101.mansion'
    model = json.loads((package / 'mansionModel.json').read_text())
    stops = json.loads((package / 'diagnostics/navigation-graph.json').read_text())['tourStops']
    room = next(r for r in model['rooms'] if r['id'] == 'living')
    center, size = room['center'], room['size']
    bpy.ops.wm.open_mainfile(filepath=str(args.renders / style / f'{style}.blend'))
    scene = bpy.context.scene
    scene.frame_set(1)
    camera = scene.camera
    camera.animation_data_clear()
    camera.data.clip_start = .03
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24 if args.preview else 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = (1280, 720) if args.preview else (2304, 1296)
    scene.view_settings.exposure = -.25
    # Keep the softbox below pendant fixtures, with an offset from the ceiling
    # light's mesh, so the Japanese room receives the intended soft illumination.
    bpy.ops.object.light_add(type='AREA', location=(center['x'] + .65, -center['z'], center['y'] + 2.12))
    fill = bpy.context.object
    fill.name = 'Interior presentation softbox'
    fill.data.energy = 400 if style == 'japaneseCourtyard' else 320
    fill.data.shape, fill.data.size = 'DISK', min(size['x'], size['z']) * .65
    fill.data.color = (1, .93, .84)
    records = []
    for view in ['living', 'art']:
        stop = next(s for s in stops if s['id'] == ('stop-living' if view == 'living' else 'stop-living-art'))
        pos, look = stop['position'], stop['lookAt']
        dx, dz = look['x'] - pos['x'], look['z'] - pos['z']
        length = math.hypot(dx, dz)
        offset = .6 if view == 'living' else .3
        camera.location = (pos['x'] - dx / length * offset, -pos['z'] + dz / length * offset, pos['y'] + 1.4)
        if view == 'living':
            target = Vector((center['x'], -center['z'], center['y'] + .8))
            camera.data.lens = 22
            if style == 'modernResort':
                # Turn toward the sofa's wall relief, keeping the coffee table
                # in the foreground and the full framed composition in view.
                target = Vector((center['x'] - .3, -(center['z'] - 1.05), center['y'] + 1.02))
                camera.data.lens = 20
        else:
            subject = next(e for e in model['elements'] if e['id'] == stop['focusElementID'])
            focus = subject['center']
            target = Vector((focus['x'], -focus['z'], focus['y'] - (.2 if style != 'modernResort' else 0)))
            camera.data.lens = 32
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
        image = dest / f'{style}-{view}{"-review" if args.preview else ""}.png'
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        records.append({'style': style, 'view': view, 'package': package.name,
                        'generatorVersion': '2026.09.07.1', 'seed': 1101,
                        'sourceUSDZSHA256': hashlib.sha256((package / 'exports/mansion.usdz').read_bytes()).hexdigest(),
                        'image': image.name, 'sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
                        'cameraPosition': list(camera.location), 'cameraTarget': list(target),
                        'lensMM': camera.data.lens, 'renderer': 'Blender 5.1 Cycles CPU',
                        'softboxWatts': fill.data.energy, 'geometryModified': False})
        print('INTERIOR', image, flush=True)
    if not args.preview:
        (dest / f'{style}-sources.json').write_text(json.dumps(records, indent=2) + '\n')
        bpy.ops.wm.save_as_mainfile(filepath=str(dest / f'{style}-interior.blend'))
