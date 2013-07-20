# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# ################################################################
# Init
# ################################################################


bl_info = {
    "name": "three.js format for mixee labs",
    "author": "mrdoob, kikko, alteredq, remoe, pxf, n3tfr34k, neuralfirings",
    "version": (1, 4, 0),
    "blender": (2, 6, 6),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export three.js meshes for Mixee Labs",
    "warning": "",
    "wiki_url": "https://github.com/mrdoob/three.js/tree/master/utils/exporters/blender",
    "tracker_url": "https://github.com/mrdoob/three.js/issues",
    "category": "Import-Export"}

# To support reload properly, try to access a package var,
# if it's there, reload everything

import bpy

if "bpy" in locals():
    import imp
    if "export_mixeejs" in locals():
        imp.reload(export_mixeejs)

from bpy.props import *
from bpy_extras.io_utils import ExportHelper

# ################################################################
# Custom properties
# ################################################################

bpy.types.Object.THREE_castShadow = bpy.props.BoolProperty()
bpy.types.Object.THREE_receiveShadow = bpy.props.BoolProperty()
bpy.types.Object.THREE_doubleSided = bpy.props.BoolProperty()
bpy.types.Object.THREE_exportGeometry = bpy.props.BoolProperty(default = True)

bpy.types.Material.THREE_useVertexColors = bpy.props.BoolProperty()
bpy.types.Material.THREE_depthWrite = bpy.props.BoolProperty(default = True)
bpy.types.Material.THREE_depthTest = bpy.props.BoolProperty(default = True)

THREE_material_types = [("Basic", "Basic", "Basic"), ("Phong", "Phong", "Phong"), ("Lambert", "Lambert", "Lambert")]
bpy.types.Material.THREE_materialType = EnumProperty(name = "Material type", description = "Material type", items = THREE_material_types, default = "Lambert")

THREE_blending_types = [("NoBlending", "NoBlending", "NoBlending"), ("NormalBlending", "NormalBlending", "NormalBlending"),
                        ("AdditiveBlending", "AdditiveBlending", "AdditiveBlending"), ("SubtractiveBlending", "SubtractiveBlending", "SubtractiveBlending"),
                        ("MultiplyBlending", "MultiplyBlending", "MultiplyBlending"), ("AdditiveAlphaBlending", "AdditiveAlphaBlending", "AdditiveAlphaBlending")]
bpy.types.Material.THREE_blendingType = EnumProperty(name = "Blending type", description = "Blending type", items = THREE_blending_types, default = "NormalBlending")

class OBJECT_PT_hello( bpy.types.Panel ):

    bl_label = "THREE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.label(text="Selected object: " + obj.name )

        row = layout.row()
        row.prop( obj, "THREE_exportGeometry", text="Export geometry" )

        row = layout.row()
        row.prop( obj, "THREE_castShadow", text="Casts shadow" )

        row = layout.row()
        row.prop( obj, "THREE_receiveShadow", text="Receives shadow" )

        row = layout.row()
        row.prop( obj, "THREE_doubleSided", text="Double sided" )

class MATERIAL_PT_hello( bpy.types.Panel ):

    bl_label = "THREE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        mat = context.material

        row = layout.row()
        row.label(text="Selected material: " + mat.name )

        row = layout.row()
        row.prop( mat, "THREE_materialType", text="Material type" )

        row = layout.row()
        row.prop( mat, "THREE_blendingType", text="Blending type" )

        row = layout.row()
        row.prop( mat, "THREE_useVertexColors", text="Use vertex colors" )

        row = layout.row()
        row.prop( mat, "THREE_depthWrite", text="Enable depth writing" )

        row = layout.row()
        row.prop( mat, "THREE_depthTest", text="Enable depth testing" )


# ################################################################
# Exporter - settings
# ################################################################

SETTINGS_FILE_EXPORT = "threejs_settings_export.js"

import os
import json

def file_exists(filename):
    """Return true if file exists and accessible for reading.

    Should be safer than just testing for existence due to links and
    permissions magic on Unix filesystems.

    @rtype: boolean
    """

    try:
        f = open(filename, 'r')
        f.close()
        return True
    except IOError:
        return False

def get_settings_fullpath():
    return os.path.join(bpy.app.tempdir, SETTINGS_FILE_EXPORT)

def save_settings_export(properties):

    settings = {} #export_mixeejs.py will load default

    fname = get_settings_fullpath()
    f = open(fname, "w")
    json.dump(settings, f)

def restore_settings_export(properties):

    settings = {}

    fname = get_settings_fullpath()
    if file_exists(fname):
        f = open(fname, "r")
        settings = json.load(f)

# ################################################################
# Exporter
# ################################################################

class ExportMixeeTHREEJS(bpy.types.Operator, ExportHelper):
    '''Export selected object / scene for Three.js (ASCII JSON format).'''

    bl_idname = "export.mixeelabsthreejs"
    bl_label = "Export Three.js for Mixee Labs"

    filename_ext = ".json"

    def invoke(self, context, event):
        restore_settings_export(self.properties)
        return ExportHelper.invoke(self, context, event)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        print("Selected: " + context.active_object.name)

        if not self.properties.filepath:
            raise Exception("filename not set")

        save_settings_export(self.properties)

        filepath = self.filepath

        import io_mesh_mixeelabs.export_mixeejs
        return io_mesh_mixeelabs.export_mixeejs.save(self, context, **self.properties)

    def draw(self, context):
        layout = self.layout


# ################################################################
# Common
# ################################################################

def menu_func_export(self, context):
    default_path = bpy.data.filepath.replace(".blend", ".js")
    self.layout.operator(ExportMixeeTHREEJS.bl_idname, text="Three.js (.json) for Mixee Labs").filepath = default_path

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
