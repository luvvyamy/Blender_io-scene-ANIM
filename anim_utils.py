import bpy, math
from bpy_extras import anim_utils as bpy_anim_utils
from mathutils import Matrix, Euler, Quaternion


def create_action_channelbag(obj: bpy.types.Object, action_name: str):
    """Create an Action assigned to *obj* and return its slot and channelbag."""
    anim_data = obj.animation_data_create()
    action = bpy.data.actions.new(action_name)
    slot = action.slots.new(obj.id_type, obj.name)
    channelbag = bpy_anim_utils.action_ensure_channelbag_for_slot(action, slot)
    anim_data.action = action
    anim_data.action_slot = slot
    return action, slot, channelbag


def get_assigned_action_channelbag(obj: bpy.types.Object):
    """Return the Action, assigned slot, and channelbag for *obj*."""
    anim_data = obj.animation_data
    if anim_data is None or anim_data.action is None or anim_data.action_slot is None:
        return None

    channelbag = bpy_anim_utils.animdata_get_channelbag_for_assigned_slot(anim_data)
    if channelbag is None:
        return None

    return anim_data.action, anim_data.action_slot, channelbag


def get_copied_action_channelbag(action: bpy.types.Action, slot: bpy.types.ActionSlot):
    """Copy *action* and return the copy with the slot corresponding to *slot*."""
    action_copy = action.copy()
    slot_copy = action_copy.slots.get(slot.identifier)
    if slot_copy is None:
        bpy.data.actions.remove(action_copy)
        raise RuntimeError("Copied Action is missing the assigned Action slot")

    channelbag = bpy_anim_utils.action_get_channelbag_for_slot(action_copy, slot_copy)
    if channelbag is None:
        bpy.data.actions.remove(action_copy)
        raise RuntimeError("Copied Action slot is missing its channelbag")

    return action_copy, slot_copy, channelbag

UNITS = {
    "METERS": 1.0,  # Ref unit!
    "KILOMETERS": 0.001,
    'MILLIMETERS': 1000.0,
    'CENTIMETERS': 100.0,
    "FEET": 1.0 / 0.3048,
    "INCHES": 1.0 / 0.0254,
    "turn": 1.0,  # Ref unit!
    "DEGREES": 360.0,
    "RADIANS": math.pi * 2.0,
    "SECONDS": 1.0,  # Ref unit!
}

ASCII_X = 88

ANIM_TIME_UNITS = {
    # in fps
    15: "game",
    24: "film",
    25: "pal",
    30: "ntsc",
    48: "show",
    50: "palf",
    60: "ntscf"
}

B3D_TIME_UNITS = {v: k for k, v in ANIM_TIME_UNITS.items()}

ANIM_LINEAR_UNITS = {
    'MILLIMETERS': "mm",
    'CENTIMETERS': "cm",
    'METERS': "m",
    'KILOMETERS': "km",
    'INCHES': "in",
    'FEET': "ft",
    'MILES': "mi",
}

B3D_LINEAR_UNITS = {v: k for k, v in ANIM_LINEAR_UNITS.items()}

ANIM_ANGULAR_UNITS = {
    'DEGREES': "deg",
    'RADIANS': "rad"
}

B3D_ANGULAR_UNITS = {v: k for k, v in ANIM_ANGULAR_UNITS.items()}

ANIM_CYCLES_TYPE = {
    'REPEAT': 'cycle',
    'REPEAT_OFFSET': 'cycleRelative',
    'MIRROR': 'oscillate',
    'NONE': None,
}

B3D_CYCLES_TYPE = {
    'cycle': 'REPEAT',
    'cycleRelative': 'REPEAT_OFFSET',
    'oscillate': 'MIRROR',
    'linear': 'NONE',
    'constant': 'NONE'
}

ANIM_UNIT_TYPE = { # blender defaults:
    'TIME': 'time', # frame
    'LENGTH': 'linear', # meter
    'ROTATION': 'angular', # radians
    'NONE': 'unitless'
}

B3D_UNIT_TYPE = {v: k for k, v in ANIM_UNIT_TYPE.items()}

