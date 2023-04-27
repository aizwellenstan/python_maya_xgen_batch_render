import xgenm as xg
import xgenm.xgGlobal as xgg
import xgenm.XgExternalAPI as xge
import os
import maya.cmds as cmds
import os
import maya.cmds as cmds
import xgenm.xmaya.xgmExternalAPI as xgmExternalAPI
import xgenm.XgExternalAPI as xge
import xgenm.xgGlobal as xgg
if xgg.Maya:
    import maya.mel as mel

strCurrentScene = cmds.file( q=True, sn=True )
strSceneName = ""
if strCurrentScene:
    strScenePath = os.path.dirname( strCurrentScene )
    strSceneFile = os.path.basename( strCurrentScene )
    strSceneName = os.path.splitext( strSceneFile )[0];
projPath = strScenePath.replace("scenes","")
abcFolderPath = projPath + "cache/alembic"

def HideAll():
    modelPanels = cmds.getPanel(type = 'modelPanel')
    for eachmodelPanel in modelPanels:
        cmds.modelEditor( eachmodelPanel, e=True, allObjects= False)

def SetRenderFrame():
    # Get the start and end frames from the timeline
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)

    # Set the renderable frame range in the Render Settings
    cmds.setAttr("defaultRenderGlobals.startFrame", start_frame)
    cmds.setAttr("defaultRenderGlobals.endFrame", end_frame)

    print("Renderable frame range set to timeline: {}-{}".format(start_frame, end_frame))

def ExportBatchesAnim():
    ExportStartFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
    ExportEndFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
    cmdAlembicBase = 'AbcExport -j "' 
    cmdAlembicBase = cmdAlembicBase + '-frameRange '+str(ExportStartFrame)+' '+str(ExportEndFrame)
    cmdAlembicBase = cmdAlembicBase + ' -uvWrite -attrPrefix xgen -worldSpace'
    palette = cmds.ls( exactType="xgmPalette" )
    for p in range( len(palette) ):
        filename = strScenePath+ "/" + strSceneName + "__" + xgmExternalAPI.encodeNameSpace(str(palette[p])) + ".abc"
        descShapes = cmds.listRelatives( palette[p], type="xgmDescription", ad=True )
        cmdAlembic = cmdAlembicBase
        for d in range( len(descShapes) ):
            descriptions = cmds.listRelatives( descShapes[d], parent=True )
            if len(descriptions):
                patches = xg.descriptionPatches(descriptions[0])
                for patch in patches:
                    cmd = 'xgmPatchInfo -p "'+patch+'" -g';
                    geom = mel.eval(cmd)
                    geomFullName = cmds.ls( geom, l=True )
                    cmdAlembic += " -root " + geomFullName[0]
        
        cmdAlembic = cmdAlembic + ' -stripNamespaces -file \''+ filename+ '\'";';
        print(cmdAlembic)
        mel.eval(cmdAlembic)

def GetGuideCurveAbc(description):
    print(description)
    patchAbcFiles = os.listdir(abcFolderPath)
    print(abcFolderPath)
    description = description.split(":")[-1]
    for abcFile in patchAbcFiles:
        if description.lower() in abcFile.lower():
            abcFilePath = abcFolderPath + "/" + abcFile
            return str(os.path.normpath(abcFilePath))
    return ""

def GetRenderPatchAbc(palette):
    patchAbcFiles = os.listdir(strScenePath)
    pExplode = palette.split(":")
    pFirst = pExplode[0]
    for abcFile in patchAbcFiles:
        if not strSceneName in abcFile: continue
        explode = abcFile.split("__ns__")
        first = explode[0]
        if pFirst in first:
            abcFilePath = abcFolderPath + "/" + abcFile
            return str(os.path.normpath(abcFilePath))
    return ""

