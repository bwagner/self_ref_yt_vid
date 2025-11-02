#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "opencv-python",
#   "numpy",
#   "qrcode[pil]",
#   "rich",
#   "typer",
# ]
# ///


"""
Creates a video of changing qrcodes for a given audio file.
These qrcodes point to the location in the audio file currently playing.
Purpose: you're listening to this audio file on youtube. When you want to bookmark or share a specific
moment in the file, pause the video and point your iphone camera at the qr-code in the video: the qr-code
points to that location in the audio.
Optionally, an srt-file (Subtitles) is generated.

Usage:
1. Prepare a unique url on tinyurl.com, without yet creating it.
2. This is the "Base URL stem for the shortener.", e.g. tinyurl.com/arp20130725
3. Call this script with the audio file name and the above tinyurl as parameters.
   The script will generate a video with the given audio and a qr-code in the video that will
   change every second and will point to, e.g.  https://tinyurl.com/arp20130725?t=565
4. Upload the generated video to youtube.
5. Optionally upload the generated srt-file.
6. Complete the shortened url on tinyurl for the prepared url, letting it point to the youtube-url
   of your new video.
Done.

Since youtube will remember where you stopped playing a video, and that moment seems to have
precedence over the t=xx setting, it is recommended to use the qr-encoded urls in incognito browser
windows, such that youtube can't have any knowledge of prior play positions of that particular video.
"""

import subprocess
from pathlib import Path

import cv2
import numpy as np
import qrcode
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


def seconds_to_hms(s: int):
    parts = []
    for _ in range(2):
        s, x = divmod(s, 60)
        parts.append(x)
    parts.append(s)
    return ":".join([f"{int(x):02}" for x in reversed(parts)])


def create_qrcode_image(url: str):
    """
    Create a QR code with a black background for a given URL and return it as an OpenCV image.

    Args:
        url (str): The URL to encode into the QR code.

    Returns:
        np.ndarray: OpenCV image of the QR code.
    """
    # QR code settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code with black background
    pil_img = qr.make_image(fill_color="white", back_color="black")

    # Convert PIL Image to OpenCV format
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img


def get_media_duration(media_file):
    # Get the duration of the input media in seconds using ffprobe
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        media_file,
    ]
    duration = float(subprocess.check_output(cmd).strip())
    return duration


def generate_subtitles(
    shortener_stem: str, total_duration: int, qr_duration: int, subtitle_file_path: str
):
    with open(subtitle_file_path, "w") as sub:
        for i in range(0, total_duration, qr_duration):
            sub.write(f"{int(i/qr_duration) + 1}\n")
            start_time = seconds_to_hms(i)
            end_time = seconds_to_hms(min(i + qr_duration, total_duration))
            sub.write(f"{start_time} --> {end_time}\n")
            sub.write(f"{shortener_stem}?t={i}\n\n")


def create_qr_video_with_audio(
    shortener_stem: str, audio_file_path: str, output_video: str, qr_duration: int
):
    """Creates a video of QR codes based on audio duration and shortener_stem, and combine with audio."""

    video_duration = get_media_duration(audio_file_path)
    total_qr_codes = int((video_duration + qr_duration - 1) / qr_duration)

    height, width, layers = create_qrcode_image(shortener_stem + "?t=0").shape
    fps = 30
    frames_per_qr = qr_duration * fps

    # Define ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{width}x{height}",
        "-pix_fmt",
        "bgr24",  # OpenCV uses bgr format
        "-r",
        str(fps),
        "-i",
        "-",  # Input from pipe
        "-thread_queue_size",
        "512",  # Increase the thread_queue_size
        "-i",
        audio_file_path,
        "-c:v",
        "libx264",  # Video codec
        "-pix_fmt",
        "yuv420p",  # Set pixel format for broader compatibility
        "-profile:v",
        "main",  # Main profile for H.264 video
        "-c:a",
        "aac",  # Audio codec
        "-strict",
        "experimental",
        output_video,
    ]

    # Initialize the progress bar
    total_time_used = None
    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        "Elapsed:",
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("[cyan]Creating video...", total=total_qr_codes)

        # Start ffmpeg subprocess and suppress its output
        with subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ) as pipe:
            for i in range(total_qr_codes):
                time_in_seconds = i * qr_duration
                qr_url = f"{shortener_stem}?t={time_in_seconds}"
                img = create_qrcode_image(qr_url)
                for _ in range(frames_per_qr):
                    pipe.stdin.write(img.tobytes())

                # Update the progress bar
                progress.update(task, advance=1)
        total_time_used = progress.tasks[0].elapsed
    return video_duration, total_time_used


if __name__ == "__main__":

    import sys

    import typer

    def custom_help_check():
        if "-h" in sys.argv or "-?" in sys.argv:
            sys.argv[1] = "--help"

    def main(
        audio_file_path: str = typer.Argument(
            ...,
            help="Path to the audio file whose duration will determine the length of the video.",
        ),
        shortener_stem: str = typer.Argument(
            ...,
            help="Base URL stem for the shortener. QR codes will be generated based on this stem.",
        ),
        output_video: str = typer.Option(
            None,
            "--output",
            "-o",
            help="Output path for the generated QR code video.",
            show_default = "stem of audio file .mp4",
        ),
        qr_duration: int = typer.Option(
            1,
            "--duration",
            "-d",
            help="Duration in seconds for which each QR code is displayed in the video.",
        ),
        generate_video: bool = typer.Option(
            True, "--generate-video", help="Generate video file."
        ),
        subtitles_only: bool = typer.Option(
            False, "--subtitles-only", help="Generate only subtitles."
        ),
    ):
        output_video = output_video or f"{Path(audio_file_path).stem}.mp4"
        video_duration = int(get_media_duration(audio_file_path))
        subtitle_file_path = Path(output_video).with_suffix(".srt")

        if "_" in shortener_stem:
            print(f"Argument shortener_stem ({shortener_stem}) may not contain \"_\". Quitting.")
            return

        if not shortener_stem.startswith("http"):
            print(f"Argument shortener_stem ({shortener_stem}) must start with \"http\". Quitting.")

        if subtitles_only or generate_video:
            generate_subtitles(
                shortener_stem, video_duration, qr_duration, subtitle_file_path
            )
            typer.echo(f"Subtitles file '{subtitle_file_path}' generated.")

        if generate_video and not subtitles_only:
            vid_duration, time_used = create_qr_video_with_audio(
                shortener_stem, audio_file_path, output_video, qr_duration
            )
            typer.echo(
                f"Video '{output_video}' of duration {seconds_to_hms(vid_duration)} generated in {seconds_to_hms(time_used)}."
            )

    custom_help_check()
    typer.run(main)