ANIM_TANGENT_TYPE = {
    'AUTO_CLAMPED': 'auto',
    'AUTO': 'spline',
    'VECTOR': 'linear',
    'ALIGNED': 'fixed',
    'FREE': 'fixed',

    # interpolation
    'BEZIER': 'spline',
    'LINEAR': 'linear', # doesn't write tangents
    'CONSTANT': 'step' # doesn't write tangents, only out tangent
}

B3D_TANGENT_TYPE = {
    'clamped': 'AUTO_CLAMPED',
    'auto': 'AUTO_CLAMPED',
    'spline': 'AUTO',
    'linear': 'VECTOR',
    'fixed': 'FREE', # 'ALIGNED' is also an option but this should offer more flexibility
    'step': 'VECTOR'
}

B3D_INTERP_TYPE = {
    'spline': 'BEZIER',
    'linear': 'LINEAR', # no tangents
    'step': 'CONSTANT' # only right-handle tangent
}

ANIM_ATTR_NAMES = {
    "location": 'translate',
    "rotation_euler": 'rotate',
    "rotation_quaternion": 'rotate',
    "scale": 'scale'
}

B3D_ATTR_NAMES = {
    "translate": 'location',
    "rotate": 'rotation_euler',
    "scale": 'scale'
}

FCURVE_PATHS_NAME_TO_ID = {
    "location": 0,
    "rotation_euler": 1,
    "rotation_quaternion": 2,
    "scale": 3,
    "custom": 4
}

FCURVE_PATHS_ID_TO_NAME = {v: k for k, v in FCURVE_PATHS_NAME_TO_ID.items()}

# Return a convertor between specified units.
def units_convertor(u_from, u_to):
    conv = UNITS[u_to] / UNITS[u_from]
    return lambda v: v * conv

linear_converter = units_convertor('METERS', bpy.context.scene.unit_settings.length_unit) 
angular_converter = units_convertor('RADIANS', bpy.context.scene.unit_settings.system_rotation)

def anim_unit_converter(animData_output: str, linearUnit: str, angularUnit: str):
    linearUnit = B3D_LINEAR_UNITS[linearUnit]
    angularUnit = B3D_ANGULAR_UNITS[angularUnit]

    fc_unit = B3D_UNIT_TYPE[animData_output]
    unit_convert = {'LENGTH': units_convertor(linearUnit, 'METERS'),
                    'ROTATION': units_convertor(angularUnit, 'RADIANS')}
    
    return fc_unit, unit_convert

def dupe_obj(ctx: bpy.context, obj: bpy.types.Object):
    obj = obj.copy()
    arm = obj.data.copy()
    obj.data = arm

    ctx.scene.collection.objects.link(obj)
    obj.make_local()
    obj.data.make_local()

    return obj

def lerp(a:float, b:float, time:float):
    '''Linearly interpolates between A and B, using Time in range [0.0 - 1.0]'''
    return a+(b-a)*time

def offset_rotation(keys_array, fc_path, node_rot):
    # get a rotation matrix of the animated values
    # TODO add option to retain original bone rotation
    if fc_path.endswith('quaternion'):
        key_rotValues = Quaternion(keys_array)
    else:
        key_Euler = Euler(keys_array, 'XYZ')
        key_rotValues = key_Euler.to_quaternion()

    rotMat = node_rot @ key_rotValues

    return rotMat

def bone_calculate_parentSpace(bone: bpy.types.Bone) -> Matrix:
    # Get bone's rest pose parent-space matrix and if bone has no parent, then get armature-space matrix
    if bone.parent:
        boneMat = Matrix(bone.parent.matrix_local.inverted() @ bone.matrix_local)
    else:
        boneMat = bone.matrix_local
     
    return boneMat

def convert_axes(obj: bpy.types.Object, global_matrix, global_scale, bake_space_transform, reverse=False):
    # Revert changes when done with the object
    if reverse:
        global_matrix = global_matrix.inverted()
        global_scale = 1/global_scale

    if bake_space_transform:
        dataMat = Matrix.Scale(global_scale, 4) @ global_matrix
    else: dataMat = Matrix.Scale(global_scale, 4)

    # transform armature or mesh by the new axis
    # this is basically "apply transforms"
    if hasattr (obj.data, 'transform'):
        obj.data.transform(dataMat)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')