# Running QR Codes for YouTube Audio

Generate a video of **continuously updating QR codes** that point to the *current timestamp* of your audio on YouTube.  
Viewers can pause at any moment, scan the on-screen QR, and jump straight to that exact time.

> **Use case:** Long podcasts, lectures, or interviews uploaded to YouTube.  
> This script makes it easy to bookmark and share precise moments with a phone camera—no scrubbing required.

---

## ✨ Features

- Creates a video with QR codes that update every *N* seconds.
- QR codes point to `SHORTENER_URL?t=SECONDS`.
- Muxes video + audio into an H.264 MP4 with AAC audio.
- Optionally generates an `.srt` subtitle file with URLs per timestamp.
- Designed for use with URL shorteners like TinyURL.

---

## 📦 Requirements

- **Python 3.9+**
- **ffmpeg + ffprobe** installed and in `PATH`
- Python dependencies:
  - `opencv-python`
  - `numpy`
  - `qrcode[pil]`
  - `rich`
  - `typer`

> If you use [uv](https://github.com/astral-sh/uv), the shebang at the top of the script handles dependencies automatically.

---

## 🔗 Workflow with TinyURL

1. Pick a unique short URL stem (don’t create it yet), e.g.  
   `https://tinyurl.com/myshow2025`
2. Run the script with your audio file and the chosen stem.
3. Upload the generated video (and optional `.srt`) to YouTube.
4. Create the TinyURL and point it to your YouTube video URL.
5. Scanning QR codes in the video now jumps to the correct timestamp.

---

## 🚀 Usage

### Using `uv` (recommended)

```bash
chmod +x run_qr_codes.py
./run_qr_codes.py audio.mp3 https://tinyurl.com/myshow2025 -o qr_codes_video.mp4 -d 1
```

### Using Python directly

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install opencv-python numpy "qrcode[pil]" rich typer

python run_qr_codes.py audio.mp3 https://tinyurl.com/myshow2025 \
  --output qr_codes_video.mp4 --duration 1
```

---

## 🧰 CLI Reference

```
Usage: run_qr_codes.py [OPTIONS] AUDIO_FILE_PATH SHORTENER_STEM

Arguments:
  AUDIO_FILE_PATH  Path to the audio file. [required]
  SHORTENER_STEM   Base URL stem for the shortener. Example: https://tinyurl.com/myshow2025 [required]

Options:
  -o, --output TEXT         Output video path [default: qr_codes_video.mp4]
  -d, --duration INTEGER    Seconds per QR code [default: 1]
      --generate-video      Generate video [default: True]
      --subtitles-only      Generate only subtitles
  -h, -?                    Show help
```

---

## 🗂️ Outputs

- `qr_codes_video.mp4` – video with QR codes + audio  
- `qr_codes_video.srt` – matching subtitles with QR URLs

Example `.srt`:

```
1
00:00:00 --> 00:00:01
https://tinyurl.com/myshow2025?t=0

2
00:00:01 --> 00:00:02
https://tinyurl.com/myshow2025?t=1
```

---

## ⚙️ Tips

- Use **incognito mode** when testing, to prevent YouTube’s resume position from overriding `t=…`.
- For better scan reliability:
  - Increase QR display duration (`-d 2` or `-d 5`).
  - Scale video to higher resolution after rendering:
    ```bash
    ffmpeg -i qr_codes_video.mp4 -vf "scale=1920:1080:flags=neighbor" -c:a copy qr_1080p.mp4
    ```

---

## 📁 Project Structure

```
.
├── run_qr_codes.py   # Main script
└── README.md
```

---

## 🧾 License

MIT License

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

## 🙌 Acknowledgements

- [ffmpeg](https://ffmpeg.org/)
- [qrcode](https://pypi.org/project/qrcode/)
- [opencv-python](https://pypi.org/project/opencv-python/)
- [rich](https://pypi.org/project/rich/)
- [typer](https://typer.tiangolo.com/)
