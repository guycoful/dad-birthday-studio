import json
import re

with open('public/storyboard.json', 'r', encoding='utf-8') as f:
    storyboard = json.load(f)
sb_json_str = json.dumps(storyboard, ensure_ascii=False)

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update initialTimelineData
    prefix = 'const initialTimelineData = '
    start_idx = content.find(prefix)
    if start_idx == -1:
        raise Exception(f'initialTimelineData not found in {filepath}')
    end_idx = content.find(';\n', start_idx)
    if end_idx == -1:
        raise Exception(f'End of initialTimelineData not found in {filepath}')
    content = content[:start_idx + len(prefix)] + sb_json_str + content[end_idx:]
    print(f'[{filepath}] Updated initialTimelineData!')

    # 2. Update LOCAL_STORAGE_KEY & migration logic
    old_init = """const LOCAL_STORAGE_KEY = 'dad_cloud_studio_state_v8';
        let savedState = null;
        try {
            const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
            if (raw) {
                savedState = JSON.parse(raw);
            } else {
                localStorage.removeItem('dad_cloud_studio_last_save');
            }
        } catch(e) { console.log('LocalStorage load:', e); }"""

    new_init = """const LOCAL_STORAGE_KEY = 'dad_cloud_studio_state_v9';
        let savedState = null;
        try {
            let raw = localStorage.getItem(LOCAL_STORAGE_KEY);
            if (!raw) {
                // Seamlessly migrate from v8 or older cached state
                const v8Raw = localStorage.getItem('dad_cloud_studio_state_v8');
                if (v8Raw) {
                    console.log('[Storage Migration] Migrating state_v8 to state_v9 with cut presets support');
                    raw = v8Raw;
                }
            }
            if (raw) {
                savedState = JSON.parse(raw);
            } else {
                localStorage.removeItem('dad_cloud_studio_last_save');
            }
        } catch(e) { console.log('LocalStorage load error:', e); }"""

    if old_init in content:
        content = content.replace(old_init, new_init)
        print(f'[{filepath}] Updated LOCAL_STORAGE_KEY to v9 with migration!')
    else:
        print(f'[{filepath}] Warning: old_init not found directly, checking...')

    content = content.replace("localStorage.setItem('dad_cloud_studio_state_v8'", "localStorage.setItem(LOCAL_STORAGE_KEY")

    # 3. Add BLESSING_CUT_PRESETS, getBlessingNumber, ensureSlideCutPresets before applySlideDefaults
    presets_block = """        // ==========================================
        // ✂️ BLESSING VIDEOS CUT PRESETS & PERSISTENCE
        // ==========================================
        const BLESSING_CUT_PRESETS = {
            1: { none: { url: 'videos/blessing_01_raw.mp4', duration: 30.17 }, moderate: { url: 'videos/blessing_01_moderate.mp4', duration: 20.43 }, aggressive: { url: 'videos/blessing_01_aggressive.mp4', duration: 15.80 } },
            2: { none: { url: 'videos/blessing_02_raw.mp4', duration: 58.10 }, moderate: { url: 'videos/blessing_02_moderate.mp4', duration: 54.39 }, aggressive: { url: 'videos/blessing_02_aggressive.mp4', duration: 46.43 } },
            3: { none: { url: 'videos/blessing_03_raw.mp4', duration: 8.10 }, moderate: { url: 'videos/blessing_03_moderate.mp4', duration: 7.20 }, aggressive: { url: 'videos/blessing_03_aggressive.mp4', duration: 5.57 } },
            4: { none: { url: 'videos/blessing_04_raw.mp4', duration: 35.30 }, moderate: { url: 'videos/blessing_04_moderate.mp4', duration: 32.93 }, aggressive: { url: 'videos/blessing_04_aggressive.mp4', duration: 20.93 } },
            5: { none: { url: 'videos/blessing_05_raw.mp4', duration: 25.86 }, moderate: { url: 'videos/blessing_05_moderate.mp4', duration: 25.47 }, aggressive: { url: 'videos/blessing_05_aggressive.mp4', duration: 21.02 } },
            6: { none: { url: 'videos/blessing_06_raw.mp4', duration: 27.97 }, moderate: { url: 'videos/blessing_06_moderate.mp4', duration: 26.61 }, aggressive: { url: 'videos/blessing_06_aggressive.mp4', duration: 18.82 } },
            7: { none: { url: 'videos/blessing_07_raw.mp4', duration: 21.98 }, moderate: { url: 'videos/blessing_07_moderate.mp4', duration: 19.27 }, aggressive: { url: 'videos/blessing_07_aggressive.mp4', duration: 14.29 } },
            8: { none: { url: 'videos/blessing_08_raw.mp4', duration: 21.47 }, moderate: { url: 'videos/blessing_08_moderate.mp4', duration: 20.47 }, aggressive: { url: 'videos/blessing_08_aggressive.mp4', duration: 20.05 } },
            9: { none: { url: 'videos/blessing_09_raw.mp4', duration: 23.67 }, moderate: { url: 'videos/blessing_09_moderate.mp4', duration: 18.77 }, aggressive: { url: 'videos/blessing_09_aggressive.mp4', duration: 13.14 } },
            10: { none: { url: 'videos/blessing_10_raw.mp4', duration: 16.18 }, moderate: { url: 'videos/blessing_10_moderate.mp4', duration: 16.18 }, aggressive: { url: 'videos/blessing_10_aggressive.mp4', duration: 14.90 } },
            11: { none: { url: 'videos/blessing_11_raw.mp4', duration: 49.77 }, moderate: { url: 'videos/blessing_11_moderate.mp4', duration: 29.82 }, aggressive: { url: 'videos/blessing_11_aggressive.mp4', duration: 20.35 } },
            12: { none: { url: 'videos/blessing_12_raw.mp4', duration: 23.50 }, moderate: { url: 'videos/blessing_12_moderate.mp4', duration: 21.08 }, aggressive: { url: 'videos/blessing_12_aggressive.mp4', duration: 18.33 } },
            13: { none: { url: 'videos/blessing_13_raw.mp4', duration: 66.12 }, moderate: { url: 'videos/blessing_13_moderate.mp4', duration: 60.40 }, aggressive: { url: 'videos/blessing_13_aggressive.mp4', duration: 52.20 } },
            14: { none: { url: 'videos/blessing_14_raw.mp4', duration: 63.05 }, moderate: { url: 'videos/blessing_14_moderate.mp4', duration: 51.52 }, aggressive: { url: 'videos/blessing_14_aggressive.mp4', duration: 44.98 } },
            15: { none: { url: 'videos/blessing_15_raw.mp4', duration: 16.62 }, moderate: { url: 'videos/blessing_15_moderate.mp4', duration: 15.07 }, aggressive: { url: 'videos/blessing_15_aggressive.mp4', duration: 14.37 } },
            16: { none: { url: 'videos/blessing_16_raw.mp4', duration: 24.51 }, moderate: { url: 'videos/blessing_16_moderate.mp4', duration: 21.42 }, aggressive: { url: 'videos/blessing_16_aggressive.mp4', duration: 12.11 } },
            17: { none: { url: 'videos/blessing_17_raw.mp4', duration: 33.28 }, moderate: { url: 'videos/blessing_17_moderate.mp4', duration: 25.36 }, aggressive: { url: 'videos/blessing_17_aggressive.mp4', duration: 26.16 } },
            18: { none: { url: 'videos/blessing_18_raw.mp4', duration: 41.34 }, moderate: { url: 'videos/blessing_18_moderate.mp4', duration: 36.45 }, aggressive: { url: 'videos/blessing_18_aggressive.mp4', duration: 29.11 } },
            19: { none: { url: 'videos/blessing_19_raw.mp4', duration: 28.47 }, moderate: { url: 'videos/blessing_19_moderate.mp4', duration: 26.73 }, aggressive: { url: 'videos/blessing_19_aggressive.mp4', duration: 23.17 } },
            20: { none: { url: 'videos/blessing_20_raw.mp4', duration: 99.90 }, moderate: { url: 'videos/blessing_20_moderate.mp4', duration: 91.63 }, aggressive: { url: 'videos/blessing_20_aggressive.mp4', duration: 82.93 } },
            21: { none: { url: 'videos/blessing_21_raw.mp4', duration: 23.99 }, moderate: { url: 'videos/blessing_21_moderate.mp4', duration: 23.59 }, aggressive: { url: 'videos/blessing_21_aggressive.mp4', duration: 22.26 } },
            22: { none: { url: 'videos/blessing_22_raw.mp4', duration: 35.10 }, moderate: { url: 'videos/blessing_22_moderate.mp4', duration: 31.09 }, aggressive: { url: 'videos/blessing_22_aggressive.mp4', duration: 25.24 } },
            23: { none: { url: 'videos/blessing_23_raw.mp4', duration: 21.70 }, moderate: { url: 'videos/blessing_23_moderate.mp4', duration: 20.95 }, aggressive: { url: 'videos/blessing_23_aggressive.mp4', duration: 17.31 } },
            24: { none: { url: 'videos/blessing_24_raw.mp4', duration: 8.61 }, moderate: { url: 'videos/blessing_24_moderate.mp4', duration: 7.94 }, aggressive: { url: 'videos/blessing_24_aggressive.mp4', duration: 6.44 } }
        };

        function getBlessingNumber(s) {
            if (!s) return null;
            const fn = (s.primary_item && (s.primary_item.filename || s.primary_item.url || s.primary_item.cloud_path)) || '';
            const cap = s.caption || (s.primary_item && s.primary_item.caption) || '';
            const m1 = fn.match(/blessing_(\d+)/i);
            if (m1) return parseInt(m1[1], 10);
            const m2 = cap.match(/ברכה\s*(\d+)/i);
            if (m2) return parseInt(m2[1], 10);
            if (s.slide_id >= 1790579438954 && s.slide_id <= 1790579438977) {
                return (s.slide_id - 1790579438954) + 1;
            }
            return null;
        }

        function ensureSlideCutPresets(s) {
            if (!s) return;
            const num = getBlessingNumber(s);
            if (num && BLESSING_CUT_PRESETS[num]) {
                const defPresets = BLESSING_CUT_PRESETS[num];
                if (!s.cut_presets || !s.cut_presets.none || !s.cut_presets.moderate || !s.cut_presets.aggressive) {
                    s.cut_presets = JSON.parse(JSON.stringify(defPresets));
                }
                if (!s.cut_mode) {
                    const fn = (s.primary_item && (s.primary_item.url || s.primary_item.filename)) || '';
                    if (fn.includes('_raw')) s.cut_mode = 'none';
                    else if (fn.includes('_aggressive')) s.cut_mode = 'aggressive';
                    else s.cut_mode = 'moderate';
                }

                // Sync media url and filenames with the active cut_mode
                const preset = s.cut_presets[s.cut_mode] || s.cut_presets['moderate'];
                if (preset) {
                    if (!s.primary_item) s.primary_item = {};
                    const curUrl = s.primary_item.url || '';
                    if (!curUrl || (curUrl.includes('blessing_') && !curUrl.endsWith(preset.url.split('/').pop()))) {
                        s.primary_item.url = preset.url;
                        s.primary_item.cloud_path = preset.url;
                        s.primary_item.relative_path = preset.url;
                        s.primary_item.filename = preset.url.replace('videos/', '');
                    }
                    if (Array.isArray(s.items)) {
                        s.items.forEach(it => {
                            if (it) {
                                it.url = preset.url;
                                it.cloud_path = preset.url;
                                it.relative_path = preset.url;
                                it.filename = preset.url.replace('videos/', '');
                            }
                        });
                    }
                    if (!s.video_segments || s.video_segments.length === 0) {
                        s.video_segments = [{ start: 0, end: preset.duration }];
                        s.video_start = 0;
                        s.video_end = preset.duration;
                        s.duration = Math.round(preset.duration);
                    }
                }
            }
        }

"""

    old_apply = """        // Clean slide defaults without overwriting user adjustments or zooms
        function applySlideDefaults(s) {
            if (s.fitMode === undefined) s.fitMode = 'contain';
            if (s.scale === undefined) s.scale = 1.0;
            if (s.offsetX === undefined) s.offsetX = 0;
            if (s.offsetY === undefined) s.offsetY = 0;
            if (s.trim === undefined) s.trim = 0;
            if (s.showCaption === undefined) s.showCaption = true;
            if (s.soundtrack_action === undefined) s.soundtrack_action = 'continue';
            if (s.transition_effect === undefined) s.transition_effect = 'crossfade';

            const isVid = s.type === 'video' || (s.primary_item && s.primary_item.is_video);
            if (isVid) {
                if (s.video_start === undefined || s.video_start === null) s.video_start = 0;
                if (s.video_end === undefined || s.video_end === null) s.video_end = s.duration || 14;
            }

            const fname = (s.primary_item && s.primary_item.filename) || '';"""

    new_apply = presets_block + """        // Clean slide defaults without overwriting user adjustments or zooms
        function applySlideDefaults(s) {
            if (s.fitMode === undefined) s.fitMode = 'contain';
            if (s.scale === undefined) s.scale = 1.0;
            if (s.offsetX === undefined) s.offsetX = 0;
            if (s.offsetY === undefined) s.offsetY = 0;
            if (s.trim === undefined) s.trim = 0;
            if (s.showCaption === undefined) s.showCaption = true;
            if (s.soundtrack_action === undefined) s.soundtrack_action = 'continue';
            if (s.transition_effect === undefined) s.transition_effect = 'crossfade';

            const isVid = s.type === 'video' || (s.primary_item && s.primary_item.is_video);
            if (isVid) {
                if (s.video_start === undefined || s.video_start === null) s.video_start = 0;
                if (s.video_end === undefined || s.video_end === null) s.video_end = s.duration || 14;
            }

            ensureSlideCutPresets(s);

            const fname = (s.primary_item && s.primary_item.filename) || '';"""

    if old_apply in content:
        content = content.replace(old_apply, new_apply)
        print(f'[{filepath}] Injected presets_block and updated applySlideDefaults!')
    else:
        print(f'[{filepath}] Warning: old_apply not found directly, checking...')

    # 4. Update setVideoCutMode to ensure items & paths are updated and autoSaveState runs
    old_set_cut = """        function setVideoCutMode(mode, fromUserClick = true) {
            const cur = slides[currentIndex];
            if (!cur || !videoPlayer) return;

            cur.cut_mode = mode;

            if (cur.cut_presets && cur.cut_presets[mode]) {
                const preset = cur.cut_presets[mode];
                const prevPaused = videoPlayer.paused;
                if (cur.primary_item) {
                    cur.primary_item.url = preset.url;
                    cur.primary_item.filename = preset.url.replace('videos/', '');
                }
                cur.duration = Math.round(preset.duration);
                cur.video_start = 0;
                cur.video_end = preset.duration;
                cur.video_segments = [{ start: 0, end: preset.duration }];

                videoPlayer.removeAttribute('data-active-src');
                videoPlayer.src = preset.url;
                videoPlayer.currentTime = 0;
                videoPlayer.load();
                if (!prevPaused) {
                    videoPlayer.play().catch(e => console.log('Autoplay error:', e));
                }
            } else {
                const vidDur = (videoPlayer && videoPlayer.duration && !isNaN(videoPlayer.duration)) ? videoPlayer.duration : (cur.duration || 60);
                if (mode === 'none') {
                    cur.video_segments = [{ start: 0, end: Number(vidDur.toFixed(1)) }];
                    cur.video_start = 0;
                    cur.video_end = Number(vidDur.toFixed(1));
                    cur.duration = Math.round(vidDur);
                    videoPlayer.currentTime = 0;
                }
            }"""

    new_set_cut = """        function setVideoCutMode(mode, fromUserClick = true) {
            const cur = slides[currentIndex];
            if (!cur || !videoPlayer) return;

            ensureSlideCutPresets(cur);
            cur.cut_mode = mode;

            if (cur.cut_presets && cur.cut_presets[mode]) {
                const preset = cur.cut_presets[mode];
                const prevPaused = videoPlayer.paused;
                if (cur.primary_item) {
                    cur.primary_item.url = preset.url;
                    cur.primary_item.filename = preset.url.replace('videos/', '');
                    cur.primary_item.cloud_path = preset.url;
                    cur.primary_item.relative_path = preset.url;
                }
                if (Array.isArray(cur.items)) {
                    cur.items.forEach(it => {
                        if (it) {
                            it.url = preset.url;
                            it.filename = preset.url.replace('videos/', '');
                            it.cloud_path = preset.url;
                            it.relative_path = preset.url;
                        }
                    });
                }
                cur.duration = Math.round(preset.duration);
                cur.video_start = 0;
                cur.video_end = preset.duration;
                cur.video_segments = [{ start: 0, end: preset.duration }];

                videoPlayer.removeAttribute('data-active-src');
                videoPlayer.src = preset.url;
                videoPlayer.currentTime = 0;
                videoPlayer.load();
                if (!prevPaused) {
                    videoPlayer.play().catch(e => console.log('Autoplay error:', e));
                }
            } else {
                const vidDur = (videoPlayer && videoPlayer.duration && !isNaN(videoPlayer.duration)) ? videoPlayer.duration : (cur.duration || 60);
                if (mode === 'none') {
                    cur.video_segments = [{ start: 0, end: Number(vidDur.toFixed(1)) }];
                    cur.video_start = 0;
                    cur.video_end = Number(vidDur.toFixed(1));
                    cur.duration = Math.round(vidDur);
                    videoPlayer.currentTime = 0;
                }
            }"""

    if old_set_cut in content:
        content = content.replace(old_set_cut, new_set_cut)
        print(f'[{filepath}] Updated setVideoCutMode!')
    else:
        print(f'[{filepath}] Warning: old_set_cut not found directly, checking...')

    # 5. Update static fetch fallback in loadStoryboardFromCloud
    old_fetch = """                // Priority 2: Static fetch from GitHub Pages CDN
                if (!cloudData) {
                    const res = await fetch('storyboard.json?v=' + Date.now());
                    if (res.ok) {
                        cloudData = await res.json();
                    }
                }"""

    new_fetch = """                // Priority 2: Static fetch from GitHub Pages CDN or local server
                if (!cloudData) {
                    try {
                        let res = await fetch('storyboard.json?v=' + Date.now());
                        if (!res.ok) {
                            res = await fetch('public/storyboard.json?v=' + Date.now());
                        }
                        if (res.ok) {
                            cloudData = await res.json();
                        }
                    } catch(fetchErr) {
                        console.warn('[Cloud Load] Static fetch failed:', fetchErr);
                    }
                }"""

    if old_fetch in content:
        content = content.replace(old_fetch, new_fetch)
        print(f'[{filepath}] Updated loadStoryboardFromCloud static fetch with public/ fallback!')
    else:
        print(f'[{filepath}] Warning: old_fetch not found directly, checking...')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'[{filepath}] Written successfully!')

update_file('public/index.html')
update_file('index.html')
