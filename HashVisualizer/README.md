# Hash Visualizer

Attempt to create visualizer of hashes for visual comparison.
Targets 128 bit hashes (for now) in 512x512 bitmap.
When used in real product, input hash should now be the raw hash of
whatever, but rather a more secure password-grade hash with salt,
to make it harder to search for visual collisions.

## Strategy
Split the bits into feature parts, that is, blocks that control one
specific feature of the result image.

## Version 1: Hardcoded selection pools
- 4 quadrants (32 bits each) all having the following:
    - 8 bits of bg color
    - 8 bits of primary fg color
    - 8 bits of secondary fg color
    - 4 bits for primary pattern
    - 4 bits for secondary pattern
    