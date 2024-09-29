# MotionFrame

|Fade Blend|Motion Blend|
-----------|-------------
|![Smoke Fade](https://github.com/user-attachments/assets/579d1eea-abbd-48f6-8821-f535de6f2dab)|![Smoke Motion](https://github.com/user-attachments/assets/365c401e-5eee-4fdb-b2b9-776bb8b14c73)|
|![Explosion Fade](https://github.com/user-attachments/assets/1591cd44-1326-453d-b787-4e6373fb3457)|![Explosion Motion](https://github.com/user-attachments/assets/18a4fe4c-93c9-45e6-bc54-c231954f5b39)|

## Overview

**MotionFrame** is a Python-based application designed to analyze flipbook images and generate motion vector flipbook textures. These textures are particularly useful in visual effects (VFX) to enhance the inter-frame blending of flipbook animations. MotionFrame is compatible with both macOS and Windows operating systems and uses OpenCV to generate optical flow.

## Features

- **Language Support**: English and Japanese.
- **File Input**: Customizable directory, file prefix, extension, and sequence digits. Supports drag and drop for files and folders to auto-detect settings.
- **Atlas**: Configure pixel width, columns (X), rows (Y), and enable Stagger Pack.
- **Animation**: Frame skipping with optional analysis of skipped frames and a looping option.
- **Export**: Downsample motion vector, choose motion vector encoding format, and select resize algorithm.
- **Motion Vector Encoding**: Supports "R8G8 Remapped to 0-1" and "SideFX Labs R8G8 Encoding".
- **Visualization**: View color, motion vector, and other visual aspects of the generated textures.

## Usage

### File Input

1. **Directory**: Browse and select the directory containing the flipbook images.
2. **File Prefix**: Enter the common prefix of the flipbook image files.
3. **Extension**: Specify the file extension (e.g., `tga`).
4. **Sequence Digits**: Set the number of digits used in the file sequence numbering.
5. **Drag and Drop**: You can drag and drop a single file or an entire folder to automatically configure the file input settings.

### Atlas Configuration

1. **Pixel Width**: Set the width of the atlas in pixels.
2. **Columns (X)**: Define the number of columns in the atlas.
3. **Rows (Y)**: Define the number of rows in the atlas.
4. **Stagger Pack**: Enable or disable staggered packing of the atlas. When enabled, the RG channels store the even frames, and the BA channels store the odd frames.

### Animation Settings

1. **Frame Skip**: Set the number of frames to skip during analysis.
2. **Analyze Skipped Frames**: Enable or disable analysis of skipped frames.
3. **Loop**: Enable or disable looping of the animation.

### Export Options

1. **Downsample Motion Vector**: Enable or disable downsampling of the motion vector.
2. **Motion Vector Encoding**: Choose the encoding format for the motion vector: "R8G8 Remapped to 0-1" or "SideFX Labs R8G8 Encoding".
3. **Resize Algorithm**: Select the algorithm used for resizing (e.g., `Cubic`).

### Generating and Saving

- **Generate**: Click to generate the motion vector flipbook texture based on the provided settings.
- **Save**: Save the generated texture to the desired location.

