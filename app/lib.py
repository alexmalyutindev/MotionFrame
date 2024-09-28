from enum import Enum
import os
import cv2
import numpy as np
import math
import imageio.v3 as imageio


class MotionVectorEncoding(Enum):
    R8G8_REMAP_0_1 = 0
    SIDEFX_LABS_R8G8 = 1
    R16G16 = 2


class EncodeResult:
    def __init__(self, color_atlas, motion_atlas, flow_directions, strength, total_frames):
        self.color_atlas = color_atlas
        self.motion_atlas = motion_atlas
        self.flow_directions = flow_directions
        self.strength = strength
        self.total_frames = total_frames


def calculate_required_frames(frames, frame_skip):
    return (frames // (frame_skip + 1)) + min(frames % (frame_skip + 1), 1)


def decode_atlas(atlas, atlas_width, atlas_height):
    # Error check for divisibility
    if atlas.shape[0] % atlas_height != 0 or atlas.shape[1] % atlas_width != 0:
        return None

    height = atlas.shape[0] // atlas_height
    width = atlas.shape[1] // atlas_width
    frames = []

    for y in range(atlas_height):
        for x in range(atlas_width):
            frame = atlas[y * height:(y + 1) * height, x * width:(x + 1) * width]
            frames.append(frame)

    return frames


def _resize_steps(height, width, new_width, callback):
    if width < new_width:
        callback(height * new_width // width, new_width)
    else:
        while width > new_width:
            # Make sure that Nyquist limit is not violated
            half_width = math.ceil(float(width) / 2.0)
            half_height = math.ceil(float(height) / 2.0)
            if half_width <= new_width:
                height = math.ceil(height * (float(new_width) / float(width)))
                width = new_width
            else:
                height = half_height
                width = half_width
            callback(height, width)


def _resize(src, new_width, interpolation_method):
    def resize_callback(height, width):
        nonlocal src
        src = cv2.resize(src, (width, height), interpolation=interpolation_method)

    _resize_steps(src.shape[0], src.shape[1], new_width, resize_callback)

    return src


def _predict_resize_height(height, width, new_width):
    def resize_callback(res_height, res_width):
        nonlocal height
        height = res_height

    _resize_steps(height, width, new_width, resize_callback)

    return height


def motion_atlas_stagger_pack(atlas, tiles_x, tiles_y):
    # Calculate the number of tiles in the atlas
    atlas_height, atlas_width, _ = atlas.shape
    tile_width = atlas_width // tiles_x
    tile_height = atlas_height // tiles_y
    num_tiles = tiles_x * tiles_y

    # Split the atlas into individual tile images
    tiles = [atlas[i*tile_height:(i+1)*tile_height, j*tile_width:(j+1)*tile_width]
             for i in range(tiles_y) for j in range(tiles_x)]

    # Calculate the required atlas height.
    new_atlas_height = math.ceil(math.ceil(num_tiles / 2) / tiles_x) * tile_height

    # Create a new 4 channel image with half the height of the atlas
    new_image = np.zeros((new_atlas_height, atlas_width, 4), dtype=np.uint8)

    # Assign the even-indexed tiles to the R and G channels, and the odd-indexed tiles to the B and A channels
    for i in range(num_tiles):
        tile_i = i // 2
        tile_y = (tile_i // tiles_x) * tile_height
        tile_x = (tile_i % tiles_x) * tile_width
        if i % 2 == 0:
            new_image[tile_y:tile_y+tile_height, tile_x:tile_x+tile_width, 2] = tiles[i][:, :, 0]  # R
            new_image[tile_y:tile_y+tile_height, tile_x:tile_x+tile_width, 1] = tiles[i][:, :, 1]  # G
        else:
            new_image[tile_y:tile_y+tile_height, tile_x:tile_x+tile_width, 0] = tiles[i][:, :, 0]  # B
            new_image[tile_y:tile_y+tile_height, tile_x:tile_x+tile_width, 3] = tiles[i][:, :, 1]  # A

    return new_image


def motion_atlas_flat_pack(image):
    # Split the image into top and bottom halves
    height = image.shape[0]
    width = image.shape[1]

    # Create a new 3 channel image
    new_image = np.zeros((height, width, 3), dtype=np.uint8)
    new_image[:, :, 0] = 0  # B
    new_image[:, :, 1] = image[:, :, 1]  # G
    new_image[:, :, 2] = image[:, :, 0]  # R

    return new_image


def encode_atlas(frames, atlas_width, atlas_height, atlas_pixel_width, extrude, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames, halve_motion_vector, resize_algorithm, enable_stagger_pack):
    # Assert that the atlas pixel width is divisible by the atlas width
    assert atlas_pixel_width % atlas_width == 0

    # Compute atlas frame dimention
    frame_width = atlas_pixel_width // atlas_width
    # Cap the extrusion to not consume the whole width
    extrude = min(extrude, (frame_width - 1) // 2)
    # Calculate the actual frame width before extrusion
    valid_frame_width = frame_width - (extrude * 2)
    # Make sure that the frame height matches the result of the resize operation
    valid_frame_height = _predict_resize_height(frames[0].shape[0], frames[0].shape[1], valid_frame_width)
    # Finally add the extrusion to the frame height
    frame_height = valid_frame_height + (extrude * 2)

    color_atlas, total_frames = _create_color_atlas(
        frames, atlas_width, atlas_height, frame_width, frame_height, extrude, frame_skip, resize_algorithm)

    motion_vector_width = atlas_pixel_width
    if halve_motion_vector:
        motion_vector_width //= 2
    motion_atlas, flow_directions, max_strength = _create_motion_atlas(
        frames, atlas_width, atlas_height, frame_width, frame_height, extrude, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames, motion_vector_width, resize_algorithm)

    if enable_stagger_pack:
        motion_atlas = motion_atlas_stagger_pack(motion_atlas, atlas_width, atlas_height)
    else:
        motion_atlas = motion_atlas_flat_pack(motion_atlas)

    return EncodeResult(color_atlas, motion_atlas, flow_directions, max_strength, total_frames)


def load_frames(frame_paths):
    frames = []
    idx = 1

    for file_path in frame_paths:
        idx += 1
        if not os.path.exists(file_path):
            break

        frame = imageio.imread(file_path)
        if frame is None:
            print(f'Image could not be loaded: {file_path}')
            continue

        channels = channel_count(frame)
        if channels >= 3:
            # RGB to BGR conversion
            frame[..., [0, 2]] = frame[..., [2, 0]]

        frames.append(frame)

    return frames


def channel_count(frame):
    return frame.shape[2] if len(frame.shape) > 2 else 1


def _create_color_atlas(frames, atlas_width, atlas_height, frame_width, frame_height, extrude, frame_skip, resize_algorithm):
    channels = channel_count(frames[0])

    if channels > 1:
        color_atlas = np.zeros([atlas_height * frame_height, atlas_width * frame_width, channels], dtype=np.uint8)
    else:
        color_atlas = np.zeros([atlas_height * frame_height, atlas_width * frame_width], dtype=np.uint8)

    _blit_extrude_image(frames[0], color_atlas, (0, 0), frame_width, resize_algorithm, extrude)
    atlas_idx = 1
    for i in range(frame_skip + 1, len(frames), frame_skip + 1):
        _blit_extrude_image(frames[i], color_atlas, ((
            (atlas_idx % atlas_width) * frame_width), (atlas_idx // atlas_width) * frame_height), frame_width, resize_algorithm, extrude)
        atlas_idx += 1

    return color_atlas, atlas_idx


def _prepare_optical_flow_frame(frame):
    channels = channel_count(frame)

    # Premultiply alpha
    if channels == 4:
        multiplied_frame = np.zeros_like(frame)
        alpha = frame[:, :, 3] / 255.0
        multiplied_frame[:, :, :3] = (frame[:, :, :3] * alpha[:, :, np.newaxis]).astype(np.uint8)
        multiplied_frame[:, :, 3] = 255
        frame = multiplied_frame

    # To grayscale if needed
    if channels >= 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame

    return gray


def _encode_motion_vector_sidefx_labs(flow, max_strength):
    # Calculate the magnitude and angle of the flow vectors
    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    # Clear tiny vector
    magnitude[magnitude < 1e-8] = 0
    # Normalize the magnitude to [0, 1]
    normalized_magnitude = magnitude / max_strength

    # Convert from vector to angle
    angle = np.arctan2(flow[..., 1], flow[..., 0])  # range [-pi, pi]
    # Map the angles to the range [0, 2*pi]
    normalized_angle = np.mod(angle, 2 * np.pi)
    normalized_angle[normalized_angle < 0] += 2 * np.pi
    # Normalize to the range [0, 1]
    normalized_angle = normalized_angle / (2 * np.pi)
    # Clear angle if vector magnitude is zero
    normalized_angle[magnitude == 0] = 0

    # Map normalized_angle to [0, 511]
    encoded_polar = (normalized_angle * 511.0).astype(np.int32)
    # Determine polar flip bit and the actual angle encoding
    polar_flip_bit = (encoded_polar // 256).astype(np.int32)
    encoded_angle = (encoded_polar % 256).astype(np.int32)

    # Map normalized magnitude to [0, 127]
    encoded_magnitude = (normalized_magnitude * 127.0).astype(np.int32)

    # Combine polar flip bit and magnitude bits into the green channel using bitwise operations
    encoded_g = (encoded_magnitude | (polar_flip_bit << 7)).astype(np.int32)

    return encoded_angle, encoded_g


def _encode_motion_vector(method, flow, max_strength):
    flow[..., 1] = -flow[..., 1]
    match method:
        case MotionVectorEncoding.R8G8_REMAP_0_1:
            r = (flow[..., 0] / (2 * max_strength) + 0.5) * 255
            g = (flow[..., 1] / (2 * max_strength) + 0.5) * 255
        case MotionVectorEncoding.SIDEFX_LABS_R8G8:
            r, g = _encode_motion_vector_sidefx_labs(flow, max_strength)

    return r, g


def _create_motion_atlas(frames, atlas_width, atlas_height, frame_width, frame_height, extrude, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames, motion_vector_width, resize_algorithm):
    height, width = frames[0].shape[:2]

    # Image for motion vector directions
    flow_directions = np.zeros([atlas_height * height, atlas_width * width, 3], dtype=np.uint8)

    max_strength = 0
    frame_idx = 1
    atlas_idx = 0

    flow_frames = []
    last_valid_frame_batch = []
    loop_frame_batch = []

    while frame_idx < len(frames):
        frame_batch = []
        # The final frame in the last frame batch will be the starting point for this batch, so go back by one
        frame_idx -= 1

        # Prepare frames for optical flow computation.
        # This includes skipped frames.
        for _ in range(frame_skip + 2):
            if frame_idx >= len(frames):
                break

            current_frame = frames[frame_idx]
            prepared_frame = _prepare_optical_flow_frame(current_frame)
            frame_batch.append(prepared_frame)

            frame_idx += 1

        # Couldn't load enough frames for consistent frame skips
        if len(frame_batch) != (frame_skip + 2):
            # Use the unused batch for the loop mode
            loop_frame_batch = frame_batch
            break

        # Compute displacement
        flow = _accumulate_displacement(frame_batch, analyze_skipped_frames)
        # Normalize the flow vectors based on image dimensions
        flow = _normalize_displacement(flow)

        # Update maximum motion strength
        max_strength = _update_max_strength(flow, motion_vector_encoding, max_strength)

        # Draw optical flow directions visualization
        direction_image = _draw_optical_flow(flow, frame_batch[0], frame_batch[-1])
        _blit_image(direction_image, flow_directions,
                    (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
        atlas_idx += 1

        flow_frames.append(flow)
        last_valid_frame_batch = frame_batch

    # In a case where there are no frames to process for the loop, the last frame in the last valid frame batch is used.
    if len(loop_frame_batch) == 0:
        loop_frame_batch.append(last_valid_frame_batch[-1])

    # Generate final motion vector frame. The number of frames in flow_frames are one less than the color atlas frames now.
    # This is because motion vector represents the motion between each color atlas frames, which means there is one less motion vector.
    if is_loop:
        # This is for loop mode. In this case, the last motion vector is a motion vector from the last frame to the first frame.
        # The displacement is computed from the last frame to the first frame, with the remaining unprocessed frames in the middle if skipped frame analysis is enabled.
        frame_batch = loop_frame_batch + [_prepare_optical_flow_frame(frames[0])]

        # Compute displacement
        flow = _accumulate_displacement(frame_batch, analyze_skipped_frames)
        # Normalize the flow vectors based on image dimensions
        flow = _normalize_displacement(flow)

        # Update maximum motion strength
        max_strength = _update_max_strength(flow, motion_vector_encoding, max_strength)
    else:
        # This is for non-loop mode. The last frame batch is not complete, so we need to extrapolate the motion vector for the last frame.
        # This is done by computing the motion vector in reverse order, and flipping the direction.
        # This is not the most accurate way to compute the motion vector, but it is a simple way to make up the missing motion vector.
        frame_batch = last_valid_frame_batch
        frame_batch.reverse()

        # Compute displacement
        flow = _accumulate_displacement(frame_batch, analyze_skipped_frames)
        # Normalize the flow vectors based on image dimensions
        flow = _normalize_displacement(flow)
        # Flip the displacement direction
        flow = -flow

        # Update maximum motion strength
        max_strength = _update_max_strength(flow, motion_vector_encoding, max_strength)

    # Draw optical flow directions visualization
    direction_image = _draw_optical_flow(flow, frame_batch[0], frame_batch[-1])
    _blit_image(direction_image, flow_directions,
                (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
    atlas_idx += 1

    flow_frames.append(flow)

    motion_atlas = np.zeros([atlas_height * frame_height, atlas_width * frame_width, 2], dtype=np.float32)
    for atlas_idx, flow in enumerate(flow_frames):
        flow = _resize(flow, frame_width, resize_algorithm)
        _blit_extrude_image(flow, motion_atlas, (((atlas_idx % atlas_width) * frame_width),
                            (atlas_idx // atlas_width) * frame_height), frame_width, resize_algorithm, extrude)

    # Encode motion to a texture
    r, g = _encode_motion_vector(motion_vector_encoding, motion_atlas, max_strength)
    motion_atlas = np.zeros([motion_atlas.shape[0], motion_atlas.shape[1], 2], dtype=np.uint8)
    motion_atlas[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    motion_atlas[..., 1] = np.clip(g, 0, 255).astype(np.uint8)

    return motion_atlas, flow_directions, max_strength


def _draw_optical_flow(flow, image, to_image, scale=1, step=16):
    h, w = image.shape[:2]
    y, x = np.mgrid[step//2:h:step, step//2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T

    fx = fx * w
    fy = fy * h

    # Create an empty image with 3 channels
    height, width = image.shape[:2]
    vis = np.zeros((height, width, 3), dtype=np.uint8)
    vis[:, :, 2] = image  # Red channel
    vis[:, :, 1] = to_image  # Green channel

    for (x1, y1, u, v) in zip(x, y, fx, fy):
        cv2.arrowedLine(vis, (x1, y1), (int(x1 + u * scale), int(y1 + v * scale)), (255, 0, 255), 1, tipLength=0.2)

    return vis


def _blit_image(source, target, target_coords):
    channels = channel_count(source)
    x, y = target_coords
    source_height, source_width = source.shape[:2]
    if channels > 1:
        target[y:y+source_height, x:x+source_width, :] = source
    else:
        target[y:y+source_height, x:x+source_width] = source


def _blit_extrude_image(source, target, target_coords, frame_width, resize_algorithm, extrude):
    # Resize to frame width
    source = _resize(source, frame_width - (extrude * 2), resize_algorithm)
    _blit_image(source, target, (target_coords[0] + extrude, target_coords[1] + extrude))
    # Extrude the inner image blit above to the surrounding pixel, with padding size of extrude variable.
    # This is done by copying the border pixel of the inner image to the surrounding pixels.
    if extrude > 0:
        target_x, target_y = target_coords
        source_height, source_width = source.shape[:2]

        # Top
        target[target_y:target_y+extrude,
               target_x+extrude:target_x+source_width+extrude] = source[0, :]
        # Bottom
        target[target_y+source_height+extrude:target_y+source_height + (extrude*2),
               target_x+extrude:target_x+source_width+extrude] = source[-1, :]
        # Left
        target[target_y+extrude:target_y+source_height + extrude,
               target_x:target_x+extrude] = source[:, 0][:, np.newaxis]
        # Right
        target[target_y+extrude:target_y+source_height + extrude,
               target_x+source_width+extrude:target_x+source_width+(extrude*2)] = source[:, -1][:, np.newaxis]
        # Corners
        target[target_y:target_y+extrude,
               target_x:target_x+extrude] = source[0, 0]
        target[target_y:target_y+extrude,
               target_x+source_width+extrude:target_x+source_width+extrude*2] = source[0, -1]
        target[target_y+source_height+extrude:target_y+source_height + extrude*2,
               target_x:target_x+extrude] = source[-1, 0]
        target[target_y+source_height+extrude:target_y+source_height+extrude*2,
               target_x + source_width+extrude:target_x+source_width+extrude*2] = source[-1, -1]


def _accumulate_displacement(frames, analyze_skipped_frames):
    if len(frames) < 2:
        return None

    if not analyze_skipped_frames:
        frames = [frames[0], frames[-1]]

    h, w = frames[0].shape[:2]
    accumulated_displacement = np.zeros((h, w, 2), np.float32)
    for i in range(1, len(frames)):
        prev_frame = frames[i-1]
        next_frame = frames[i]
        flow = cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None, 0.5, 8, 15, 5, 5, 1.5, 0)
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        current_x = (grid_x + accumulated_displacement[..., 0]).astype(np.float32)
        current_y = (grid_y + accumulated_displacement[..., 1]).astype(np.float32)
        displacement_x = cv2.remap(flow[..., 0], current_x, current_y, interpolation=cv2.INTER_LINEAR)
        displacement_y = cv2.remap(flow[..., 1], current_x, current_y, interpolation=cv2.INTER_LINEAR)
        accumulated_displacement[..., 0] += displacement_x
        accumulated_displacement[..., 1] += displacement_y
    return accumulated_displacement


def _normalize_displacement(flow):
    height, width = flow.shape[:2]
    normalized_flow = np.zeros_like(flow)
    normalized_flow[..., 0] = np.clip(flow[..., 0] / width, -1, 1)
    normalized_flow[..., 1] = np.clip(flow[..., 1] / height, -1, 1)
    return normalized_flow


def _update_max_strength(flow, motion_vector_encoding, max_strength):
    if motion_vector_encoding == MotionVectorEncoding.SIDEFX_LABS_R8G8:
        max_strength = max(max_strength, np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).max())
    else:
        max_strength = max(max_strength, np.abs(flow[..., 0]).max())
        max_strength = max(max_strength, np.abs(flow[..., 1]).max())
    return max_strength


def bgr_to_rgb(image):
    channels = channel_count(image)

    if channels < 3:
        return image

    image_copy = np.zeros_like(image)
    # BGR to RGB conversion
    if channels == 3:
        image_copy[..., [0, 1, 2]] = image[..., [2, 1, 0]]
    elif channels == 4:
        image_copy[..., [0, 1, 2, 3]] = image[..., [2, 1, 0, 3]]
    return image_copy
