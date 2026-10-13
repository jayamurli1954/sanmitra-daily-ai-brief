"""
Render a long Remotion composition in frame chunks, then join them.

A single ~22,000-frame render on the production PC has crashed with "Target
closed", so the master is rendered in chunks of about 6,000 frames. Each chunk
keeps uncompressed PCM audio (in .mkv) and the audio is encoded to AAC once
when the chunks are joined, so there are no gaps or clicks at the joins.

The frame count comes from Remotion itself. timings.json is not a reliable
source: it holds one entry per transition id, while the video repeats a
transition at every region change (it ran 240 frames short on 2026-10-12).

Usage:
    python render_master.py out/aibrief/AI_News_2026-10-13.mp4
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

COMPOSITION = "AIBriefMaster16x9"
CHUNK_FRAMES = 6000


def _npx(*args: str) -> list:
    return ["npx.cmd" if sys.platform == "win32" else "npx", *args]


def composition_frames(composition: str = COMPOSITION) -> int:
    res = subprocess.run(_npx("remotion", "compositions"), capture_output=True,
                         text=True, encoding="utf-8", errors="replace")
    for line in res.stdout.splitlines():
        m = re.match(rf"\s*{re.escape(composition)}\s+\d+\s+\d+x\d+\s+(\d+)\b", line)
        if m:
            return int(m.group(1))
    raise RuntimeError(f"Could not read the frame count of {composition}:\n{res.stdout[-2000:]}{res.stderr[-2000:]}")


def chunk_ranges(total: int, size: int = CHUNK_FRAMES) -> list:
    return [(start, min(start + size, total) - 1) for start in range(0, total, size)]


def render_in_chunks(out_path: str, composition: str = COMPOSITION, size: int = CHUNK_FRAMES) -> bool:
    total = composition_frames(composition)
    gl = "angle" if sys.platform == "win32" else "swangle"
    parts_dir = os.path.join(os.path.dirname(out_path) or ".", "chunks")
    shutil.rmtree(parts_dir, ignore_errors=True)
    os.makedirs(parts_dir)
    print(f"[*] {composition}: {total} frames ({total / 30 / 60:.1f} min) in {len(chunk_ranges(total, size))} chunks", flush=True)

    parts = []
    for i, (start, end) in enumerate(chunk_ranges(total, size)):
        part = os.path.join(parts_dir, f"part_{i:02d}.mkv")
        cmd = _npx("remotion", "render", composition, part, f"--frames={start}-{end}",
                   "--codec=h264", "--audio-codec=pcm-16", "--concurrency=2",
                   "--timeout=120000", f"--gl={gl}", "--log=warn")
        for attempt in (1, 2):
            print(f"[*] Chunk {i + 1}: frames {start}-{end} (attempt {attempt})", flush=True)
            if subprocess.run(cmd).returncode == 0 and os.path.getsize(part) > 0:
                break
        else:
            print(f"[X] Chunk {i + 1} failed twice.", flush=True)
            return False
        parts.append(part)

    listfile = os.path.join(parts_dir, "list.txt")
    with open(listfile, "w", encoding="utf-8") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    join = _npx("remotion", "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                "-i", listfile, "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                "-movflags", "+faststart", out_path)
    if subprocess.run(join).returncode != 0 or not os.path.exists(out_path):
        print("[X] Joining chunks failed.", flush=True)
        return False

    probe = subprocess.run(_npx("remotion", "ffprobe", "-v", "error", "-select_streams", "v:0",
                                "-count_packets", "-show_entries", "stream=nb_read_packets",
                                "-of", "csv=p=0", out_path), capture_output=True, text=True)
    frames = int((probe.stdout.strip().splitlines() or ["0"])[0] or 0)
    if frames != total:
        print(f"[X] Joined video has {frames} frames, expected {total}.", flush=True)
        return False
    shutil.rmtree(parts_dir, ignore_errors=True)
    print(f"[+] Rendered {out_path} ({frames} frames)", flush=True)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("out", help="Output .mp4 path")
    parser.add_argument("--chunk-frames", type=int, default=CHUNK_FRAMES)
    args = parser.parse_args()
    sys.exit(0 if render_in_chunks(args.out, size=args.chunk_frames) else 1)
