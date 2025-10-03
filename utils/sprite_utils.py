#!/usr/bin/env python3
"""
Sprite manipulation utilities
Provides tools for cutting and processing sprite sheets
"""

import numpy as np
from PIL import Image


class SpriteCutter:
    """Utility for slicing sprite sheets into individual frames"""

    @staticmethod
    def parse_dimensions(dimension_str):
        """
        Parse dimension string

        Args:
            dimension_str: String like '48' or '48x48'

        Returns:
            Tuple of (width, height) or (width, None)
        """
        if "x" in dimension_str:
            width, height = map(int, dimension_str.lower().split("x"))
            return width, height
        else:
            return int(dimension_str), None

    @staticmethod
    def detect_transparent_regions(img, direction="h"):
        """
        Detect non-transparent regions in image

        Args:
            img: PIL Image with transparency
            direction: 'h' for horizontal, 'v' for vertical

        Returns:
            List of (start, end) tuples for regions
        """
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        data = np.array(img)
        alpha = data[:, :, 3]

        if direction == "h":
            non_transparent_cols = []
            for x in range(img.width):
                if np.any(alpha[:, x] > 0):
                    non_transparent_cols.append(x)
        else:
            non_transparent_cols = []
            for y in range(img.height):
                if np.any(alpha[y, :] > 0):
                    non_transparent_cols.append(y)

        # Group consecutive columns
        regions = []
        if non_transparent_cols:
            start = non_transparent_cols[0]
            prev = start

            for col in non_transparent_cols[1:]:
                if col > prev + 1:
                    regions.append((start, prev))
                    start = col
                prev = col

            regions.append((start, prev))

        return regions

    @staticmethod
    def calculate_dimensions(img, width, height, slices, direction="h"):
        """
        Calculate frame dimensions

        Args:
            img: PIL Image
            width: Frame width
            height: Frame height
            slices: Number of slices
            direction: 'h' or 'v'

        Returns:
            Tuple of (frame_width, frame_height)
        """
        if direction == "h":
            img_width = img.width
            img_height = img.height
        else:
            img_width = img.height
            img_height = img.width

        if width is not None:
            frame_width = width
            frame_height = height if height is not None else img_height
        elif slices is not None:
            frame_width = img_width // slices
            frame_height = img_height
        else:
            raise ValueError("Either width or slices must be specified")

        return frame_width, frame_height

    @staticmethod
    def slice_sprite(img, width=None, height=None, slices=None, direction="h",
                    auto_detect=True, padding=0, resize=None):
        """
        Slice sprite sheet into frames

        Args:
            img: PIL Image to slice
            width: Frame width
            height: Frame height
            slices: Number of slices
            direction: 'h' for horizontal, 'v' for vertical
            auto_detect: Auto-detect transparent regions
            padding: Padding around frames
            resize: Tuple (width, height) to resize frames

        Returns:
            List of PIL Image frames
        """
        frame_width, frame_height = SpriteCutter.calculate_dimensions(
            img, width, height, slices, direction
        )

        frames = []

        if auto_detect:
            regions = SpriteCutter.detect_transparent_regions(img, direction)

            if not regions:
                return frames

            for start, end in regions:
                if direction == "h":
                    frame = img.crop((start, 0, end + 1, img.height))
                else:
                    frame = img.crop((0, start, img.width, end + 1))

                if padding > 0:
                    padded_frame = Image.new('RGBA',
                                           (frame.width + 2*padding, frame.height + 2*padding),
                                           (0, 0, 0, 0))
                    padded_frame.paste(frame, (padding, padding))
                    frame = padded_frame

                if resize:
                    frame = frame.resize(resize, Image.LANCZOS)

                frames.append(frame)
        else:
            # Fixed size slicing
            if direction == "h":
                for i in range(slices or (img.width // frame_width)):
                    start_x = i * frame_width
                    if start_x >= img.width:
                        break

                    end_x = min(start_x + frame_width, img.width)
                    frame = img.crop((start_x, 0, end_x, frame_height))

                    if padding > 0:
                        padded_frame = Image.new('RGBA',
                                               (frame.width + 2*padding, frame.height + 2*padding),
                                               (0, 0, 0, 0))
                        padded_frame.paste(frame, (padding, padding))
                        frame = padded_frame

                    if resize:
                        frame = frame.resize(resize, Image.LANCZOS)

                    frames.append(frame)
            else:
                # Vertical slicing
                for i in range(slices or (img.height // frame_height)):
                    start_y = i * frame_height
                    if start_y >= img.height:
                        break

                    end_y = min(start_y + frame_height, img.height)
                    frame = img.crop((0, start_y, frame_width, end_y))

                    if padding > 0:
                        padded_frame = Image.new('RGBA',
                                               (frame.width + 2*padding, frame.height + 2*padding),
                                               (0, 0, 0, 0))
                        padded_frame.paste(frame, (padding, padding))
                        frame = padded_frame

                    if resize:
                        frame = frame.resize(resize, Image.LANCZOS)

                    frames.append(frame)

        return frames
