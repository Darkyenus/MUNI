# Hash Visualizer

Attempt to create visualizer of hashes for visual comparison.
Targets 128 bit hashes (for now) in 512x512 bitmap.
When used in real product, input hash should not be the raw hash or key,
but rather a more secure password-grade hash with salt,
to make it harder to search for collisions.

## Strategy
Split the bits into feature parts, that is, blocks that control one
specific feature of the result image. Most of the image is created
fairly predictably, but some (namely patterns) depend partly on the
bits assigned to them and partly on the hash of the whole seed.
This makes it easy to prove/test that small changes in the seed lead to
recognizably different image, while making it more difficult to automate
collision finding.

## Version 1: Hardcoded selection pools
- 4 quadrants (32 bits each) all having the following:
    - 8 bits of bg color
    - 8 bits of primary fg color
    - 8 bits of secondary fg color
    - 4 bits for primary pattern
    - 4 bits for secondary pattern
    