def ExportAbc(selection, start, end, save_name):
    # AbcExport -j "-frameRange 1 120 -dataFormat ogawa -root |locator1 -root |locator2 -file D:/After.Effect.Plugins/test.abc"
    root = ""
    for i in selection:
        root += " -root %s" % (i)

    command = "-frameRange " + str(start) + " " + str(end) +" -worldSpace -dataFormat ogawa" + root + " -file " + save_name
    cmds.AbcExport ( j = command )
    print(save_name)

def ExportGuideAbc():
    start_frame = cmds.playbackOptions(q=True, min=True)
    end_frame = cmds.playbackOptions(q=True, max=True)
    curves = cmds.ls("CHShiZhongTian_00:*_tempCurve", long=True)
    parts = ["BackLong", "Front", "FrontB"]
    curveDict = {}
    for curve in curves:
        currentPart = ""
        for part in parts:
            if part in curve:
                currentPart = part
                break
        # print(curve, currentPart)
        if currentPart == "": continue
        if part not in curveDict:
            curveDict[currentPart] = [curve]
        else:
            print(curveDict[currentPart])
            # if "BackLong_guideCurve_geo16" in curve: continue
            curveDict[currentPart].append(curve)
    print(abcFolderPath)
    for part, curves in curveDict.items():
        cmds.select(curves)
        filePath = abcFolderPath + "/" + part + ".abc"
        ExportAbc(curves, start_frame, end_frame, filePath)

def SetAttr():
    if xgg.Maya:
        #palette is collection, use palettes to get collections first.
        palettes = xg.palettes()
        for palette in palettes:
            #print "Collection:" + palette

            #Use descriptions to get description of each collection
            descriptions = xg.descriptions(palette)
            for description in descriptions:
                #print " Description:" + description
                objects = xg.objects(palette, description, True)

                #Get active objects,e.g. SplinePrimtives
                for object in objects:
                    #print " Object:" + object
                    attrs = xg.allAttrs(palette, description, object)
                    for attr in attrs:
                        print " Attribute:" + attr + ", Value:" + xg.getAttr(attr, palette, description, object)
                        # cacheFileName
                        if attr == "liveMode":
                            xg.setAttr(attr,xge.prepForAttribute("False"),palette, description, object)
                        elif attr == "cacheFileName":
                            charNamespace = palette.split(":")[0]
                            if charNamespace == "CH_00":
                                abcFile = GetGuideCurveAbc(description)
                                if abcFile != "":
                                    xg.setAttr(attr,xge.prepForAttribute(abcFile),palette, description, object)
                                else:
                                    xg.setAttr("useCache",xge.prepForAttribute("False"),palette, description, object)
                            else:
                                xg.setAttr("useCache",xge.prepForAttribute("False"),palette, description, object)
                        # elif attr == "custom__arnold_useAuxRenderPatch":
                        #     xg.setAttr(attr,xge.prepForAttribute("True"),palette, description, object)
                        #     #xg.setActive(palette, description, "custom__arnold_useAuxRenderPatch", xge.prepForAttribute(True))
                        # elif attr == "custom__arnold_auxRenderPatch":
                        #     abcFile = GetRenderPatchAbc(palette)
                        #     xg.setAttr(attr,xge.prepForAttribute(abcFile),palette, description, object)
                        elif attr == "renderer":
                           xg.setAttr(attr,xge.prepForAttribute("Arnold Renderer"),palette, description, object)
                        elif attr == "custom__arnold_rendermode":
                           xg.setAttr(attr,xge.prepForAttribute("1"),palette, description, object)

    # de = xgg.DescriptionEditor
    # de.refresh("Full")
    xg.registerCallback("RenderAPIRendererTabUIInit", "xgenArnoldUI.xgArnoldUI")
    xg.registerCallback("RenderAPIRendererTabUIRefresh", "xgenArnoldUI.xgArnoldRefresh")
    if xg.xgGlobal.DescriptionEditor is not None:
        xg.xgGlobal.DescriptionEditor.refresh("Full")

HideAll()
SetRenderFrame()
ExportGuideAbc()
ExportBatchesAnim()
SetAttr()
