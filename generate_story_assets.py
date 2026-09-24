import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

ASSETS_DIR = "public/aibrief/assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

WIDTH, HEIGHT = 1920, 1080

def create_cyber_gradient(draw, top_color, bottom_color):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

def draw_grid(draw, color=(16, 42, 77), step=60):
    for x in range(0, WIDTH, step):
        draw.line([(x, 0), (x, HEIGHT)], fill=color, width=1)
    for y in range(0, HEIGHT, step):
        draw.line([(0, y), (WIDTH, y)], fill=color, width=1)

def draw_radial_glow(img, center, radius, color):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    cx, cy = center
    for r in range(radius, 0, -20):
        alpha = int(45 * (1.0 - (r / radius)))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))
    img.alpha_composite(overlay)

# Today's 2026-09-24 Story Assets

def render_gpt6_astra():
    out_file = os.path.join(ASSETS_DIR, "gpt6_astra.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 14, 28, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (10, 24, 40), (3, 7, 18))
    draw_grid(draw, (20, 48, 76))
    draw_radial_glow(img, (960, 480), 550, (16, 163, 127))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(15, 23, 42, 240), outline=(16, 185, 129), width=3)
    draw.text((360, 215), "AUTONOMOUS ENTERPRISE AGENTS • FRONTIER LAB LAUNCH", fill=(52, 211, 153))
    draw.text((360, 265), "OpenAI GPT-6 Astra: End-to-End Enterprise Task Execution", fill=(255, 255, 255))

    # Architecture panels
    draw.rounded_rectangle([260, 400, 920, 700], radius=16, fill=(15, 28, 50, 230), outline=(16, 163, 127), width=2)
    draw.text((290, 435), "AGENTIC EXECUTION FABRIC", fill=(52, 211, 153))
    draw.text((290, 490), "• Multi-step software & data workflow orchestration", fill=(226, 232, 240))
    draw.text((290, 540), "• Self-correcting test & tool-use loops", fill=(148, 163, 184))
    draw.text((290, 590), "• Sandboxed runtime with strict access tokens", fill=(148, 163, 184))

    draw.rounded_rectangle([1000, 400, 1660, 700], radius=16, fill=(15, 28, 50, 230), outline=(56, 189, 248), width=2)
    draw.text((1030, 435), "DEVDAY 2026 ROADMAP", fill=(56, 189, 248))
    draw.text((1030, 490), "• Scheduled for September 29 Global Keynote", fill=(226, 232, 240))
    draw.text((1030, 540), "• Managed enterprise agent platform preview", fill=(148, 163, 184))
    draw.text((1030, 590), "• High-throughput batch inference endpoints", fill=(148, 163, 184))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

def render_anthropic_accenture():
    out_file = os.path.join(ASSETS_DIR, "anthropic_accenture.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 14, 28, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (20, 16, 32), (3, 7, 18))
    draw_grid(draw, (40, 32, 60))
    draw_radial_glow(img, (960, 480), 550, (217, 119, 6))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(15, 23, 42, 240), outline=(217, 119, 6), width=3)
    draw.text((360, 215), "AI SAFETY & RED-TEAMING • STRATEGIC ALLIANCE", fill=(251, 191, 36))
    draw.text((360, 265), "Anthropic & Accenture $1 Billion Joint Commitment (5-Year Plan)", fill=(255, 255, 255))

    draw.rounded_rectangle([260, 400, 920, 700], radius=16, fill=(24, 20, 36, 230), outline=(217, 119, 6), width=2)
    draw.text((290, 435), "EMBEDDED EVALUATORS", fill=(251, 191, 36))
    draw.text((290, 490), "• Dedicated on-site AI safety engineering squads", fill=(226, 232, 240))
    draw.text((290, 540), "• Real-time red-teaming against model injection", fill=(148, 163, 184))

    draw.rounded_rectangle([1000, 400, 1660, 700], radius=16, fill=(24, 20, 36, 230), outline=(168, 85, 247), width=2)
    draw.text((1030, 435), "THREAT INTELLIGENCE REPORT", fill=(192, 132, 252))
    draw.text((1030, 490), "• Neutralized multi-vector automated exploits", fill=(226, 232, 240))
    draw.text((1030, 540), "• Disrupted state-affiliated propaganda operations", fill=(148, 163, 184))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

