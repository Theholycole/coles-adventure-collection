# Cole’s Adventure Collection

A personal Foundry VTT module for a Pathfinder Second Edition campaign. It holds four importable adventures: Lantern House, Raincoil, Voyage to Morrowmaw, and Morrowmaw — Festival and the Three Crises.

> **Spoilers.** This module is GM material: prepared adventure text, secrets, and GM maps. If you play in this campaign, please don't download it.

Module ID: `lantern-house` · Foundry 14 · PF2e 8.5.1 or later

## Install

Manifest URL:

```
https://github.com/Theholycole/coles-adventure-collection/releases/latest/download/module.json
```

**Forge:** open the Bazaar, choose **Install From Manifest**, paste the URL, then click **Install module**.

**Foundry:** in the setup screen, go to **Add-on Modules → Install Module**, paste the URL into **Manifest URL**, then click **Install**.

Then enable **Cole’s Adventure Collection** in the world and import the adventure you want from **Compendium Packs**. Installing the module doesn't import anything into a world by itself.

### Replacing a copy uploaded by hand

A copy uploaded as a ZIP has no update link. Install once from the manifest URL above. If Forge says the module is already installed, uninstall the old copy first, then install from the URL. Adventures you already imported into a world stay in that world. Their scene images load from the module folder, so they come back once the module is reinstalled.

## Update

When a new version is released, open the Forge Bazaar, choose **Update All Packages**, select this module, and click **Update**. In Foundry, use **Update** on the module in **Add-on Modules**.

An update replaces the module's compendiums. It never changes documents you already imported into a world. Each version's notes say what to import again; usually that's only the new scenes or journals.

## Publish a new version

1. Build the new version folder as usual, for example `v1.4.2/lantern-house`, with a new `"version"` in its `module.json` and a new top section in `RELEASE-NOTES.md`.
2. Run:

   ```bash
   python3 release.py "/run/media/theholycole/Bigger Local Disk/PF2e Notes/Empyrean Bloom/Game Prep/Maps and Assets/Foundry Packages/Coles Adventure Collection/v1.4.2/lantern-house"
   ```

The script leaves the folder untouched. It adds the manifest and download links to a copy of `module.json`, zips the module with `module.json` at the ZIP root, commits the released `module.json` here, and creates the GitHub release with `module.json` and `module.zip` attached. It needs `gh` signed in as Theholycole. Add `--dry-run` to only build `.build/module.zip`.

## Licence

Personal campaign content; all rights reserved. Pathfinder Second Edition game statistics are used under the ORC License and the Open Game License. Both licences ship in the module's `licenses/` folder.
