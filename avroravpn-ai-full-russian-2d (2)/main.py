import os, json, math, asyncio, subprocess, textwrap, random
from pathlib import Path
from datetime import datetime, timezone

import requests
from PIL import Image, ImageDraw, ImageFont
import edge_tts

ROOT = Path(__file__).parent
OUT = ROOT / "output"
WORK = ROOT / "work"
OUT.mkdir(exist_ok=True)
WORK.mkdir(exist_ok=True)

W, H, FPS = 720, 1280, 12
SCENES = 5
SECONDS_PER_SCENE = 4
FRAMES_PER_SCENE = FPS * SECONDS_PER_SCENE

def gemini_story():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("Не задан секрет GEMINI_API_KEY в GitHub Settings → Secrets and variables → Actions.")
    prompt = """
Напиши сценарий короткого оригинального доброго смешного 2D-мультика на русском языке,
длительность около 20 секунд, 5 сцен. Главные герои постоянные:
Бублик — круглый синий смешной персонаж, добрый и немного наивный;
Пиксель — маленький оранжевый робот, умный и энергичный.
Сюжет должен быть понятен за 20 секунд, с быстрым началом и шуткой в конце.
AvroraVPN упомяни естественно и ненавязчиво как спонсора/полезный сервис,
не обещай абсолютную анонимность, безопасность или обход блокировок.
Верни ТОЛЬКО JSON такого вида:
{"title":"...","scenes":[
{"speaker":"bublik","text":"короткая реплика до 12 слов","caption":"короткая надпись до 6 слов"},
{"speaker":"pixel","text":"...","caption":"..."},
{"speaker":"bublik","text":"...","caption":"..."},
{"speaker":"pixel","text":"...","caption":"..."},
{"speaker":"narrator","text":"...","caption":"..."}
]}
Все значения должны быть на русском. Ровно 5 сцен.
"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    r = requests.post(url, params={"key": key}, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.9, "responseMimeType": "application/json"}
    }, timeout=60)
    r.raise_for_status()
    raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    start, end = raw.find("{"), raw.rfind("}")
    data = json.loads(raw[start:end+1])
    if not isinstance(data.get("scenes"), list) or len(data["scenes"]) != SCENES:
        raise ValueError("Gemini вернул сценарий неправильного формата.")
    return data

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap_text(draw, text, fnt, max_width):
    words = str(text).split()
    lines, cur = [], ""
    for word in words:
        test = (cur + " " + word).strip()
        if draw.textbbox((0,0), test, font=fnt)[2] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines[:3]

def draw_character(draw, x, y, t, kind):
    bounce = int(math.sin(t * 5) * 13)
    y += bounce
    if kind == "bublik":
        color = (42, 142, 255)
        r = 112
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color, outline=(15,55,120), width=8)
        draw.ellipse((x-48, y-28, x-25, y-5), fill="white")
        draw.ellipse((x+25, y-28, x+48, y-5), fill="white")
        draw.ellipse((x-40, y-20, x-29, y-9), fill=(20,30,50))
        draw.ellipse((x+33, y-20, x+44, y-9), fill=(20,30,50))
        draw.arc((x-35,y+10,x+35,y+70), 0, 180, fill=(10,35,80), width=8)
    else:
        color = (255, 145, 48)
        draw.rounded_rectangle((x-88,y-105,x+88,y+105), radius=28, fill=color, outline=(130,65,15), width=8)
        draw.rounded_rectangle((x-58,y-55,x-12,y-8), radius=10, fill=(210,245,255))
        draw.rounded_rectangle((x+12,y-55,x+58,y-8), radius=10, fill=(210,245,255))
        draw.ellipse((x-43,y-45,x-25,y-25), fill=(15,45,65))
        draw.ellipse((x+25,y-45,x+43,y-25), fill=(15,45,65))
        draw.arc((x-35,y+5,x+35,y+55), 0, 180, fill=(110,45,10), width=7)
        draw.line((x,y-105,x,y-145), fill=(130,65,15), width=9)
        draw.ellipse((x-15,y-160,x+15,y-130), fill=(255,210,70), outline=(130,65,15), width=4)

def render_frame(scene, index, scene_i, title):
    t = index / FPS
    img = Image.new("RGB", (W,H), (18,24,54))
    d = ImageDraw.Draw(img)
    # colorful animated cartoon background
    for yy in range(H):
        k = yy/H
        col = (int(20+30*k), int(35+22*k), int(85+55*k))
        d.line((0,yy,W,yy), fill=col)
    # stars and floating bubbles
    for j in range(18):
        sx = (j*97 + index*3) % W
        sy = (j*173 + index*2) % H
        d.ellipse((sx,sy,sx+7,sy+7), fill=(120,180,255))
    d.ellipse((-100,850,820,1450), fill=(34,60,105))
    # scene characters
    if scene_i % 2 == 0:
        draw_character(d, 235, 650, t, "bublik")
        draw_character(d, 505, 690, t+0.7, "pixel")
    else:
        draw_character(d, 505, 650, t, "bublik")
        draw_character(d, 215, 690, t+0.7, "pixel")
    # top title
    d.rounded_rectangle((35,40,685,125), radius=24, fill=(8,14,38), outline=(100,150,255), width=3)
    d.text((60,63), title[:34], font=font(30, True), fill="white")
    # dialogue/caption panel
    caption = scene.get("caption") or scene.get("text","")
    lines = wrap_text(d, caption, font(34, True), 590)
    d.rounded_rectangle((35,950,685,1135), radius=30, fill=(5,10,28), outline=(255,255,255), width=3)
    yy = 985
    for line in lines:
        box = d.textbbox((0,0), line, font=font(34,True))
        d.text(((W-(box[2]-box[0]))/2, yy), line, font=font(34,True), fill="white")
        yy += 48
    d.text((42,1185), "AVRORAVPN", font=font(26,True), fill=(120,190,255))
    d.text((430,1185), f"{scene_i+1}/{SCENES}", font=font(24,True), fill=(220,230,255))
    return img

async def make_voice(text, speaker, path):
    voice = {
        "bublik": "ru-RU-DmitryNeural",
        "pixel": "ru-RU-SvetlanaNeural",
        "narrator": "ru-RU-DmitryNeural"
    }.get(str(speaker).lower(), "ru-RU-SvetlanaNeural")
    communicate = edge_tts.Communicate(text=str(text), voice=voice, rate="+8%")
    await communicate.save(str(path))

def run(cmd):
    subprocess.run(cmd, check=True)

def make_video(story):
    # clean work dir
    for p in WORK.glob("*"):
        if p.is_file(): p.unlink()
    clips = []
    for si, scene in enumerate(story["scenes"]):
        frame_dir = WORK / f"scene{si:02d}"
        frame_dir.mkdir(exist_ok=True)
        for fi in range(FRAMES_PER_SCENE):
            img = render_frame(scene, fi, si, story.get("title","Приключения Бублика и Пикселя"))
            img.save(frame_dir / f"frame{fi:04d}.png")
        audio = WORK / f"voice{si:02d}.mp3"
        asyncio.run(make_voice(scene.get("text",""), scene.get("speaker","narrator"), audio))
        clip = WORK / f"clip{si:02d}.mp4"
        run(["ffmpeg","-y","-loglevel","error","-framerate",str(FPS),"-i",str(frame_dir/"frame%04d.png"),
             "-i",str(audio),"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",
             "-shortest","-vf","scale=720:1280",str(clip)])
        clips.append(clip)
    concat_file = WORK / "concat.txt"
    concat_file.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final = OUT / f"avroravpn_{stamp}.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat_file),
         "-c","copy","-movflags","+faststart",str(final)])
    (OUT / f"avroravpn_{stamp}.txt").write_text(
        story.get("title","AvroraVPN cartoon") + "\n\n" +
        "\n".join(f'{s.get("speaker","")}: {s.get("text","")}' for s in story["scenes"]),
        encoding="utf-8"
    )
    return final

if __name__ == "__main__":
    random.seed()
    story = gemini_story()
    video = make_video(story)
    print(f"ГОТОВО: {video}")
