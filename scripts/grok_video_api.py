#!/usr/bin/env python3
"""
xAI Grok Imagine Video API Client
Handles text-to-video, image-to-video, and video editing via natural language.
"""

import requests
import time
import json
import os
from typing import Optional, Dict, Any


class GrokImagineVideoClient:
    """Client for interacting with xAI Grok Imagine Video API."""

    def __init__(self, api_key: str, base_url: str = "https://api.x.ai/v1"):
        """
        Initialize the client.

        Args:
            api_key: xAI API key from environment or config
            base_url: API base URL (default: https://api.x.ai/v1)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def text_to_video(
        self,
        prompt: str,
        duration: int = 10,
        aspect_ratio: str = "16:9",
        resolution: str = "480p"
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt.

        Args:
            prompt: Text description of the video to generate
            duration: Video duration in seconds (1-15)
            aspect_ratio: Aspect ratio (16:9, 9:16, 1:1, 4:3, 3:4, 3:2, 2:3)
            resolution: Resolution (480p, 720p)

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        duration: int = 10
    ) -> Dict[str, Any]:
        """
        Animate a static image into video.

        Args:
            image_url: Public URL of the source image OR base64 data URI
            prompt: Optional text prompt to guide animation
            duration: Video duration in seconds (1-15)

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": prompt,
            "image": {"url": image_url},
            "duration": duration
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_video(
        self,
        video_url: str,
        edit_prompt: str
    ) -> Dict[str, Any]:
        """
        Edit an existing video via natural language instruction.

        Args:
            video_url: Public URL of the source video
            edit_prompt: Natural language instruction for the edit

        Returns:
            API response with request_id
        """
        url = f"{self.base_url}/videos/generations"
        payload = {
            "model": "grok-imagine-video",
            "prompt": edit_prompt,
            "video_url": video_url
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def generate_image(
        self,
        prompt: str,
        n: int = 1,
        aspect_ratio: str = "1:1",
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Generate images from a text prompt.

        Args:
            prompt: Text description of the image to generate
            n: Number of image variations (1-10)
            aspect_ratio: Aspect ratio (1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, etc.)
            response_format: "url" for temporary URL or "b64_json" for base64 data

        Returns:
            API response with image URL(s) or base64 data
        """
        url = f"{self.base_url}/images/generations"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "n": n,
            "aspect_ratio": aspect_ratio,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def edit_image(
        self,
        image_url: str,
        prompt: str,
        n: int = 1,
        response_format: str = "url"
    ) -> Dict[str, Any]:
        """
        Edit an existing image via natural language instruction.

        Args:
            image_url: Public URL or base64 data URI of the source image
            prompt: Natural language instruction for the edit
            n: Number of variations (1-10)
            response_format: "url" for temporary URL or "b64_json" for base64 data

        Returns:
            API response with edited image URL(s) or base64 data
        """
        url = f"{self.base_url}/images/edits"
        payload = {
            "model": "grok-imagine-image",
            "prompt": prompt,
            "image": {"url": image_url, "type": "image_url"},
            "n": n,
            "response_format": response_format
        }

        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def download_image(self, image_url: str, output_path: str) -> str:
        """
        Download a generated image file.

        Args:
            image_url: URL of the generated image
            output_path: Local path to save the image

        Returns:
            Path to the downloaded file
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    def get_job_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check the status of a video generation request.

        Args:
            request_id: The request ID from the initial generation request

        Returns:
            Job status with fields: status (if pending), video (if done)
        """
        url = f"{self.base_url}/videos/{request_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def wait_for_completion(
        self,
        request_id: str,
        poll_interval: int = 10,
        timeout: int = 600,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Poll job status until completion or timeout.

        Args:
            request_id: The request ID to poll
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            progress_callback: Optional function called with progress updates

        Returns:
            Final response with video_url if successful

        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            response = self.get_job_status(request_id)

            if progress_callback:
                progress_callback(response)

            # Check if video is done (response has video object)
            if "video" in response and response.get("video", {}).get("url"):
                return response

            # If not done, wait and retry
            time.sleep(poll_interval)

        raise TimeoutError(f"Request {request_id} timed out after {timeout} seconds")

    def download_video(self, response_data: Dict[str, Any], output_path: str) -> str:
        """
        Download a completed video file.

        Args:
            response_data: Response from get_job_status (contains video.url)
            output_path: Local path to save the video

        Returns:
            Path to the downloaded file
        """
        video_url = response_data.get("video", {}).get("url")
        if not video_url:
            raise ValueError("No video URL in response")

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    # ─── Long Video ────────────────────────────────────────────────────────

    def _extract_last_frame(self, video_path: str, output_path: str) -> str:
        """
        Extract the last frame of a video as a JPEG image.
        Uses ffmpeg. Requires ffmpeg to be installed.
        """
        import subprocess
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-sseof", "-1",
                "-i", video_path,
                "-frames:v", "1",
                "-q:v", "2",
                output_path
            ],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to extract last frame: {result.stderr}")
        return output_path

    def generate_long_video(
        self,
        prompt: str,
        total_duration: int,
        aspect_ratio: str = "16:9",
        resolution: str = "480p",
        output_dir: str = "/tmp",
        segment_duration: int = 15,
        poll_interval: int = 10,
        timeout: int = 600,
        progress_callback: Optional[Any] = None,
        image_url: str = "",
        scenes: Optional[list] = None
    ) -> list:
        """
        Generate a video longer than 15 seconds via sequential frame-chaining.

        Each segment is generated one at a time. After a segment completes,
        its last frame is extracted and used as the input image for the next
        segment — creating smooth continuous motion instead of jump cuts.

        **Multi-scene mode:** Pass a list of scene dicts via the `scenes`
        parameter. Each scene has its own prompt (and optional image_url).
        This lets you craft a narrative movie where each scene has distinct
        action while maintaining visual continuity through frame-chaining.

        Args:
            prompt: Default prompt used for all segments if `scenes` is not set.
            total_duration: Total desired duration in seconds (unlimited).
            aspect_ratio: Aspect ratio. Default: 16:9.
            resolution: "480p" or "720p". Default: 480p.
            output_dir: Directory to save downloaded segment files.
            segment_duration: Maximum seconds per API call (1-15). Default: 15.
            poll_interval: Seconds between status checks. Default: 10.
            timeout: Maximum seconds to wait for all segments. Default: 600.
            progress_callback: Optional callable (segment_index, total, status).
            image_url: Optional starting image URL for the first segment.
            scenes: Optional list of scene dicts for multi-prompt movie mode.
                Each dict: {"prompt": "...", "duration": 10, "image_url": "..."}
                The last frame of each scene chains into the next automatically.

        Returns:
            Ordered list of local file paths for each segment.
        """
        import math

        if not 1 <= segment_duration <= 15:
            raise ValueError("segment_duration must be between 1 and 15")

        n_segments = math.ceil(total_duration / segment_duration)
        durations = []
        remaining = total_duration
        for _ in range(n_segments):
            seg = min(segment_duration, remaining)
            durations.append(seg)
            remaining -= seg

        # ── Build per-segment prompt/image plan ───────────────────────────
        if scenes:
            # Flatten scenes into per-segment instructions
            segment_plan = []
            for scene in scenes:
                scene_dur = scene.get("duration", segment_duration)
                scene_n = math.ceil(scene_dur / segment_duration)
                for _ in range(scene_n):
                    segment_plan.append({
                        "prompt": scene.get("prompt", prompt),
                        "image_url": scene.get("image_url", ""),
                    })
        else:
            # Single-prompt chaining mode
            segment_plan = [
                {"prompt": prompt, "image_url": image_url if i == 0 else ""}
                for i in range(n_segments)
            ]

        import os as _os
        _os.makedirs(output_dir, exist_ok=True)

        current_image = image_url
        segment_paths = []
        start_time = time.time()
        total_segments = len(segment_plan)

        for i, plan in enumerate(segment_plan):
            dur = min(durations[i] if i < len(durations) else segment_duration, segment_duration)
            remaining_timeout = max(timeout - (time.time() - start_time), 60)

            seg_prompt = plan["prompt"]
            seg_image = plan["image_url"] if plan.get("image_url") else current_image

            if seg_image:
                result = self.image_to_video(
                    image_url=seg_image,
                    prompt=seg_prompt,
                    duration=dur
                )
            else:
                result = self.text_to_video(
                    prompt=seg_prompt,
                    duration=dur,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution
                )

            request_id = result["request_id"]
            if progress_callback:
                progress_callback(i, total_segments, f"chaining")

            response = self.wait_for_completion(
                request_id,
                poll_interval=poll_interval,
                timeout=remaining_timeout
            )

            seg_path = _os.path.join(output_dir, f"segment_{i:04d}.mp4")
            self.download_video(response, seg_path)
            segment_paths.append(seg_path)

            if progress_callback:
                progress_callback(i, total_segments, "done")

            frame_path = _os.path.join(output_dir, f"chain_frame_{i:04d}.jpg")
            self._extract_last_frame(seg_path, frame_path)
            current_image = f"data:image/jpeg;base64,{self._image_to_base64(frame_path)}"

            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Timeout reached at segment {i+1}/{total_segments}")

        return segment_paths

    def generate_movie(
        self,
        scenes: list,
        output_dir: str = "/tmp",
        resolution: str = "720p",
        poll_interval: int = 10,
        timeout: int = 1800,
        progress_callback: Optional[Any] = None
    ) -> str:
        """
        Generate a narrative movie from a list of scenes, each with its own prompt.
        Segments are frame-chained between scenes for smooth visual continuity.

        Each scene's last frame automatically becomes the first frame of the next
        scene's video, creating seamless motion across scene transitions.

        Args:
            scenes: List of scene dicts. Each dict:
                {
                    "prompt": "Description of what happens in this scene",
                    "duration": 10,          # How long this scene lasts (seconds)
                    "image_url": "..."      # Optional starting image for scene 1
                }
                Duration is split into 10s segments internally. Each segment
                chains from the last frame of the previous segment.
            output_dir: Directory for temp files. Default: /tmp.
            resolution: "480p" or "720p". Default: 720p.
            poll_interval: Seconds between status polls. Default: 10.
            timeout: Max seconds total. Default: 1800 (30 min).
            progress_callback: Optional callable (scene_index, total, status).

        Returns:
            Path to the final concatenated movie file.

        Example:
            client.generate_movie([
                {"prompt": "A superhero stands tall in a dark city, cape billowing",
                 "duration": 15, "image_url": "https://example.com/hero.jpg"},
                {"prompt": "The hero launches into the sky, lightning crackling around them",
                 "duration": 15},
                {"prompt": "Flying over a stormy ocean as the sun sets dramatically",
                 "duration": 15},
                {"prompt": "Landing gracefully on a rooftop as the city lights flicker on",
                 "duration": 15},
            ])
        """
        import os as _os, math

        total_duration = sum(s.get("duration", 10) for s in scenes)

        def _scene_progress(scene_idx, total, status):
            if progress_callback:
                progress_callback(scene_idx, total, status)

        _os.makedirs(output_dir, exist_ok=True)

        # Flatten scenes into frame-chained segments
        segment_plan = []
        for scene_idx, scene in enumerate(scenes):
            dur = scene.get("duration", 10)
            n_segs = math.ceil(dur / 10)  # 10s per segment
            for seg_i in range(n_segs):
                segment_plan.append({
                    "scene_idx": scene_idx,
                    "prompt": scene.get("prompt", ""),
                    "image_url": scene.get("image_url", "") if seg_i == 0 else ""
                })

        total_segments = len(segment_plan)
        current_image = scenes[0].get("image_url", "") if scenes else ""
        segment_paths = []
        start_time = time.time()

        for i, plan in enumerate(segment_plan):
            remaining_timeout = max(timeout - (time.time() - start_time), 60)

            # Only pass image_url on the first segment of a new scene
            seg_image = plan["image_url"] if plan["image_url"] else current_image

            result = self.image_to_video(
                image_url=seg_image,
                prompt=plan["prompt"],
                duration=10
            )

            request_id = result["request_id"]
            _scene_progress(plan["scene_idx"], total_segments, f"seg {i+1}/{total_segments}")

            response = self.wait_for_completion(
                request_id,
                poll_interval=poll_interval,
                timeout=remaining_timeout
            )

            seg_path = _os.path.join(output_dir, f"segment_{i:04d}.mp4")
            self.download_video(response, seg_path)
            segment_paths.append(seg_path)

            _scene_progress(plan["scene_idx"], total_segments, f"done")

            frame_path = _os.path.join(output_dir, f"chain_frame_{i:04d}.jpg")
            self._extract_last_frame(seg_path, frame_path)
            current_image = f"data:image/jpeg;base64,{self._image_to_base64(frame_path)}"

            if time.time() - start_time >= timeout:
                raise TimeoutError(f"Timeout at segment {i+1}/{total_segments}")

        output_path = _os.path.join(output_dir, "movie.mp4")
        self.concatenate_segments(segment_paths, output_path)
        return output_path

    def _image_to_base64(self, image_path: str) -> str:
        """Read an image file and return its base64-encoded string."""
        import base64
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def concatenate_segments(self, segment_paths: list, output_path: str) -> str:
        """
        Concatenate video segments into a single file using ffmpeg.

        Requires ffmpeg to be installed and accessible in PATH.

        Args:
            segment_paths: Ordered list of local segment file paths.
            output_path: Local path for the final concatenated video.

        Returns:
            The output_path that was written.
        """
        import subprocess, tempfile as _tempfile, os as _os

        for path in segment_paths:
            if not _os.path.exists(path):
                raise FileNotFoundError(f"Segment not found: {path}")

        out_dir = _os.path.dirname(_os.path.abspath(output_path))
        if out_dir:
            _os.makedirs(out_dir, exist_ok=True)

        with _tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            concat_list = f.name
            for path in segment_paths:
                f.write(f"file '{_os.path.abspath(path)}'\n")

        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                 "-i", concat_list, "-c", "copy", output_path],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
        finally:
            _os.unlink(concat_list)

        return output_path


def main():
    """Example usage."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY environment variable not set")
        return 1

    client = GrokImagineVideoClient(api_key)

    # Choose mode:
    # 1. Text-to-video
    # 2. Image-to-video
    # 3. Video editing

    mode = "text"  # Change to "image" or "edit" for other modes

    if mode == "text":
        # Example: Text-to-video
        print("Starting text-to-video generation...")
        result = client.text_to_video("A beautiful sunset over the ocean", duration=10)
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    elif mode == "image":
        # Example: Image-to-video
        print("Starting image-to-video generation...")
        result = client.image_to_video(
            image_url="https://example.com/landscape.jpg",
            prompt="Animate the clouds and add gentle wind",
            duration=10
        )
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    elif mode == "edit":
        # Example: Video editing
        print("Starting video edit...")
        result = client.edit_video(
            video_url="https://example.com/source.mp4",
            edit_prompt="Add a warm sunset filter"
        )
        request_id = result.get("request_id")
        print(f"Job started: {request_id}")

    # Wait for completion
    print("Waiting for completion...")
    final_response = client.wait_for_completion(
        request_id,
        progress_callback=lambda r: print(f"Polling... {'Done!' if 'video' in r else 'Pending'}")
    )

    video_url = final_response.get("video", {}).get("url")
    print(f"Video ready: {video_url}")

    # Download
    output_path = "/tmp/video_output.mp4"
    client.download_video(final_response, output_path)
    print(f"Downloaded to: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
