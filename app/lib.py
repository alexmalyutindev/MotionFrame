from enum import Enum
import os
import cv2
import numpy as np
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

def encode_atlas(frames, atlas_width, atlas_height, frame_skip, motion_scale, motion_vector_encoding, is_loop, analyze_skipped_frames):
    color_atlas, total_frames = _create_color_atlas(frames, atlas_width, atlas_height, frame_skip)
    motion_atlas, flow_directions, max_strength = _create_motion_atlas(frames, atlas_width, atlas_height, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames)

    motion_scale = min(max(motion_scale, 0.01), 1.0)
    if motion_scale < 1.0:
        motion_atlas = cv2.resize(motion_atlas, None, fx=motion_scale, fy=motion_scale)

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

def _create_color_atlas(frames, atlas_width, atlas_height, frame_skip):
    height, width = frames[0].shape[:2]
    channels = channel_count(frames[0])

    if channels > 1:
        color_atlas = np.zeros([atlas_height * height, atlas_width * width, channels], dtype=np.uint8)
    else:
        color_atlas = np.zeros([atlas_height * height, atlas_width * width], dtype=np.uint8)

    _blit_image(frames[0], color_atlas, (0, 0))
    atlas_idx = 1
    for i in range(frame_skip + 1, len(frames), frame_skip + 1):
        _blit_image(frames[i], color_atlas, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
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

def _create_motion_atlas(frames, atlas_width, atlas_height, frame_skip, motion_vector_encoding, is_loop, analyze_skipped_frames):
    height, width = frames[0].shape[:2]
    motion_atlas = np.zeros([atlas_height * height, atlas_width * width, 3], dtype=np.uint8)

    # Zero motion vector is mid value except for SideFx Labs R8G8
    if motion_vector_encoding != MotionVectorEncoding.SIDEFX_LABS_R8G8:
        motion_atlas[:,:,1] = 127
        motion_atlas[:,:,2] = 127

    flow_directions = np.zeros_like(motion_atlas)  # Image for motion vector directions

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
        _blit_image(direction_image, flow_directions, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
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
    _blit_image(direction_image, flow_directions, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
    atlas_idx += 1

    flow_frames.append(flow)

    # Encode motion to a texture
    for atlas_idx, flow in enumerate(flow_frames):
        r, g = _encode_motion_vector(motion_vector_encoding, flow, max_strength)

        motion_vector = np.zeros([height, width, 3], dtype=np.uint8)
        motion_vector[..., 2] = np.clip(r, 0, 255).astype(np.uint8)
        motion_vector[..., 1] = np.clip(g, 0, 255).astype(np.uint8)

        _blit_image(motion_vector, motion_atlas, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))

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
        cv2.arrowedLine(vis, (x1, y1), (int(x1 + u * scale), int(y1 + v * scale)), (255, 0, 255), 1, tipLength = 0.2)

    return vis

def _blit_image(source, target, target_coords):
    channels = channel_count(source)
    x, y = target_coords
    source_height, source_width = source.shape[:2]
    if channels > 1:
        target[y:y+source_height, x:x+source_width, :] = source
    else:
        target[y:y+source_height, x:x+source_width] = source

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

