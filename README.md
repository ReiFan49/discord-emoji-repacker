# Emoji Repacker

Bot that is made from bitter experience of a short-lived feature.

This is a proof-of-concept for people that **does not value** original experience and
just respond with "Just create it back".

Original experience of such server cannot be retrieved back unless original invite link is restored.

## Data Format

> A slightly modified data format from `/inventory` endpoint. Inventory endpoint lists all servers you
registered packs for. Discord Packs are deprecated soon, so better grab it fast!

Emoji Pack data format is a zip file consisting of certain directory format.

- `metadata.json`, server basic metadata
- `emotes.json`, list of server emotes
- `icon.png`, server icon
- `e/<EMOJI_ID>.<EXT>`, list of emoji files based on their ID and extension.

## Command

|Command|Explanation|
|:-:|:-:|
| **`/recreate`** | receives an optional Server Name and mandatory Server Data Format as explained above. |

## What does it do?

- Cleanup any created servers that ended up in a deadlock upon start.
- Relive emoji experience by creating similar server with emoji sets, as used along with packs.
  Not for sticker migration.
- Perform background job for rate-limited concerns on adding emojis in a batch.

## Potentials Consideration

> I only plan what I need quick. So, development on this logic is another priority.

- Allow continuation of previous interrupted job due to errors or restarting bot.
- Change criteria of marking a server as deadlocked.

> Continuation is possible, but it means need to revamp the import logic.
  Once that happens deadlock criteria can be changed.
