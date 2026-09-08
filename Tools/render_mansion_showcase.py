#!/usr/bin/env python3
"""Render the 1.1 showcase from authentic MansionGenerator USDZ exports.

Blender --background --factory-startup --python Tools/render_mansion_showcase.py -- \
  --packages EXPORT_ROOT --output OUTPUT --preview
Use --render for the full camera animation. Source geometry/materials stay intact.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

p = argparse.ArgumentParser()
p.add_argument('--packages', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--style', default='all')
p.add_argument('--preview', action='store_true')
p.add_argument('--render', action='store_true')
p.add_argument('--resume', action='store_true', help='Skip existing frames only when camera and render settings are unchanged')
p.add_argument('--engine', default='BLENDER_EEVEE')
p.add_argument('--cpu', action='store_true')
args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
STYLES = ['modernResort', 'japaneseCourtyard', 'mediterraneanCourtyard', 'palladianVilla']

def setup(style):
    package = args.packages / f'collection-{style}-library-1101.mansion'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.usd_import(filepath=str(package / 'exports/mansion.usdz'))
    scene = bpy.context.scene
    scene.render.engine = args.engine
    if args.engine == 'CYCLES':
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == 'METAL'
        scene.cycles.device = 'CPU' if args.cpu else 'GPU'
        scene.cycles.samples = 24
        scene.cycles.use_denoising = True
    else:
        scene.eevee.taa_render_samples = 32
        scene.eevee.use_fast_gi = True
        scene.eevee.use_raytracing = True
        scene.eevee.ray_tracing_options.resolution_scale = '1'
        for material in bpy.data.materials:
            material.use_raytrace_refraction = True
            if material.use_nodes:
                shader = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if shader and shader.inputs['Transmission Weight'].default_value > 0:
                    # Match exported opacity in a raster renderer. Eevee's
                    # screen-only refraction cannot see concealed interiors.
                    opacity = 1 - shader.inputs['Transmission Weight'].default_value
                    shader.inputs['Alpha'].default_value = opacity
                    shader.inputs['Transmission Weight'].default_value = 0
                    material.surface_render_method = 'DITHERED'
                    material.use_transparency_overlap = False
    scene.render.resolution_x = 960 if args.preview else 1920
    scene.render.resolution_y = 540 if args.preview else 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.compression = 15
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = -0.3
    scene.world = bpy.data.worlds.new('Soft daylight')
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.65, 0.75, 0.86, 1)
    bg.inputs['Strength'].default_value = 0.6
    walls = [o for o in scene.objects if o.type == 'MESH' and o.name.startswith('wall_')]
    corners = [o.matrix_world @ Vector(v) for o in walls for v in o.bound_box]
    width = max(v.x for v in corners) - min(v.x for v in corners)
    depth = max(v.y for v in corners) - min(v.y for v in corners)
    height = max(v.z for v in corners)
    garden = [o for o in scene.objects if o.type == 'MESH' and o.name == 'front_garden']
    gc = [o.matrix_world @ Vector(v) for o in garden for v in o.bound_box]
    front = max(v.y for v in gc) if gc else depth / 2
    garden_width = max(v.x for v in gc)-min(v.x for v in gc) if gc else width
    print('MODEL', style, 'building', width, depth, height, 'garden', garden_width, front, flush=True)
    bpy.ops.mesh.primitive_plane_add(size=2000, location=(0, 0, -0.055))
    ground = bpy.context.object
    ground.name = 'Presentation ground'
    mat = bpy.data.materials.new('Warm stone backdrop')
    mat.diffuse_color = (0.32, 0.35, 0.31, 1)
    mat.use_nodes = True
    mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = mat.diffuse_color
    mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.85
    ground.data.materials.append(mat)
    bpy.ops.object.light_add(type='SUN', location=(20, 30, 40))
    sun = bpy.context.object
    sun.rotation_euler = tuple(math.radians(a) for a in (28, -25, -30))
    sun.data.energy = 2.8
    sun.data.color = (1.0, 0.91, 0.79)
    sun.data.angle = math.radians(8)
    bpy.ops.object.light_add(type='AREA', location=(-15, 25, 30))
    fill = bpy.context.object
    fill.data.energy = 2200
    fill.data.shape = 'DISK'
    fill.data.size = 30
    fill.rotation_euler = (Vector((0,0,2))-fill.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    camera.name = 'Showcase camera'
    camera.data.lens = 38
    camera.data.clip_start = 0.1
    camera.data.clip_end = 2500
    scene.camera = camera
    target = Vector((0, front * 0.24, height * 0.34))
    scale = garden_width
    # Every shot is a real camera move through the same exported scene.
    shots = {
        'modernResort': ((0.65,1.25,0.72), (0.42,0.97,0.50)),
        'japaneseCourtyard': ((0.70,1.08,0.75), (0.22,1.16,0.66)),
        'mediterraneanCourtyard': ((-0.45,1.02,0.47), (0.42,1.02,0.47)),
        'palladianVilla': ((0.04,0.97,0.34), (0.04,0.83,0.58)),
    }
    start,end = shots[style]
    scene.frame_start = 1
    scene.frame_end = 216
    for frame in range(1,217):
        t=(frame-1)/215
        # Smooth arrival/departure with a sustained movement through the middle.
        s=t*t*(3-2*t)
        pos=Vector(tuple(start[i]+(end[i]-start[i])*s for i in range(3))) * scale
        pos.y += front * 0.35
        camera.location=pos
        camera.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler()
        camera.keyframe_insert(data_path='location',frame=frame)
        camera.keyframe_insert(data_path='rotation_euler',frame=frame)
    scene.frame_set(1)
    dest=args.output/style
    dest.mkdir(parents=True,exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(dest/(style+'.blend')))
    info={'style':style,'package':package.name,'frames':216,'fps':30,
          'generatorVersion':'2026.09.07.1',
          'cameraStart':list(start),'cameraEnd':list(end),'scale':scale,
          'buildingBounds':[width,depth,height]}
    (dest/'shot.json').write_text(json.dumps(info,indent=2))
    return scene,dest

for style in STYLES if args.style=='all' else [args.style]:
    scene,dest=setup(style)
    if args.preview:
        for frame in [1,108,216]:
            scene.frame_set(frame)
            scene.render.filepath=str(dest/f'preview-{frame:04d}.png')
            bpy.ops.render.render(write_still=True)
    elif args.render:
        scene.render.filepath=str(dest/'frames/frame-')
        scene.render.use_overwrite = not args.resume
        (dest/'frames').mkdir(exist_ok=True)
        bpy.ops.render.render(animation=True)
