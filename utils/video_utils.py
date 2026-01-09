"""
Утилиты для уникализации видео
"""

import subprocess
import random
import os
import json
from datetime import datetime, timedelta


def uniqualize_video(input_path, output_path, settings=None):
    """
    Уникализация видео с заданными настройками
    
    settings = {
        "fps_change": float,        # -2 до 2
        "resolution_change": float, # -10 до 10
        "tempo": float,             # -5 до 10
        "saturation": float,        # -5 до 5
        "contrast": float,          # -5 до 5
        "brightness": float,        # -5 до 5
        "border": int,              # 1 до 5
        "noise": float,             # 1 до 5
        "audio_tone": float,        # 1 до 5
        "audio_noise": float,       # 1 до 2
        "color_mixer": bool,
        "output_format": str        # mp4, avi, etc
    }
    """
    try:
        # Получаем информацию о видео
        probe_cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', input_path
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        video_info = json.loads(probe_result.stdout)
        
        # Получаем оригинальные параметры
        video_stream = None
        audio_stream = None
        for stream in video_info.get('streams', []):
            if stream['codec_type'] == 'video' and video_stream is None:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and audio_stream is None:
                audio_stream = stream
        
        if not video_stream:
            return False, "Видео поток не найден"
        
        orig_width = int(video_stream.get('width', 1920))
        orig_height = int(video_stream.get('height', 1080))
        orig_fps = eval(video_stream.get('r_frame_rate', '30/1'))
        
        # Применяем настройки или используем МИНИМАЛЬНЫЕ для скорости
        if settings is None:
            # Авто-настройки - ТОЛЬКО БЫСТРЫЕ ФИЛЬТРЫ
            settings = {
                "fps_change": 0,                                   # FPS: не меняем (медленно)
                "resolution_change": random.uniform(-3, 3),        # Разрешение: минимальное изменение
                "tempo": 1,                                        # Темп: не меняем (медленно)
                "saturation": 1 + random.uniform(0.01, 0.03),      # Насыщенность: минимум
                "contrast": 1 + random.uniform(0.01, 0.03),        # Контраст: минимум
                "brightness": random.uniform(-0.02, 0.02),         # Яркость: минимум
                "border": 0,                                       # Рамка: ОТКЛЮЧЕНА (медленно)
                "noise": 0,                                        # Шум: ОТКЛЮЧЕН (очень медленно)
                "audio_tone": 1,                                   # Тон аудио: не меняем
                "audio_noise": 0,
                "color_mixer": False,                              # Микшер цвета: ОТКЛЮЧЕН
                "output_format": "mp4",
                "bitrate_change": random.randint(-20, 20),
                "rotate": 0,
            }
        
        # Строим фильтры
        video_filters = []
        audio_filters = []
        
        # Изменение разрешения (максимум 720p для скорости)
        MAX_HEIGHT = 720
        res_change = settings.get("resolution_change", 0)
        if isinstance(res_change, tuple):
            res_change = random.uniform(res_change[0], res_change[1])
        scale_factor = 1 + (res_change / 100)
        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)
        
        # Ограничиваем до 720p если больше
        if new_height > MAX_HEIGHT:
            scale_ratio = MAX_HEIGHT / new_height
            new_height = MAX_HEIGHT
            new_width = int(new_width * scale_ratio)
        
        # Делаем четными (требование h264)
        new_width = new_width if new_width % 2 == 0 else new_width + 1
        new_height = new_height if new_height % 2 == 0 else new_height + 1
        video_filters.append(f"scale={new_width}:{new_height}")
        
        # Яркость, контраст, насыщенность
        brightness = settings.get("brightness", 0)
        if isinstance(brightness, tuple):
            brightness = random.uniform(brightness[0], brightness[1])
        brightness = brightness / 20  # Нормализуем
        
        contrast = settings.get("contrast", 1)
        if isinstance(contrast, tuple):
            contrast = random.uniform(contrast[0], contrast[1])
        if contrast > 1:
            contrast = 1 + (contrast - 1) / 10
        elif contrast < 1:
            contrast = 1 - (1 - contrast) / 10
        
        saturation = settings.get("saturation", 1)
        if isinstance(saturation, tuple):
            saturation = random.uniform(saturation[0], saturation[1])
        if saturation > 1:
            saturation = 1 + (saturation - 1) / 10
        elif saturation < 1:
            saturation = 1 - (1 - saturation) / 10
        
        video_filters.append(f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}")
        
        # Шум
        noise = settings.get("noise", 0)
        if isinstance(noise, tuple):
            noise = random.uniform(noise[0], noise[1])
        if noise > 0:
            noise_strength = int(noise * 2)
            video_filters.append(f"noise=alls={noise_strength}:allf=t")
        
        # Рамка (кроп + паддинг)
        border = settings.get("border", 0)
        if isinstance(border, tuple):
            border = random.randint(border[0], border[1])
        if border > 0:
            crop_pixels = border * 2
            video_filters.append(f"crop=iw-{crop_pixels}:ih-{crop_pixels}")
            video_filters.append(f"pad=iw+{crop_pixels}:ih+{crop_pixels}:(ow-iw)/2:(oh-ih)/2:black")
        
        # Цветовой микшер
        if settings.get("color_mixer", False):
            r_shift = random.uniform(0.98, 1.02)
            g_shift = random.uniform(0.98, 1.02)
            b_shift = random.uniform(0.98, 1.02)
            video_filters.append(f"colorbalance=rs={r_shift-1}:gs={g_shift-1}:bs={b_shift-1}")
        
        # Микро-поворот (важно для уникализации)
        rotate = settings.get("rotate", 0)
        if isinstance(rotate, tuple):
            rotate = random.uniform(rotate[0], rotate[1])
        if rotate != 0:
            # Поворот в радианах (очень маленький угол)
            rotate_rad = rotate * 0.0174533  # градусы в радианы
            video_filters.append(f"rotate={rotate_rad}:fillcolor=black")
        
        # Темп видео
        tempo = settings.get("tempo", 1)
        if isinstance(tempo, tuple):
            tempo = random.uniform(tempo[0], tempo[1])
        if tempo != 1:
            # Нормализуем tempo из диапазона настроек
            if tempo > 1:
                tempo = 1 + (tempo - 1) / 100
            else:
                tempo = 1 - (1 - tempo) / 100
            video_filters.append(f"setpts={1/tempo}*PTS")
        
        # Аудио фильтры
        if audio_stream:
            audio_tone = settings.get("audio_tone", 1)
            if isinstance(audio_tone, tuple):
                audio_tone = random.uniform(audio_tone[0], audio_tone[1])
            if audio_tone != 1:
                # Нормализуем
                if audio_tone > 1:
                    audio_tone = 1 + (audio_tone - 1) / 50
                else:
                    audio_tone = 1 - (1 - audio_tone) / 50
                audio_filters.append(f"asetrate=44100*{audio_tone},aresample=44100")
            
            if tempo != 1:
                audio_filters.append(f"atempo={tempo}")
        
        # Строим команду ffmpeg (МАКСИМАЛЬНАЯ СКОРОСТЬ)
        cmd = [
            'ffmpeg', '-y',
            '-threads', '0',           # Использовать все ядра CPU
            '-i', input_path
        ]
        
        # Видео фильтры
        if video_filters:
            cmd.extend(['-vf', ','.join(video_filters)])
        
        # Аудио фильтры
        if audio_filters:
            cmd.extend(['-af', ','.join(audio_filters)])
        
        # Изменение FPS
        fps_change = settings.get("fps_change", 0)
        if isinstance(fps_change, tuple):
            fps_change = random.uniform(fps_change[0], fps_change[1])
        new_fps = max(15, min(60, orig_fps + fps_change))
        cmd.extend(['-r', str(int(new_fps))])
        
        # Кодеки (МАКСИМАЛЬНАЯ СКОРОСТЬ)
        crf_value = 23 + random.randint(-2, 2)  # CRF 21-25 для уникальности
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'ultrafast',    # Самый быстрый пресет
            '-crf', str(crf_value),
        ])
        if audio_stream:
            audio_bitrate = 128 + random.randint(-16, 16)  # 112-144k
            cmd.extend(['-c:a', 'aac', '-b:a', f'{audio_bitrate}k'])
        
        # Метаданные (очищаем и добавляем новые случайные)
        cmd.extend(['-map_metadata', '-1'])
        
        # Случайная дата создания
        random_date = datetime.now() - timedelta(days=random.randint(1, 365), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        cmd.extend(['-metadata', f'creation_time={random_date.isoformat()}'])
        
        # Случайный энкодер
        encoders = ['Lavf58', 'Lavf59', 'Lavf60', 'HandBrake', 'FFmpeg', 'x264']
        encoder = random.choice(encoders) + f'{random.randint(1, 9)}.{random.randint(10, 99)}.{random.randint(100, 999)}'
        cmd.extend(['-metadata', f'encoder={encoder}'])
        
        # Случайный заголовок
        titles = ['Video', 'Movie', 'Clip', 'Recording', 'Film', '']
        title = random.choice(titles)
        if title:
            title += f'_{random.randint(1000, 9999)}'
            cmd.extend(['-metadata', f'title={title}'])
        
        # Случайный комментарий
        comments = ['', 'Processed', 'Edited', 'Converted', 'Exported']
        comment = random.choice(comments)
        if comment:
            cmd.extend(['-metadata', f'comment={comment}_{random.randint(100, 999)}'])
        
        # Выходной файл
        output_format = settings.get("output_format", "mp4")
        if not output_path.endswith(f'.{output_format}'):
            output_path = output_path.rsplit('.', 1)[0] + f'.{output_format}'
        
        cmd.append(output_path)
        
        # Выполняем (600 секунд = 10 минут для больших файлов)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0 and os.path.exists(output_path):
            return True, output_path
        else:
            return False, result.stderr[:500] if result.stderr else "Unknown error"
        
    except subprocess.TimeoutExpired:
        return False, "Превышено время обработки видео"
    except Exception as e:
        return False, str(e)


def download_tiktok_video(url, output_path):
    """Скачивание видео с TikTok через tikwm.com API"""
    import requests
    
    try:
        # API tikwm.com
        api_url = "https://www.tikwm.com/api/"
        params = {"url": url, "hd": 1}
        
        response = requests.get(api_url, params=params, timeout=30)
        data = response.json()
        
        if data.get("code") != 0:
            return False, data.get("msg", "Ошибка API")
        
        # Получаем ссылку на видео без водяного знака
        video_url = data.get("data", {}).get("play")
        if not video_url:
            video_url = data.get("data", {}).get("hdplay")
        
        if not video_url:
            return False, "Не удалось получить ссылку на видео"
        
        # Скачиваем видео
        video_response = requests.get(video_url, timeout=120)
        if video_response.status_code != 200:
            return False, f"Ошибка скачивания: {video_response.status_code}"
        
        # Сохраняем
        final_path = output_path if output_path.endswith('.mp4') else output_path + '.mp4'
        with open(final_path, 'wb') as f:
            f.write(video_response.content)
        
        return True, final_path
        
    except requests.Timeout:
        return False, "Превышено время ожидания"
    except Exception as e:
        return False, str(e)


def get_video_info(video_path):
    """Получение информации о видео"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    except:
        return None


# === Асинхронные обёртки для многопользовательского режима ===
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Пул потоков для тяжёлых операций (макс 10 одновременных видео)
_video_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix='video_')


async def uniqualize_video_async(input_path, output_path, settings=None):
    """Асинхронная уникализация видео"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _video_executor,
        uniqualize_video,
        input_path,
        output_path,
        settings
    )


async def download_tiktok_video_async(url, output_path):
    """Асинхронное скачивание TikTok"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _video_executor,
        download_tiktok_video,
        url,
        output_path
    )
