from enum import Enum, auto
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

def encode_atlas(frames, atlas_width, atlas_height, frame_skip, motion_scale, motion_vector_encoding):
    color_atlas, total_frames = _create_color_atlas(frames, atlas_width, atlas_height, frame_skip)
    motion_atlas, flow_directions, max_strength = _create_motion_atlas(frames, atlas_width, atlas_height, frame_skip, motion_vector_encoding)

    motion_scale = min(max(motion_scale, 0.01), 1.0)
    if motion_scale < 1.0:
        motion_atlas = cv2.resize(motion_atlas, None, fx=motion_scale, fy=motion_scale)

    return EncodeResult(color_atlas, motion_atlas, flow_directions, max_strength, total_frames)

def load_frames(pattern):
    frames = []
    idx = 1

    while True:
        file_path = pattern % idx
        idx += 1
        if not os.path.exists(file_path):
            break

        frame = imageio.imread(file_path)
        if frame is None:
            print(f'Image could not be loaded: {file_path}')
            break

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

    idx = 0
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
    magnitude[magnitude < 1e-6] = 0
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

def _create_motion_atlas(frames, atlas_width, atlas_height, frame_skip, motion_vector_encoding):
    height, width = frames[0].shape[:2]
    motion_atlas = np.zeros([atlas_height * height, atlas_width * width, 3], dtype=np.uint8)

    # Zero motion vector is mid value except for SideFx Labs R8G8
    if motion_vector_encoding != MotionVectorEncoding.SIDEFX_LABS_R8G8:
        motion_atlas[:,:,1] = 127
        motion_atlas[:,:,2] = 127

    flow_directions = np.zeros_like(motion_atlas)  # Image for motion vector directions

    max_strength = 0
    idx = 1
    atlas_idx = 0

    flow_frames = []

    while idx < len(frames):
        frame_batch = []
        idx -= 1

        # Prepare frames for optical flow computation.
        # This includes skipped frames.
        for i in range(frame_skip + 2):
            if idx >= len(frames):
                break

            current_frame = frames[idx]
            prepared_frame = _prepare_optical_flow_frame(current_frame)
            frame_batch.append(prepared_frame)

            idx += 1

        # Couldn't load enough frames for consistent displacement accumulation
        if len(frame_batch) != (frame_skip + 2):
            break

        flow = _accumulate_displacement(frame_batch)

        # Normalize the flow vectors based on image dimensions
        normalized_flow = np.zeros_like(flow)
        normalized_flow[..., 0] = np.clip(flow[..., 0] / width, -1, 1)
        normalized_flow[..., 1] = np.clip(flow[..., 1] / height, -1, 1)
        flow = normalized_flow

        if motion_vector_encoding == MotionVectorEncoding.SIDEFX_LABS_R8G8:
            max_strength = max(max_strength, np.sqrt(flow[..., 0]**2 + flow[..., 1]**2).max())
        else:
            max_strength = max(max_strength, np.abs(flow[..., 0]).max())
            max_strength = max(max_strength, np.abs(flow[..., 1]).max())

        # Draw optical flow directions visualization
        direction_image = _draw_optical_flow(flow, frame_batch[0], frame_batch[-1])
        _blit_image(direction_image, flow_directions, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))
        atlas_idx += 1

        flow_frames.append(flow)

    for atlas_idx, flow in enumerate(flow_frames):
        r, g = _encode_motion_vector(motion_vector_encoding, flow, max_strength)

        mask = np.zeros([height, width, 3], dtype=np.uint8)
        mask[..., 2] = np.clip(r, 0, 255).astype(np.uint8)
        mask[..., 1] = np.clip(g, 0, 255).astype(np.uint8)

        _blit_image(mask, motion_atlas, (((atlas_idx % atlas_width) * width), (atlas_idx // atlas_width) * height))

    return motion_atlas, flow_directions, max_strength

def _draw_optical_flow(flow, image, to_image, scale=1, step=16):
    h, w = image.shape[:2]
    y, x = np.mgrid[step//2:h:step, step//2:w:step].reshape(2, -1).astype(int)
    fx, fy = flow[y, x].T

    fx = fx * w
    fy = fy * h

    # Create an empty image with 3 channels
    height, width = image.shape
    vis = np.zeros((height, width, 3), dtype=np.uint8)
    vis[:, :, 2] = image  # Red channel
    vis[:, :, 1] = to_image  # Green channel

    for (x1, y1, u, v) in zip(x, y, fx, fy):
        cv2.arrowedLine(vis, (x1, y1), (int(x1 + u * scale), int(y1 + v * scale)), (255, 0, 255), 1, tipLength = 0.2)

    return vis

def _blit_image(source, target, target_coords):
    channels = channel_count(source)
    x, y = target_coords
    source_height, source_width = source.shape[0], source.shape[1]
    if channels > 1:
        target[y:y+source_height, x:x+source_width, :] = source
    else:
        target[y:y+source_height, x:x+source_width] = source

def _accumulate_displacement(frames):
    h, w = frames[0].shape[:2]
    accumulated_displacement = np.zeros((h, w, 2), np.float32)
    for i in range(1, len(frames)):
        prev_frame = frames[i-1]
        next_frame = frames[i]
        flow = cv2.calcOpticalFlowFarneback(prev_frame, next_frame, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        current_x = (grid_x + accumulated_displacement[..., 0]).astype(np.float32)
        current_y = (grid_y + accumulated_displacement[..., 1]).astype(np.float32)
        displacement_x = cv2.remap(flow[..., 0], current_x, current_y, interpolation=cv2.INTER_LINEAR)
        displacement_y = cv2.remap(flow[..., 1], current_x, current_y, interpolation=cv2.INTER_LINEAR)
        accumulated_displacement[..., 0] += displacement_x
        accumulated_displacement[..., 1] += displacement_y
    return accumulated_displacement

