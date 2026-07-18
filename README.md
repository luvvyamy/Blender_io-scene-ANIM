# ✨ Maya ANIM Format for Blender 5.2, bestie ✨

Maya's `.anim` import/export extension for Blender, now serving Blender 5.2 energy 💅👑

This extension imports and exports Autodesk Maya animation files, because apparently animation data needed yet another groupchat and we were NOT going to let it win 😩🍵

Source format documentation: [ANIM file format | Maya 2020](https://help.autodesk.com/view/MAYAUL/2020/ENU/?guid=GUID-87541258-2463-497A-A3D7-3DEA4C852644)

## ⚠️ warning, the tea is IMPORTANT ⚠️

This is a **quick port made with Codex**, bestie, and it is **untested on an actual Blender 5.2 installation** 🚨💀

The port was locally validated with **Blender 5.1.2** only, so Blender 5.2 is the intended target but NOT a verified runtime in this repository. Please save your `.blend` file before importing or exporting, because we are not pretending this rushed little diva has had a full production shakedown 💅🙏🏼

## installation, because the extension is being dramatic ✨

1. Download or build the release ZIP containing `blender_manifest.toml`.
2. In Blender, open **Edit → Preferences → Get Extensions**.
3. Open the dropdown menu and choose **Install from Disk…**.
4. Select the ZIP and enable **Maya ANIM Format**, periodt 👑

To build the extension ZIP from this repository:

```sh
blender --factory-startup --command extension build --source-dir . --output-dir /tmp
```

## usage, let the animation enter the chat 💬

Import:

```text
File → Import → Maya Animation (.anim)
```

Export:

```text
File → Export → Maya Animation (.anim)
```

The extension supports animation on objects and armature bones. In Blender 5, Actions can contain animation for multiple targets, so export uses the Action slot assigned to each object and does not intentionally mix another object's curves into the file. Look at Blender's assigned Action slot before exporting, bestie, because the slot is literally the chat where the animation lives 😩🍵

## features, serving actual functionality ✨

- Import and export raw animation curves as presented by Blender when **Transform** is disabled.
- Convert animation axes and bone parent-space transforms when **Transform** is enabled.
- Control bone scale for imported and exported animations when the top hierarchy node uses a different scale.
- Bake world-transform data into exported and imported object and bone animation.
- Use presets, because clicking the same settings repeatedly is NOT character development 💅
- Import multiple files.
- Offset imported animation on the timeline.
- Match the Blender scene's framerate, units, and time range to the animation.
- Limit import to selected bones.
- Limit export to a chosen frame range instead of exporting every keyframe from the timeline.
- Export only deform bones when requested.
- Convert exported curve names to avoid spaces, or to avoid spaces and special characters.

## rotation limitations, because somebody had to bring the plot twist 😭

- Imported rotations are converted to the target object's or bone's current rotation mode.
- **Axis Angle** rotation mode is not supported for import.
- Exported rotations are converted to **XYZ Euler** order.
- Quaternion rotation curves can therefore experience gimbal lock during export.
- Other software may also produce gimbal lock if the animation was exported with different axes.

## the moral of the story, gurl 💅

Use this for getting game-modding animation data into Blender 5.x, but keep the warning in the groupchat: this was a fast Codex port, Blender 5.2 itself was not tested, and Blender 5.1.2 is the only local validation target. Save backups, test on a copy, and report anything that starts acting possessed 👻✨
