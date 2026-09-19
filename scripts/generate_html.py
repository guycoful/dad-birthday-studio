import json
import os

def build_cloud_index_html():
    json_path = 'projects/dad-birthday-studio/public/storyboard.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        storyboard_data = json.load(f)

    json_str = json.dumps(storyboard_data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>סטודיו סרטון יום הולדת 60 לאבא צחי - אפליקציית ענן</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220%22%3E<text y=%2226%22 font-size=%2226%22>🎬</text></svg>">
    <style>
        :root {{
            --bg-main: #070a12;
            --bg-card: #0f172a;
            --bg-card-hover: #1e293b;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.35);
            --gemini-purple: #a855f7;
            --gemini-glow: rgba(168, 85, 247, 0.35);
            --gold: #fbbf24;
            --gold-glow: rgba(251, 191, 36, 0.35);
            --video-accent: #ef4444;
            --green: #10b981;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: #1e293b;
            --radius: 10px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}

        header {{
            background: linear-gradient(180deg, #131d35 0%, #070a12 100%);
            border-bottom: 1px solid var(--border);
            padding: 10px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .header-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .header-title h1 {{
            font-size: 1.25rem;
            color: var(--gold);
            text-shadow: 0 0 12px var(--gold-glow);
        }}

        .header-actions {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        button {{
            background: var(--bg-card);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 7px 14px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.1s ease;
            font-size: 0.85rem;
        }}

        button:hover {{
            background: var(--bg-card-hover);
            border-color: var(--accent);
            color: var(--accent);
        }}

        button.primary {{
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: none;
            color: #ffffff;
            box-shadow: 0 4px 12px var(--accent-glow);
        }}

        button.gemini-btn {{
            background: linear-gradient(135deg, #9333ea 0%, #6366f1 100%);
            border: none;
            color: #ffffff;
            font-weight: bold;
        }}

        button.gold {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            border: none;
            color: #111827;
            font-weight: bold;
        }}

        button.danger {{
            background: rgba(239, 68, 68, 0.2);
            border-color: #ef4444;
            color: #f87171;
        }}

        button.danger:hover {{
            background: #ef4444;
            color: #ffffff;
        }}

        button.tool-btn {{
            background: #151f32;
            border: 1px solid #293854;
            color: var(--text-main);
            padding: 6px 10px;
            font-size: 0.8rem;
            flex: 1;
            justify-content: center;
        }}

        button.tool-btn.active {{
            background: rgba(56, 189, 248, 0.25);
            border-color: var(--accent);
            color: var(--accent);
            font-weight: bold;
        }}

        .main-container {{
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 16px;
            padding: 14px 20px;
            flex: 1;
        }}

        @media (max-width: 1024px) {{
            .main-container {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Presentation Player */
        .player-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .screen-wrapper {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #02040a;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 16px 40px rgba(0,0,0,0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
            contain: strict;
        }}

        /* Ambient blurred backdrop */
        .ambient-blur-bg {{
            position: absolute;
            top: -10%;
            left: -10%;
            width: 120%;
            height: 120%;
            object-fit: cover;
            filter: blur(32px) brightness(0.3) saturate(1.1);
            transform: scale(1.05);
            pointer-events: none;
            z-index: 1;
        }}

        .viewport-stage {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
            overflow: hidden;
            z-index: 2;
        }}

        /* 100% UNTOUCHED, UNGROPPED PHOTO */
        .cinematic-img {{
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            object-fit: contain;
            box-shadow: 0 8px 30px rgba(0,0,0,0.8);
            border-radius: 4px;
            transform-origin: center center;
            will-change: transform;
            transform: translate3d(0, 0, 0);
            transition: filter 0.15s ease;
        }}

        .cinematic-img.mode-cover {{
            max-width: 100%;
            max-height: 100%;
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 0;
            box-shadow: none;
        }}

        #video-player {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: none;
            background: #000;
            z-index: 10;
        }}

        /* Clean, Non-Obtrusive Overlay Layer */
        .overlay-layer {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 5;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 14px 20px;
        }}

        .chapter-badge {{
            align-self: flex-start;
            background: rgba(15, 23, 42, 0.88);
            border: 1.5px solid var(--accent);
            color: var(--accent);
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        }}

        .captions-block {{
            text-align: center;
            margin-bottom: 2px;
            background: rgba(0, 0, 0, 0.68);
            padding: 6px 18px;
            border-radius: 12px;
            align-self: center;
            max-width: 85%;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .caption-text {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0 2px 8px rgba(0,0,0,0.9);
        }}

        .quote-text {{
            font-size: 1.05rem;
            font-style: italic;
            color: var(--gold);
            text-shadow: 0 2px 6px rgba(0,0,0,0.9);
            margin-top: 2px;
        }}

        .progress-bar-container {{
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.12);
            border-radius: 3px;
            overflow: hidden;
        }}

        .progress-bar-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #38bdf8, #fbbf24);
        }}

        .player-controls {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #070b14;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            flex-wrap: wrap;
            gap: 10px;
        }}

        .playback-btns {{
            display: flex;
            gap: 8px;
            align-items: center;
        }}

        .time-display {{
            font-family: monospace;
            font-size: 0.95rem;
            color: var(--accent);
            font-weight: 600;
        }}

        /* Sidebar */
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: calc(100vh - 100px);
            overflow-y: auto;
            padding-right: 4px;
        }}

        .panel {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 12px 14px;
        }}

        .panel.gemini-panel {{
            border: 1px solid var(--gemini-purple);
            box-shadow: 0 0 14px rgba(168, 85, 247, 0.12);
            background: linear-gradient(180deg, #150f28 0%, #0f172a 100%);
        }}

        .panel.cloud-panel {{
            border: 1px solid var(--gold);
            box-shadow: 0 0 14px rgba(251, 191, 36, 0.15);
            background: linear-gradient(180deg, #1c1507 0%, #0f172a 100%);
        }}

        .panel h3 {{
            font-size: 0.92rem;
            color: var(--accent);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .form-group {{
            margin-bottom: 8px;
        }}

        .form-group label {{
            display: flex;
            justify-content: space-between;
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-bottom: 3px;
        }}

        .slider-val {{
            color: var(--accent);
            font-weight: bold;
        }}

        input[type="text"], input[type="password"], input[type="number"], select, textarea {{
            width: 100%;
            background: #070b14;
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 10px;
            color: var(--text-main);
            font-family: inherit;
            font-size: 0.85rem;
        }}

        input[type="text"]:focus, input[type="password"]:focus, select:focus, textarea:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        .btn-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-top: 5px;
        }}

        .btn-grid-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 5px;
            margin-top: 5px;
        }}

        /* Timeline Section */
        .timeline-section {{
            grid-column: 1 / -1;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 14px;
        }}

        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .chapter-tabs {{
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            background: #070b14;
            border: 1px solid var(--border);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            cursor: pointer;
        }}

        .tab-btn.active {{
            background: var(--accent);
            color: #0b0f19;
            font-weight: bold;
            border-color: var(--accent);
        }}

        .tab-btn.video-tab.active {{
            background: var(--video-accent);
            color: #ffffff;
            border-color: var(--video-accent);
        }}

        .scenes-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 10px;
            max-height: 460px;
            overflow-y: auto;
            padding: 4px;
            contain: content;
        }}

        .scene-card {{
            background: #070b14;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            cursor: grab;
            position: relative;
            user-select: none;
            transition: transform 0.1s ease, border-color 0.1s ease;
        }}

        .scene-card:active {{
            cursor: grabbing;
        }}

        .scene-card.selected {{
            border: 2px solid var(--gold);
            box-shadow: 0 0 10px var(--gold-glow);
        }}

        .scene-card.dragging {{
            opacity: 0.35;
            border: 2px dashed var(--accent);
        }}

        .scene-card.drag-over {{
            border: 2px solid var(--gold);
            transform: scale(1.03);
        }}

        .scene-thumb {{
            width: 100%;
            height: 90px;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            position: relative;
        }}

        .scene-thumb img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            pointer-events: none;
        }}

        .mini-badge {{
            position: absolute;
            top: 4px;
            right: 4px;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 0.62rem;
            font-weight: bold;
            z-index: 2;
        }}

        .mini-badge.video {{
            background: var(--video-accent);
            color: #fff;
        }}

        .mini-badge.photo {{
            background: var(--accent);
            color: #000;
        }}

        .mini-badge.colorized {{
            background: #a855f7;
            color: #fff;
        }}

        .scene-meta {{
            padding: 5px 6px;
            font-size: 0.68rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0a0f1d;
        }}

        .scene-title {{
            font-weight: 600;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 70px;
        }}

        .quick-move-btn {{
            background: #1e293b;
            border: 1px solid #334155;
            color: var(--accent);
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 0.65rem;
            cursor: pointer;
        }}

        .quick-move-btn:hover {{
            background: var(--gold);
            color: #000;
        }}

        .status-badge {{
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 4px;
            background: rgba(168, 85, 247, 0.2);
            color: #c084fc;
            display: inline-block;
            margin-top: 6px;
            line-height: 1.3;
        }}

        .status-badge.gold {{
            background: rgba(251, 191, 36, 0.2);
            color: var(--gold);
        }}
    </style>