def render_gemini_live_thinking():
    out_file = os.path.join(ASSETS_DIR, "gemini_live_thinking.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (6, 14, 28, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (8, 20, 42), (3, 7, 18))
    draw_grid(draw, (20, 40, 74))
    draw_radial_glow(img, (960, 480), 550, (66, 133, 244))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(15, 23, 42, 240), outline=(66, 133, 244), width=3)
    draw.text((360, 215), "MULTIMODAL REASONING & MACROECONOMICS • GOOGLE DEEPMIND", fill=(147, 197, 253))
    draw.text((360, 265), "Gemini 3.8 Live & Extended Thinking with Labor Market ATLAS", fill=(255, 255, 255))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

def render_nvidia_isaac_quantum():
    out_file = os.path.join(ASSETS_DIR, "nvidia_isaac_quantum.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 18, 12, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (12, 30, 18), (3, 7, 18))
    draw_grid(draw, (24, 60, 36))
    draw_radial_glow(img, (960, 480), 550, (118, 185, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(15, 23, 42, 240), outline=(118, 185, 0), width=3)
    draw.text((360, 215), "PHYSICAL AI & QUANTUM ACCELERATION • NVIDIA ARCHITECTURE", fill=(163, 230, 53))
    draw.text((360, 265), "Isaac ROS 5.0 Robotics OS & IonQ Quantum QPU Direct Integration", fill=(255, 255, 255))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

def render_senate_agent_probe():
    out_file = os.path.join(ASSETS_DIR, "senate_agent_probe.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (16, 14, 24, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (24, 18, 36), (4, 8, 18))
    draw_grid(draw, (44, 32, 64))
    draw_radial_glow(img, (960, 480), 550, (147, 51, 234))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(18, 20, 36, 240), outline=(168, 85, 247), width=3)
    draw.text((360, 215), "CONGRESSIONAL OVERSIGHT • AUTONOMOUS AGENT GOVERNANCE", fill=(216, 180, 254))
    draw.text((360, 265), "U.S. Senate Opens Inquiry into Incident Reporting & Agent Security", fill=(255, 255, 255))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

def render_india_sovereign_gpus():
    out_file = os.path.join(ASSETS_DIR, "india_sovereign_gpus.png")
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 14, 28, 255))
    draw = ImageDraw.Draw(img)
    create_cyber_gradient(draw, (24, 18, 14), (4, 8, 18))
    draw_grid(draw, (50, 36, 24))
    draw_radial_glow(img, (960, 480), 550, (249, 115, 22))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([320, 180, 1600, 340], radius=20, fill=(24, 18, 16, 240), outline=(249, 115, 22), width=3)
    draw.text((360, 215), "SOVEREIGN COMPUTE & NATIONAL AI INFRASTRUCTURE", fill=(251, 146, 60))
    draw.text((360, 265), "IndiaAI Surpasses 38,000 GPUs; Microsoft Formalizes Hyderabad Hub", fill=(255, 255, 255))

    img.convert("RGB").save(out_file)
    print(f"[+] Rendered {out_file}")

# Legacy renderers preserved for archive compatibility
def render_legacy_assets():
    from PIL import Image, ImageDraw
    # un_deepseek, claude_gpt6, etc.
    legacy_files = ["un_deepseek.png", "claude_gpt6_launch.png", "healthcare_openevidence.png", "youth_ai_safety.png", "alibaba_zhenwu_v900.png", "maharashtra_ai_governance.png"]
    for f in legacy_files:
        p = os.path.join(ASSETS_DIR, f)
        if not os.path.exists(p):
            im = Image.new("RGB", (WIDTH, HEIGHT), (10, 18, 30))
            im.save(p)

if __name__ == "__main__":
    render_gpt6_astra()
    render_anthropic_accenture()
    render_gemini_live_thinking()
    render_nvidia_isaac_quantum()
    render_senate_agent_probe()
    render_india_sovereign_gpus()
    render_legacy_assets()
    print("[+] All daily visual assets generated successfully!")
