import os
import re
import maya.cmds as cmds

def xgen_export_ass(character_name, version):
    current_scene = cmds.file(q=True, sn=True)
    scene_name = ""
    if current_scene:
        scene_path = os.path.dirname(current_scene)
        scene_file = os.path.basename(current_scene)
        scene_name = os.path.splitext(scene_file)[0]
    proj_path = scene_path.replace("scenes", "")
    abc_folder_path = os.path.join(proj_path, "cache", "ass")
    cut_in = cmds.playbackOptions(q=True, min=True) - 1
    cut_out = cmds.playbackOptions(q=True, max=True) + 1

    list_xgen = cmds.ls(type='xgmPalette')
    for xgen in list_xgen:
        if re.search(character_name, xgen):
            print(xgen)
            obj = xgen
            ns, obj_name = obj.split(':')
            full_file_path = os.path.join(abc_folder_path, version, obj_name, obj_name + ".ass")
            cmds.select(list_xgen)
            cmds.arnoldExportAss(f=full_file_path,
                                  s=True,
                                  sf=cut_in,
                                  ef=cut_out,
                                  frameStep=1.0,
                                  compressed=True,
                                  expandProcedurals=True,
                                  fullPath=True)
            print(full_file_path)

xgen_export_ass('CH_a', 'v0')