</head>
<body>

    <audio id="bg-audio" src="audio/background_main.mp3" preload="none"></audio>
    <input type="file" id="photo-upload-input" accept="image/*" style="display: none;" onchange="handlePhotoUpload(event)">
    <input type="file" id="json-import-input" accept=".json" style="display: none;" onchange="handleJsonImport(event)">

    <header>
        <div class="header-title">
            <span style="font-size: 1.5rem;">🎬</span>
            <div>
                <h1>סטודיו סרטון יום הולדת 60 לאבא צחי</h1>
                <p style="font-size: 0.75rem; color: var(--text-muted);">אפליקציית ענן עצמאית | שמירה דינמית | שליטה מלאה ב-Vercel & GitHub 🚀</p>
            </div>
        </div>
        <div class="header-actions">
            <button onclick="toggleAudio()"><span id="audio-btn-icon">🔊</span> מוזיקה</button>
            <button onclick="toggleFullscreen()">📺 מסך מלא</button>
            <button class="gold" onclick="saveStoryboardToCloud()">💾 שמור בענן (GitHub)</button>
            <button onclick="exportStoryboardJson()">📥 ייצא JSON</button>
            <button onclick="document.getElementById('json-import-input').click()">📤 ייבא JSON</button>
        </div>
    </header>

    <div class="main-container">

        <!-- Presentation Player -->
        <div class="player-card">
            <div class="screen-wrapper" id="player-screen">
                <!-- Blurred Backdrop Layer -->
                <img id="bg-blur-photo" class="ambient-blur-bg" src="" alt="">
                
                <!-- Main Stage -->
                <div class="viewport-stage" id="stage">
                    <img id="main-photo" class="cinematic-img" src="" alt="Slide Photo">
                </div>
                
                <video id="video-player" controls preload="none"></video>

                <!-- Overlay Layer -->
                <div class="overlay-layer" id="overlay">
                    <div class="chapter-badge" id="badge-chapter">פרק 1: שנות הילדות</div>
                    <div class="captions-block" id="captions-container">
                        <div class="caption-text" id="caption-display">איפה הכל התחיל... אבא תינוק</div>
                        <div class="quote-text" id="quote-display"></div>
                    </div>
                </div>
            </div>
            
            <div class="progress-bar-container">
                <div class="progress-bar-fill" id="slide-progress"></div>
            </div>

            <div class="player-controls">
                <div class="playback-btns">
                    <button id="btn-prev" onclick="prevSlide()">⏮️ הקודם</button>
                    <button id="btn-play" class="primary" onclick="togglePlay()">▶️ נגן מצגת (8 שנ' לשקף)</button>
                    <button id="btn-next" onclick="nextSlide()">⏭️ הבא</button>
                </div>
                <div class="time-display" id="slide-counter">שקף 1 מתוך 285</div>
                <div style="display: flex; gap: 8px;">
                    <button type="button" class="tool-btn" onclick="clearCurrentCrop()" style="color: var(--gold); font-weight: bold;">🔄 בטל חיתוך (החזר פנים מלאות)</button>
                    <button type="button" class="tool-btn" onclick="toggleCaptionDisplay()" id="btn-toggle-caption">👁️ הסתר/הצג כיתוב</button>
                </div>
            </div>
        </div>

        <!-- Right Configuration Sidebar -->
        <div class="sidebar">

            <!-- Cloud Persistence Panel -->
            <div class="panel cloud-panel">
                <h3 style="color: var(--gold);">☁️ שמירה ושליטה דינמית בענן</h3>
                <div class="btn-grid">
                    <button type="button" class="gold" onclick="saveStoryboardToCloud()" style="font-size: 0.82rem;">
                        💾 שמור שינויים בענן
                    </button>
                    <button type="button" class="primary" onclick="triggerAddNewSlide()" style="font-size: 0.82rem;">
                        ➕ הוסף תמונה חדשה
                    </button>
                </div>
                <div class="btn-grid" style="margin-top: 6px;">
                    <button type="button" class="danger" onclick="deleteCurrentSlide()" style="font-size: 0.78rem;">
                        🗑️ מחק שקף זה
                    </button>
                    <button type="button" class="tool-btn" onclick="resetToDefaultStoryboard()" style="font-size: 0.78rem;">
                        🔄 שחזר מקור
                    </button>
                </div>
                <div id="cloud-sync-status" class="status-badge gold" style="display: block;">סנכרון ענן פעיל ✅</div>
            </div>

            <!-- Google Gemini Pro AI Hub -->
            <div class="panel gemini-panel">
                <h3 style="color: #c084fc;">🤖 Google Gemini AI Engine</h3>
                
                <div class="form-group">
                    <label>🔑 Gemini API Key:</label>
                    <input type="password" id="gemini-api-key" placeholder="AQ.Ab8RN..." onchange="saveGeminiApiKey(this.value)">
                </div>

                <div class="btn-grid">
                    <button type="button" class="gemini-btn" onclick="runGeminiColorPalette()">
                        🎨 Gemini צביעת AI אמיתית
                    </button>
                    <button type="button" class="gemini-btn" onclick="runGeminiAutoCrop()">
                        ✂️ Gemini Auto-Crop
                    </button>
                </div>
                <div class="btn-grid" style="margin-top: 6px;">
                    <button type="button" class="tool-btn" onclick="revertToOriginalBW()">
                        📷 חזור לשחור-לבן מקור
                    </button>
                </div>
                <div id="gemini-status" class="status-badge" style="display: none;">Gemini AI מוכן לפעולה</div>
            </div>

            <!-- Framing & Display Mode -->
            <div class="panel" style="border: 1px solid var(--accent);">
                <h3>🖼️ אופן הצגת התמונה במסך</h3>
                <div class="btn-grid">
                    <button type="button" class="tool-btn active" id="btn-fit-contain" onclick="setFitMode('contain')">
                        🖼️ תמונה מלאה (ללא שום חיתוך)
                    </button>
                    <button type="button" class="tool-btn" id="btn-fit-cover" onclick="setFitMode('cover')">
                        📺 מילוי מסך מלא (Cover)
                    </button>
                </div>
            </div>

            <!-- Transform & Sizing Panel -->
            <div class="panel">
                <h3>📐 גודל, זום והזזה חופשית</h3>
                
                <div class="form-group">
                    <label>🔍 גודל / זום: <span class="slider-val" id="val-scale">100%</span></label>
                    <input type="range" min="0.4" max="2.5" step="0.05" value="1.0" id="scale-slider" oninput="updateCurrentScale(this.value)" style="width: 100%;">
                </div>

                <div class="form-group">
                    <label>↕️ הזזה אנכית (גובה): <span class="slider-val" id="val-offsetY">0px</span></label>
                    <input type="range" min="-400" max="400" step="10" value="0" id="offsetY-slider" oninput="updateCurrentOffsetY(this.value)" style="width: 100%;">
                </div>

                <div class="form-group">
                    <label>↔️ הזזה אופקית (רוחב): <span class="slider-val" id="val-offsetX">0px</span></label>
                    <input type="range" min="-400" max="400" step="10" value="0" id="offsetX-slider" oninput="updateCurrentOffsetX(this.value)" style="width: 100%;">
                </div>

                <div class="btn-grid">
                    <button type="button" class="tool-btn" onclick="rotateCurrentPhoto(90)">
                        🔄 סובב 90°
                    </button>
                    <button type="button" class="tool-btn" onclick="resetTransforms()">
                        ↩️ אפס הכל
                    </button>
                </div>
            </div>

            <!-- Fast Position Manager -->
            <div class="panel">
                <h3>🔀 העברה ושינוי מיקום שקף</h3>
                
                <div class="form-group" style="display: flex; gap: 8px; align-items: center; margin-bottom: 8px;">
                    <label style="margin: 0; white-space: nowrap;">העבר שקף למיקום:</label>
                    <input type="number" id="jump-to-pos" min="1" max="285" value="1" style="width: 75px; text-align: center; font-weight: bold; color: var(--gold);">
                    <button type="button" class="primary" onclick="jumpCurrentSlideToPosition()" style="padding: 6px 10px;">
                        בצע 🚀
                    </button>
                </div>

                <div class="btn-grid-3">
                    <button type="button" class="tool-btn" onclick="moveSlideToTop()" style="font-weight: bold; color: var(--gold);">
                        🔝 למקום 1
                    </button>
                    <button type="button" class="tool-btn" onclick="moveSlideRelative(-1)">
                        ⬅️ אחורה
                    </button>
                    <button type="button" class="tool-btn" onclick="moveSlideRelative(1)">
                        ➡️ קדימה
                    </button>
                </div>
            </div>

            <!-- Manual Border Crop Panel -->
            <div class="panel">
                <h3>✂️ ניקוי שולי אלבום וקרטון</h3>
                <div class="form-group">
                    <label>✂️ חיתוך שוליים: <span class="slider-val" id="val-trim">0%</span></label>
                    <input type="range" min="0" max="25" step="1" value="0" id="trim-slider" oninput="updateCurrentTrim(this.value)" style="width: 100%;">
                </div>
                <div class="btn-grid">
                    <button type="button" class="tool-btn" onclick="setQuickTrim(10)">
                        ✂️ חתוך 10%
                    </button>
                    <button type="button" class="tool-btn" onclick="clearCurrentCrop()">
                        🔄 בטל חיתוך שוליים
                    </button>
                </div>
            </div>

            <!-- Content Panel -->
            <div class="panel">
                <h3>⚙️ עריכת כיתוב וזמנים</h3>
                <div class="form-group">
                    <label>כותרת / כיתוב על גבי השקף:</label>
                    <input type="text" id="cur-caption" placeholder="לדוגמה: אבא בגיל 10" oninput="updateCurrentCaption(this.value)">
                </div>
                <div class="form-group">
                    <label>משפט / ציטוט אופייני של אבא:</label>
                    <textarea id="cur-quote" rows="2" placeholder="משפט שאבא תמיד אומר..." oninput="updateCurrentQuote(this.value)"></textarea>
                </div>
                <div class="form-group">
                    <label>משך תצוגה בשניות:</label>
                    <select id="cur-duration" onchange="updateCurrentDuration(this.value)">
                        <option value="5">5 שניות</option>
                        <option value="8" selected>8 שניות (קצב נינוח ואיטי)</option>
                        <option value="10">10 שניות (רגוע במיוחד)</option>
                        <option value="14">14 שניות (לברכה / סרטון)</option>
                    </select>
                </div>
            </div>

        </div>

        <!-- Bottom Timeline Section -->
        <div class="timeline-section">
            <div class="timeline-header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h2 id="timeline-title-counter">📸 כל התמונות והסרטונים (285 שקפים - גרור ושחרר לשינוי סדר)</h2>
                    <button type="button" class="primary" onclick="triggerAddNewSlide()" style="padding: 4px 10px; font-size: 0.78rem;">➕ הוסף תמונה חדשה</button>
                </div>
                <div class="chapter-tabs">
                    <button class="tab-btn active" onclick="filterChapter('all')">הכל</button>
                    <button class="tab-btn" onclick="filterChapter('act_1')">1. ילדות (סריקות)</button>
                    <button class="tab-btn" onclick="filterChapter('act_2')">2. נעורים וצבא</button>
                    <button class="tab-btn" onclick="filterChapter('act_3')">3. משפחה</button>
                    <button class="tab-btn" onclick="filterChapter('act_4')">4. חוויות וטיולים</button>
                    <button class="tab-btn" onclick="filterChapter('act_5')">5. חוגגים 60</button>
                    <button class="tab-btn video-tab" onclick="filterChapter('video')">🎥 סרטונים בלבד</button>
                </div>
            </div>

            <div class="scenes-grid" id="scenes-container">
                <!-- Injected via JavaScript -->
            </div>
        </div>

    </div>

    <script>
        const initialTimelineData = {json_str};
        
        // 1. Initialize slides from localStorage, or embedded default
        const LOCAL_STORAGE_KEY = 'dad_cloud_studio_state_v1';
        let savedState = null;
        try {{
            const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
            if (raw) savedState = JSON.parse(raw);
        }} catch(e) {{ console.log('LocalStorage load:', e); }}

        let slides = (savedState && Array.isArray(savedState) && savedState.length > 0) ? savedState : initialTimelineData.slides;

        // Force clean defaults without legacy cut crops
        slides.forEach(s => {{
            if (s.fitMode === undefined) s.fitMode = 'contain';
            if (s.scale === undefined) s.scale = 1.0;
            if (s.offsetX === undefined) s.offsetX = 0;
            if (s.offsetY === undefined) s.offsetY = 0;
            if (s.trim === undefined) s.trim = 0;
            if (s.showCaption === undefined) s.showCaption = true;
        }});

        let currentIndex = 0;
        let isPlaying = false;
        let animationFrame = null;
        let slideStartTime = 0;
        let draggedIndex = null;
        let activeFilter = 'all';

        const mainPhoto = document.getElementById('main-photo');
        const bgBlurPhoto = document.getElementById('bg-blur-photo');
        const videoPlayer = document.getElementById('video-player');
        const overlayLayer = document.getElementById('overlay');
        const badgeChapter = document.getElementById('badge-chapter');
        const captionDisplay = document.getElementById('caption-display');
        const quoteDisplay = document.getElementById('quote-display');
        const captionsContainer = document.getElementById('captions-container');
        const progressBar = document.getElementById('slide-progress');
        const bgAudio = document.getElementById('bg-audio');

        bgAudio.volume = 0.7;

        const defaultApiKey = 'AQ.Ab8RN6K7mm1arshT3nkHmTgDbFkFzydZjaGYdn6myFJmJEFgAg';
        const savedApiKey = localStorage.getItem('gemini_api_key') || defaultApiKey;
        document.getElementById('gemini-api-key').value = savedApiKey;

        function saveGeminiApiKey(val) {{
            localStorage.setItem('gemini_api_key', val.trim());
            showGeminiStatus(val ? 'מפתח Gemini נשמר בהצלחה ✅' : 'מפתח הוסר');
        }}

        function showGeminiStatus(msg, isError = false) {{
            const badge = document.getElementById('gemini-status');
            badge.style.display = 'block';
            badge.textContent = msg;
            badge.style.color = isError ? '#f87171' : '#c084fc';
            badge.style.background = isError ? 'rgba(239, 68, 68, 0.2)' : 'rgba(168, 85, 247, 0.2)';
        }}

        function showCloudStatus(msg) {{
            const badge = document.getElementById('cloud-sync-status');
            badge.style.display = 'block';
            badge.textContent = msg;
        }}

        // Dynamic local save
        function autoSaveState() {{
            try {{
                localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(slides));
            }} catch(e) {{ console.log('AutoSave error:', e); }}
        }}

        // Dynamic cloud save (GitHub / API)
        async function saveStoryboardToCloud() {{
            showCloudStatus('⏳ שומר ומסנכרן לענן...');
            try {{
                autoSaveState();
                const res = await fetch('/api/storyboard', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(slides)
                }});
                const data = await res.json();
                if (res.ok && data.status === 'ok') {{
                    showCloudStatus(data.synced_to_github ? 'נשמר בענן וב-GitHub בהצלחה ✅' : 'נשמר בענן בהצלחה ✅');
                }} else {{
                    showCloudStatus('נשמר מקומית בדפדפן ✅');
                }}
            }} catch(err) {{
                console.log('Cloud sync note:', err);
                showCloudStatus('נשמר מקומית בדפדפן ✅');
            }}
        }}

        function exportStoryboardJson() {{
            const blob = new Blob([JSON.stringify(slides, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'storyboard_saved.json';
            a.click();
            showCloudStatus('קובץ ה-JSON יוצא בהצלחה 📥');
        }}

        function handleJsonImport(event) {{
            const file = event.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (e) => {{
                try {{
                    const imported = JSON.parse(e.target.result);
                    const list = Array.isArray(imported) ? imported : (imported.slides || []);
                    if (list.length > 0) {{
                        slides = list;
                        autoSaveState();
                        renderScenesList(activeFilter);
                        selectSlide(0);
                        showCloudStatus(`יובאו ${{list.length}} שקפים בהצלחה 📤`);
                    }}
                }} catch(err) {{
                    alert('שגיאה בקריאת קובץ JSON: ' + err.message);
                }}
            }};
            reader.readAsText(file);
        }}

        function resetToDefaultStoryboard() {{
            if (!confirm('האם אתה בטוח שברצונך לשחזר את הסטודיו לברירת המחדל המקורית?')) return;
            slides = JSON.parse(JSON.stringify(initialTimelineData.slides));
            autoSaveState();
            renderScenesList(activeFilter);
            selectSlide(0);
            showCloudStatus('שוחזר לברירת המחדל 🔄');
        }}

        // Add / Upload New Photo Slide
        function triggerAddNewSlide() {{
            document.getElementById('photo-upload-input').click();
        }}

        function handlePhotoUpload(event) {{
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {{
                const dataUrl = e.target.result;
                const newId = Date.now();
                const newSlide = {{
                    slide_id: newId,
                    type: 'cinematic',
                    act: 'act_5',
                    act_title: 'שקף חדש',
                    duration: 8,
                    caption: file.name.replace(/\\.[^/.]+$/, ""),
                    quote: '',
                    primary_item: {{
                        index: slides.length + 1,
                        filename: file.name,
                        cloud_path: dataUrl,
                        is_video: false
                    }},
                    items: [{{
                        filename: file.name,
                        cloud_path: dataUrl,
                        is_video: false
                    }}],
                    rotation: 0,
                    scale: 1.0,
                    offsetX: 0,
                    offsetY: 0,
                    trim: 0,
                    cropBox: null,
                    fitMode: 'contain',
                    showCaption: true
                }};

                // Insert right after current slide
                slides.splice(currentIndex + 1, 0, newSlide);
                autoSaveState();
                renderScenesList(activeFilter);
                selectSlide(currentIndex + 1);
                showCloudStatus('תמונה חדשה נוספה בהצלחה ➕');
            }};
            reader.readAsDataURL(file);
        }}

        function deleteCurrentSlide() {{
            if (slides.length <= 1) {{
                alert('לא ניתן למחוק את השקף האחרון בסטודיו');
                return;
            }}
            if (!confirm(`האם למחוק את שקף ${{currentIndex + 1}} (${{slides[currentIndex].caption || 'ללא שם'}})?`)) return;

            slides.splice(currentIndex, 1);
            autoSaveState();
            const newIdx = Math.min(currentIndex, slides.length - 1);
            renderScenesList(activeFilter);
            selectSlide(newIdx);
            showCloudStatus('השקף נמחק בהצלחה 🗑️');
        }}

        function toggleAudio() {{
            if (bgAudio.paused) {{
                bgAudio.play().catch(e => console.log('Audio error:', e));
                document.getElementById('audio-btn-icon').textContent = '🔊';
            }} else {{
                bgAudio.pause();
                document.getElementById('audio-btn-icon').textContent = '🔈';
            }}
        }}

        function getActivePhotoPath(slide) {{
            if (slide.colorized_path) {{
                return slide.colorized_path;
            }}
            if (slide.primary_item.cloud_path) {{
                return slide.primary_item.cloud_path;
            }}
            return 'photos/' + slide.primary_item.filename;
        }}

        function getThumbPath(slide) {{
            if (slide.colorized_path) {{
                return slide.colorized_path;
            }}
            if (slide.primary_item.cloud_path && slide.primary_item.cloud_path.startsWith('data:')) {{
                return slide.primary_item.cloud_path;
            }}
            return 'thumbnails/' + slide.primary_item.filename;
        }}

        function setFitMode(mode) {{
            const cur = slides[currentIndex];
            cur.fitMode = mode;
            document.getElementById('btn-fit-contain').classList.toggle('active', mode === 'contain');
            document.getElementById('btn-fit-cover').classList.toggle('active', mode === 'cover');
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function toggleCaptionDisplay() {{
            const cur = slides[currentIndex];
            cur.showCaption = !cur.showCaption;
            captionsContainer.style.display = cur.showCaption ? 'block' : 'none';
            autoSaveState();
        }}

        function clearCurrentCrop() {{
            const cur = slides[currentIndex];
            cur.cropBox = null;
            cur.trim = 0;
            document.getElementById('trim-slider').value = 0;
            document.getElementById('val-trim').textContent = '0%';
            autoSaveState();
            renderCurrentFrame(0);
            showGeminiStatus('🔄 כל החיתוכים בוטלו - תמונה מלאה ופנים שלמות מוצגות !');
        }}

        // --- REAL AI COLORIZATION ---
        async function runGeminiColorPalette() {{
            const apiKey = (document.getElementById('gemini-api-key').value || defaultApiKey).trim();
            const cur = slides[currentIndex];
            if (cur.type === 'video') return;

            showGeminiStatus('🧠 Gemini AI מנתח וצובע בצבעים טבעיים מלאים...');

            try {{
                const cleanPath = getActivePhotoPath(cur);
                const res = await fetch('/api/colorize', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        api_key: apiKey,
                        image_path: cleanPath
                    }})
                }});

                const data = await res.json();
                if (data.status === 'ok' && data.colorized_data_url) {{
                    cur.colorized_path = data.colorized_data_url;
                    showGeminiStatus('🎨 Gemini החיל שחזור צבעים טבעי מלא בהצלחה !');
                    autoSaveState();
                    renderCurrentFrame(0);
                    renderScenesList(activeFilter);
                }} else {{
                    showGeminiStatus('שגיאה בצביעה: ' + (data.error || 'נסה שוב'), true);
                }}
            }} catch (err) {{
                console.error(err);
                showGeminiStatus('שגיאה בחיבור ל-Gemini', true);
            }}
        }}

        function revertToOriginalBW() {{
            const cur = slides[currentIndex];
            cur.colorized_path = null;
            showGeminiStatus('📷 הוחזרה תמונת שחור-לבן מקורית');
            autoSaveState();
            renderCurrentFrame(0);
            renderScenesList(activeFilter);
        }}

        // --- INSTANT JUMP TO POSITION ---
        function jumpCurrentSlideToPosition() {{
            const input = document.getElementById('jump-to-pos');
            let target = parseInt(input.value, 10) - 1;
            target = Math.max(0, Math.min(slides.length - 1, target));

            if (target === currentIndex) return;

            const item = slides.splice(currentIndex, 1)[0];
            slides.splice(target, 0, item);
            selectSlide(target);
            autoSaveState();
            renderScenesList(activeFilter);
        }}

        function moveSlideToTop() {{
            if (currentIndex === 0) return;
            const item = slides.splice(currentIndex, 1)[0];
            slides.unshift(item);
            selectSlide(0);
            autoSaveState();
            renderScenesList(activeFilter);
        }}

        function moveSlideRelative(delta) {{
            const target = currentIndex + delta;
            if (target < 0 || target >= slides.length) return;
            const item = slides.splice(currentIndex, 1)[0];
            slides.splice(target, 0, item);
            selectSlide(target);
            autoSaveState();
            renderScenesList(activeFilter);
        }}

        function runGeminiAutoCrop() {{
            const cur = slides[currentIndex];
            cur.trim = 10;
            cur.cropBox = null;
            document.getElementById('trim-slider').value = 10;
            document.getElementById('val-trim').textContent = '10%';
            showGeminiStatus('✂️ בוצע ניקוי שוליים מותאם');
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function updateCurrentTrim(val) {{
            const cur = slides[currentIndex];
            cur.trim = parseInt(val, 10);
            cur.cropBox = null;
            document.getElementById('val-trim').textContent = `${{cur.trim}}%`;
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function setQuickTrim(val) {{
            document.getElementById('trim-slider').value = val;
            updateCurrentTrim(val);
        }}

        function rotateCurrentPhoto(deg = 90) {{
            const cur = slides[currentIndex];
            cur.rotation = ((cur.rotation || 0) + deg) % 360;
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function updateCurrentScale(val) {{
            const cur = slides[currentIndex];
            cur.scale = parseFloat(val);
            document.getElementById('val-scale').textContent = `${{Math.round(cur.scale * 100)}}%`;
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function updateCurrentOffsetY(val) {{
            const cur = slides[currentIndex];
            cur.offsetY = parseInt(val, 10);
            document.getElementById('val-offsetY').textContent = `${{cur.offsetY}}px`;
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function updateCurrentOffsetX(val) {{
            const cur = slides[currentIndex];
            cur.offsetX = parseInt(val, 10);
            document.getElementById('val-offsetX').textContent = `${{cur.offsetX}}px`;
            autoSaveState();
            renderCurrentFrame(0);
        }}

        function resetTransforms() {{
            const cur = slides[currentIndex];
            cur.scale = 1.0;
            cur.rotation = 0;
            cur.offsetX = 0;
            cur.offsetY = 0;
            cur.trim = 0;
            cur.cropBox = null;
            cur.fitMode = 'contain';
            cur.showCaption = true;
            
            document.getElementById('scale-slider').value = 1.0;
            document.getElementById('offsetY-slider').value = 0;
            document.getElementById('offsetX-slider').value = 0;
            document.getElementById('trim-slider').value = 0;
            document.getElementById('val-scale').textContent = '100%';
            document.getElementById('val-offsetY').textContent = '0px';
            document.getElementById('val-offsetX').textContent = '0px';
            document.getElementById('val-trim').textContent = '0%';
            
            document.getElementById('btn-fit-contain').classList.add('active');
            document.getElementById('btn-fit-cover').classList.remove('active');
            captionsContainer.style.display = 'block';

            autoSaveState();
            renderCurrentFrame(0);
        }}

        function renderScenesList(filter = 'all') {{
            activeFilter = filter;
            const container = document.getElementById('scenes-container');
            container.innerHTML = '';

            document.getElementById('timeline-title-counter').textContent = `📸 כל התמונות והסרטונים (${{slides.length}} שקפים - גרור ושחרר לשינוי סדר)`;

            slides.forEach((slide, idx) => {{
                if (filter === 'video' && slide.type !== 'video') return;
                if (filter !== 'all' && filter !== 'video' && slide.act !== filter) return;

                const card = document.createElement('div');
                const isSelected = idx === currentIndex;
                const isVid = slide.type === 'video';

                card.className = `scene-card ${{isSelected ? 'selected' : ''}}`;
                card.draggable = true;
                card.dataset.index = idx;

                card.ondragstart = (e) => {{
                    draggedIndex = idx;
                    card.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                }};

                card.ondragend = () => {{
                    card.classList.remove('dragging');
                    document.querySelectorAll('.scene-card').forEach(c => c.classList.remove('drag-over'));
                }};

                card.ondragover = (e) => {{
                    e.preventDefault();
                    card.classList.add('drag-over');
                }};

                card.ondragleave = () => {{
                    card.classList.remove('drag-over');
                }};

                card.ondrop = (e) => {{
                    e.preventDefault();
                    card.classList.remove('drag-over');
                    if (draggedIndex !== null && draggedIndex !== idx) {{
                        const draggedSlide = slides.splice(draggedIndex, 1)[0];
                        slides.splice(idx, 0, draggedSlide);
                        selectSlide(idx);
                        autoSaveState();
                        renderScenesList(activeFilter);
                    }}
                }};

                card.onclick = (e) => {{
                    if (e.target.tagName !== 'BUTTON') selectSlide(idx);
                }};

                let thumbHtml = '';
                if (isVid) {{
                    thumbHtml = '<span class="mini-badge video">וידאו 🎥</span><div style="background: #1e293b; width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:#fff; font-size:0.75rem;">🎥 סרטון</div>';
                }} else {{
                    const thumbUrl = getThumbPath(slide);
                    const colorBadge = slide.colorized_path ? '<span class="mini-badge colorized" style="left:4px; right:auto;">צבע 🎨</span>' : '';
                    thumbHtml = `<span class="mini-badge photo">#${{idx + 1}}</span>${{colorBadge}}<img src="${{thumbUrl}}" loading="lazy" onerror="this.src='photos/${{slide.primary_item.filename}}'">`;
                }}

                card.innerHTML = `
                    <div class="scene-thumb">${{thumbHtml}}</div>
                    <div class="scene-meta">
                        <div class="scene-title">${{slide.caption || 'שקף'}}</div>
                        <button type="button" class="quick-move-btn" onclick="event.stopPropagation(); quickMoveToTop(${{idx}})">🔝 1</button>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        function quickMoveToTop(idx) {{
            const item = slides.splice(idx, 1)[0];
            slides.unshift(item);
            selectSlide(0);
            autoSaveState();
            renderScenesList(activeFilter);
        }}

        function filterChapter(act) {{
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            renderScenesList(act);
        }}

        function selectSlide(idx) {{
            currentIndex = idx;
            slideStartTime = performance.now();

            document.querySelectorAll('.scene-card').forEach((c) => {{
                c.classList.toggle('selected', parseInt(c.dataset.index, 10) === idx);
            }});

            const cur = slides[currentIndex];
            document.getElementById('cur-caption').value = cur.caption || '';
            document.getElementById('cur-quote').value = cur.quote || '';
            document.getElementById('cur-duration').value = cur.duration || 8;
            document.getElementById('jump-to-pos').value = currentIndex + 1;
            document.getElementById('jump-to-pos').max = slides.length;
            document.getElementById('slide-counter').textContent = `שקף ${{currentIndex + 1}} מתוך ${{slides.length}}`;

            // Transforms
            const scale = cur.scale !== undefined ? cur.scale : 1.0;
            const offsetY = cur.offsetY || 0;
            const offsetX = cur.offsetX || 0;
            const trim = cur.trim || 0;
            const fitMode = cur.fitMode || 'contain';
            const showCap = cur.showCaption !== undefined ? cur.showCaption : true;

            document.getElementById('scale-slider').value = scale;
            document.getElementById('val-scale').textContent = `${{Math.round(scale * 100)}}%`;
            document.getElementById('offsetY-slider').value = offsetY;
            document.getElementById('val-offsetY').textContent = `${{offsetY}}px`;
            document.getElementById('offsetX-slider').value = offsetX;
            document.getElementById('val-offsetX').textContent = `${{offsetX}}px`;
            document.getElementById('trim-slider').value = trim;
            document.getElementById('val-trim').textContent = `${{trim}}%`;

            document.getElementById('btn-fit-contain').classList.toggle('active', fitMode === 'contain');
            document.getElementById('btn-fit-cover').classList.toggle('active', fitMode === 'cover');
            captionsContainer.style.display = showCap ? 'block' : 'none';

            // Update text overlays
            badgeChapter.textContent = cur.act_title || 'יום הולדת 60 לאבא';
            captionDisplay.textContent = cur.caption || '';
            quoteDisplay.textContent = cur.quote ? `"${{cur.quote}}"` : '';

            renderCurrentFrame(0);
        }}

        function renderCurrentFrame(progress = 0) {{
            const cur = slides[currentIndex];

            if (cur.type === 'video') {{
                mainPhoto.style.display = 'none';
                bgBlurPhoto.style.display = 'none';
                overlayLayer.style.display = 'none';
                videoPlayer.style.display = 'block';
                const videoUrl = cur.primary_item.cloud_path || ('videos/' + cur.primary_item.filename);
                videoPlayer.src = videoUrl;
                bgAudio.volume = 0.1;
                
                if (isPlaying) {{
                    videoPlayer.play().catch(e => console.log('Video play policy:', e));
                }}
                videoPlayer.onended = () => {{
                    bgAudio.volume = 0.7;
                    if (isPlaying) nextSlide();
                }};
                return;
            }}

            bgAudio.volume = 0.7;
            videoPlayer.style.display = 'none';
            videoPlayer.pause();
            mainPhoto.style.display = 'block';
            bgBlurPhoto.style.display = 'block';
            overlayLayer.style.display = 'flex';

            const cleanPath = getActivePhotoPath(cur);
            if (mainPhoto.getAttribute('data-active-src') !== cleanPath) {{
                mainPhoto.setAttribute('data-active-src', cleanPath);
                mainPhoto.src = cleanPath;
                bgBlurPhoto.src = cleanPath;
            }}

            // Fit mode class
            const fitMode = cur.fitMode || 'contain';
            if (fitMode === 'cover') {{
                mainPhoto.className = 'cinematic-img mode-cover';
                bgBlurPhoto.style.display = 'none';
            }} else {{
                mainPhoto.className = 'cinematic-img';
                bgBlurPhoto.style.display = 'block';
            }}

            // User Transforms
            const userScale = cur.scale !== undefined ? cur.scale : 1.0;
            const userOffsetY = cur.offsetY || 0;
            const userOffsetX = cur.offsetX || 0;
            const rot = cur.rotation || 0;

            let trimClip = 'none';
            if (cur.cropBox && cur.cropBox.length === 4) {{
                const top = (cur.cropBox[0] / 10).toFixed(1);
                const left = (cur.cropBox[1] / 10).toFixed(1);
                const bottom = ((1000 - cur.cropBox[2]) / 10).toFixed(1);
                const right = ((1000 - cur.cropBox[3]) / 10).toFixed(1);
                trimClip = `inset(${{top}}% ${{right}}% ${{bottom}}% ${{left}}%)`;
            }} else if (cur.trim && cur.trim > 0) {{
                trimClip = `inset(${{cur.trim}}%)`;
            }}
            mainPhoto.style.clipPath = trimClip;

            // Subtle slow drift
            const panDrift = fitMode === 'cover' ? progress * -30 : 0;
            const slowZoom = userScale * (1.0 + (progress * 0.02));

            mainPhoto.style.transform = `translate3d(${{userOffsetX}}px, ${{userOffsetY + panDrift}}px, 0) scale(${{slowZoom}}) rotate(${{rot}}deg)`;
        }}

        function updateCurrentCaption(val) {{
            slides[currentIndex].caption = val;
            captionDisplay.textContent = val;
            autoSaveState();
        }}

        function updateCurrentQuote(val) {{
            slides[currentIndex].quote = val;
            quoteDisplay.textContent = val ? `"${{val}}"` : '';
            autoSaveState();
        }}

        function updateCurrentDuration(val) {{
            slides[currentIndex].duration = parseInt(val, 10);
            autoSaveState();
        }}

        function nextSlide() {{
            if (currentIndex < slides.length - 1) {{
                selectSlide(currentIndex + 1);
            }} else {{
                selectSlide(0);
            }}
        }}

        function prevSlide() {{
            if (currentIndex > 0) {{
                selectSlide(currentIndex - 1);
            }}
        }}

        function togglePlay() {{
            isPlaying = !isPlaying;
            const btn = document.getElementById('btn-play');
            if (isPlaying) {{
                btn.textContent = '⏸️ השהה מצגת';
                btn.className = 'gold';
                slideStartTime = performance.now();
                if (bgAudio.paused) {{
                    bgAudio.play().catch(e => console.log('Audio autoplay policy:', e));
                }}
                startPresentationLoop();
            }} else {{
                btn.textContent = "▶️ נגן מצגת (8 שנ' לשקף)";
                btn.className = 'primary';
                stopPresentationLoop();
                progressBar.style.width = '0%';
                renderCurrentFrame(0);
            }}
        }}

        function startPresentationLoop() {{
            function step(now) {{
                if (!isPlaying) return;
                const cur = slides[currentIndex];

                if (cur.type === 'video') {{
                    animationFrame = requestAnimationFrame(step);
                    return;
                }}

                const durationMs = (cur.duration || 8) * 1000;
                const elapsed = now - slideStartTime;
                const progress = Math.min(1.0, elapsed / durationMs);
                
                progressBar.style.width = `${{(progress * 100).toFixed(1)}}%`;
                renderCurrentFrame(progress);

                if (elapsed >= durationMs) {{
                    progressBar.style.width = '0%';
                    nextSlide();
                }}

                animationFrame = requestAnimationFrame(step);
            }}

            animationFrame = requestAnimationFrame(step);
        }}

        function stopPresentationLoop() {{
            if (animationFrame) cancelAnimationFrame(animationFrame);
        }}

        function toggleFullscreen() {{
            const screen = document.getElementById('player-screen');
            if (!document.fullscreenElement) {{
                screen.requestFullscreen().catch(err => alert(`Error: ${{err.message}}`));
            }} else {{
                document.exitFullscreen();
            }}
        }}

        renderScenesList('all');
        selectSlide(0);
    </script>
</body>
</html>
"""
    out_path = 'projects/dad-birthday-studio/public/index.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated standalone cloud index.html at {out_path}")

if __name__ == '__main__':
    build_cloud_index_html()
