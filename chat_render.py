"""Render QQ faces and combined chat histories as a single supported image."""
import asyncio
from io import BytesIO
from pathlib import Path
import re

import aiohttp
from PIL import Image, ImageDraw, ImageFont

FACE_PATTERN = re.compile(r'<faceType=1,faceId="(\d+)",ext="[^"]*">|<emoji:(\d+)>|\[CQ:face,id=(\d+)\]')


def face_url(face_id):
    return f'https://qzonestyle.gtimg.cn/qzone/em/e{int(face_id)}@2x.gif'


def channel_content(content):
    return FACE_PATTERN.sub(lambda match: f'<emoji:{next(value for value in match.groups() if value)}>', content)


def load_font(size):
    for filename in (
        str(Path(__file__).parent / 'data' / 'chat-font.ttc'),
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        'C:/Windows/Fonts/msyh.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ):
        if Path(filename).exists():
            return ImageFont.truetype(filename, size)
    return ImageFont.load_default(size=size)


async def download_image(session, url):
    if not url.startswith(('https://', 'http://')):
        raise ValueError('图片地址无效')
    async with session.get(url) as response:
        response.raise_for_status()
        data = bytearray()
        async for chunk in response.content.iter_chunked(65536):
            data.extend(chunk)
            if len(data) > 8 * 1024 * 1024:
                raise ValueError('图片超过 8 MB')
    with Image.open(BytesIO(data)) as source:
        if source.width * source.height > 24000000:
            raise ValueError('图片尺寸过大')
        return source.convert('RGBA')


def render_records(records, images, merged=True):
    width, padding, line_height = 900, 32, 40
    font, small = load_font(25), load_font(20)
    canvas = Image.new('RGB', (width, 16000), '#f0f2f5')
    draw = ImageDraw.Draw(canvas)
    y = padding
    if merged:
        draw.text((padding, y), f'合并转发 · {len(records)} 条消息', font=font, fill='#303844')
        y += 60
    for record in records:
        if y > 14500:
            raise ValueError('合并内容过长，请减少所选消息')
        if merged:
            heading = f"{record['sender_name']}  {record.get('created_at', '').replace('T', ' ')[:19]}"
            draw.text((padding, y), heading[:55], font=small, fill='#657287')
            y += 35
        if record['content_type'] == 'image':
            image = images[record['content']].copy()
            image.thumbnail((width - padding * 2, 1600))
            if y + image.height > 15500:
                raise ValueError('合并图片过长，请减少所选消息')
            canvas.paste(image, (padding, y), image)
            y += image.height + 20
        else:
            text = record['content']
            parts, offset = [], 0
            for match in FACE_PATTERN.finditer(text):
                parts.extend(text[offset:match.start()])
                parts.append(('face', next(value for value in match.groups() if value)))
                offset = match.end()
            parts.extend(text[offset:])
            x = padding
            for part in parts:
                if y > 15500:
                    raise ValueError('合并内容过长，请减少所选消息')
                if isinstance(part, tuple):
                    image = images[face_url(part[1])].copy()
                    image.thumbnail((34, 34))
                    advance = 38
                else:
                    advance = draw.textlength(part, font=font)
                if part == '\n' or x + advance > width - padding:
                    x = padding
                    y += line_height
                    if part == '\n':
                        continue
                if isinstance(part, tuple):
                    canvas.paste(image, (int(x), y), image)
                else:
                    draw.text((x, y), part, font=font, fill='#17202e')
                x += advance
            y += line_height + 20
        if merged:
            draw.line((padding, y, width - padding, y), fill='#d9dee7')
            y += 20
    output = BytesIO()
    canvas.crop((0, 0, width, min(y + padding, 16000))).save(output, format='PNG')
    return output.getvalue()


def render_answer_image(text):
    width, padding, line_height = 900, 32, 40
    font, small, code_font = load_font(25), load_font(20), load_font(22)
    canvas = Image.new('RGB', (width, 16000), '#f0f2f5')
    draw = ImageDraw.Draw(canvas)
    y = padding
    in_code_block = False
    code_lines = []

    def flush_code_block():
        nonlocal code_lines, y
        if not code_lines:
            return
        block_height = len(code_lines) * (line_height + 4) + 16
        if y + block_height > 15500:
            raise ValueError('回答内容过长，无法渲染为图片')
        draw.rectangle((padding - 8, y - 4, width - padding + 8, y + block_height), fill='#2d333b')
        cy = y + 8
        for cline in code_lines:
            draw.text((padding + 8, cy), cline, font=code_font, fill='#e6edf3')
            cy += line_height + 4
        y += block_height + 20
        code_lines.clear()

    lines = text.split('\n')
    for line in lines:
        if y > 15500:
            raise ValueError('回答内容过长，无法渲染为图片')
        stripped = line.lstrip()
        if stripped.startswith('```'):
            if in_code_block:
                flush_code_block()
                in_code_block = False
            else:
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue
        if stripped.startswith('#'):
            heading_text = stripped.lstrip('#').strip()
            draw.text((padding, y), heading_text, font=small, fill='#17202e')
            y += line_height + 10
            draw.line((padding, y - 4, width - padding, y - 4), fill='#d9dee7')
            continue
        parts = []
        offset = 0
        code_pattern = re.compile(r'`([^`]+)`')
        for match in code_pattern.finditer(line):
            parts.append(('text', line[offset:match.start()]))
            parts.append(('code', match.group(1)))
            offset = match.end()
        parts.append(('text', line[offset:]))
        x = padding
        for part_type, part_text in parts:
            if y > 15500:
                raise ValueError('回答内容过长，无法渲染为图片')
            if part_type == 'code':
                text_width = draw.textlength(part_text, font=code_font)
                draw.rectangle((x - 4, y - 2, x + text_width + 4, y + line_height - 6), fill='#e8ecf1')
                draw.text((x, y), part_text, font=code_font, fill='#17202e')
                x += text_width + 8
            else:
                words = part_text.split(' ')
                for word in words:
                    if not word:
                        continue
                    advance = draw.textlength(word + ' ', font=font)
                    if x + advance > width - padding:
                        x = padding
                        y += line_height
                    draw.text((x, y), word + ' ', font=font, fill='#17202e')
                    x += advance
        y += line_height + 20
    if in_code_block:
        flush_code_block()
    output = BytesIO()
    canvas.crop((0, 0, width, min(y + padding, 16000))).save(output, format='PNG')
    return output.getvalue()


async def render_chat_image(records, merged=True):
    urls = set()
    for record in records:
        if record['content_type'] == 'image':
            urls.add(record['content'])
        else:
            for match in FACE_PATTERN.finditer(record['content']):
                urls.add(face_url(next(value for value in match.groups() if value)))
    images = {}
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        for url in urls:
            try:
                images[url] = await download_image(session, url)
            except Exception as error:
                raise ValueError('无法加载表情或消息图片，请检查资源后重试') from error
    return await asyncio.to_thread(render_records, records, images, merged)
