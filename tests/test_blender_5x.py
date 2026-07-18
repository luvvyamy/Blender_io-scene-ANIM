from pathlib import Path
import importlib.util
import sys
import tempfile

import bpy
from mathutils import Matrix


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "maya_anim_format"


def load_addon():
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return module


class Operator:
    def report(self, _level, _message):
        pass


def assert_curve(channelbag, data_path, index, expected_keys):
    curve = channelbag.fcurves.find(data_path=data_path, index=index)
    assert curve is not None, f"Missing {data_path}[{index}]"
    actual_keys = [(round(key.co[0], 6), round(key.co[1], 6)) for key in curve.keyframe_points]
    assert actual_keys == expected_keys, f"Unexpected keys for {data_path}[{index}]: {actual_keys}"


def main():
    addon = load_addon()
    importer = __import__(f"{PACKAGE_NAME}.import_anim", fromlist=["import_anim"])
    exporter = __import__(f"{PACKAGE_NAME}.export_anim", fromlist=["export_anim"])
    utils = __import__(f"{PACKAGE_NAME}.anim_utils", fromlist=["anim_utils"])
    context = bpy.context

    bpy.ops.mesh.primitive_cube_add()
    cube = context.active_object
    cube.name = "Cube"

    fixture = ROOT / "tests" / "fixtures" / "object_location.anim"
    nodes, settings = importer.read_animation(Operator(), context, cube, str(fixture), use_fps=False, use_units=False, use_timerange=False)
    importer.write_animation(
        Operator(), context, cube, "object_location", nodes, settings,
        apply_unit_linear=True,
        axis_transform=False,
        bake_space_transform=False,
        use_custom_props=True,
        use_selected_bones=False,
        anim_offset=0,
        global_matrix=Matrix.Identity(4),
        global_scale=1,
    )

    assigned = utils.get_assigned_action_channelbag(cube)
    assert assigned is not None, "Import did not assign an Action slot/channelbag"
    action, slot, channelbag = assigned
    assert action.name == "object_location"
    assert slot.target_id_type == "OBJECT"
    assert_curve(channelbag, "location", 0, [(1.0, 0.01), (3.0, 0.03)])

    bpy.ops.mesh.primitive_cube_add(location=(3, 0, 0))
    other = context.active_object
    other.name = "Other"
    other_slot = action.slots.new(other.id_type, other.name)
    other_channelbag = __import__("bpy_extras.anim_utils", fromlist=["action_ensure_channelbag_for_slot"]).action_ensure_channelbag_for_slot(action, other_slot)
    other_curve = other_channelbag.fcurves.new("location", index=1)
    other_curve.keyframe_points.insert(1, 99)
    other.select_set(False)
    cube.select_set(True)
    context.view_layer.objects.active = cube

    source_key_count = len(channelbag.fcurves.find("location", index=0).keyframe_points)
    text = exporter.anim_fcurve_elements(
        Operator(), context, (cube,), "NONE", False, Matrix.Identity(4), False,
        bake_axis=False,
        global_scale=1,
        only_deform_bones=False,
        use_time_range=False,
        start_time=1,
        end_time=3,
        angularUnit="deg",
    ).read()
    assert "Cube" in text
    assert "Other" not in text, "Export traversed an unassigned Action slot"
    assert "99.000000" not in text
    assert len(channelbag.fcurves.find("location", index=0).keyframe_points) == source_key_count

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "roundtrip.anim"
        result = exporter.save(
            Operator(), context,
            filepath=str(output),
            use_selection=True,
            use_visible=False,
            use_active_collection=False,
            sanitize_names="NONE",
            sanitize_spacesOnly=False,
            global_matrix=Matrix.Identity(4),
            bake_space_transform=False,
            bake_axis=False,
            global_scale=1,
            only_deform_bones=False,
            use_time_range=False,
            start_time=1,
            end_time=3,
        )
        assert result == {'FINISHED'}
        assert "Cube" in output.read_text(encoding="ascii")

        object_count = len(bpy.data.objects)
        baked_output = Path(directory) / "baked.anim"
        result = exporter.save(
            Operator(), context,
            filepath=str(baked_output),
            use_selection=True,
            use_visible=False,
            use_active_collection=False,
            sanitize_names="NONE",
            sanitize_spacesOnly=False,
            global_matrix=Matrix.Identity(4),
            bake_space_transform=False,
            bake_axis=True,
            global_scale=1,
            only_deform_bones=False,
            use_time_range=False,
            start_time=1,
            end_time=3,
        )
        assert result == {'FINISHED'}
        assert len(bpy.data.objects) == object_count
        assert context.view_layer.objects.active == cube
        assert cube.select_get()

    print("Blender 5 Action-slot import/export tests passed")


if __name__ == "__main__":
    main()
