from pathlib import Path
import importlib.util
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "maya_anim_format_registration_test"

spec = importlib.util.spec_from_file_location(
    PACKAGE_NAME,
    ROOT / "__init__.py",
    submodule_search_locations=[str(ROOT)],
)
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE_NAME] = addon
spec.loader.exec_module(addon)

addon.register()
try:
    assert hasattr(bpy.ops.maya_anim, "import")
    assert hasattr(bpy.ops.maya_anim, "export")
finally:
    addon.unregister()

print("Add-on registration test passed")
