import re
import sys

def apply_github_cloud_sync():
    html_path = 'projects/dad-birthday-studio/public/index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS for modal
    modal_css = """
        /* GitHub Sync Modal */
        .modal-backdrop {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            padding: 20px;
        }
        .modal-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 8px 10px -6px rgba(0, 0, 0, 0.6);
            overflow: hidden;
            animation: modalIn 0.2s ease-out;
        }
        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .modal-header {
            background: #1e293b;
            padding: 14px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
        }
        .modal-header h3 {
            margin: 0;
            font-size: 1.05rem;
            color: var(--gold);
        }
        .modal-close {
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }
        .modal-close:hover {
            color: #fff;
        }
        .modal-body {
            padding: 18px;
            font-size: 0.88rem;
            color: var(--text-main);
            line-height: 1.5;
        }
    """
    if '.modal-backdrop' not in content:
        content = content.replace('    </style>', modal_css + '\n    </style>')
        print('Added modal CSS!')

    # 2. Add GitHub token field in sidebar cloud panel
    old_cloud_panel_target = '<div id="cloud-sync-status" class="status-badge gold" style="display: block;">סנכרון ענן פעיל ✅</div>'
    new_cloud_panel_elements = """<div class="form-group" style="margin-top: 8px;">
                    <label style="display: flex; justify-content: space-between; align-items: center; font-size: 0.78rem; margin-bottom: 3px;">
                        <span>🔑 מפתח GitHub Token לסנכרון:</span>
                        <a href="https://github.com/settings/tokens/new?description=DadBirthdayStudio&scopes=repo" target="_blank" style="color: var(--accent); font-size: 0.72rem; text-decoration: underline;">יצירת מפתח</a>
                    </label>
                    <div style="display: flex; gap: 4px;">
                        <input type="password" id="github-sync-token" placeholder="ghp_... או gho_..." onchange="saveGithubToken(this.value)" style="flex: 1; font-size: 0.78rem; padding: 5px 8px;">
                        <button type="button" class="tool-btn" onclick="toggleGithubTokenVisibility()" style="padding: 4px 8px; font-size: 0.75rem;" id="btn-toggle-gh-token" title="הצג/הסתר מפתח">👁️</button>
                    </div>
                </div>
                <div id="cloud-sync-status" class="status-badge gold" style="display: block;">סנכרון ענן פעיל ✅</div>"""
    
    if 'id="github-sync-token"' not in content:
        if old_cloud_panel_target in content:
            content = content.replace(old_cloud_panel_target, new_cloud_panel_elements)
            print('Added GitHub token field to sidebar!')
        else:
            print('Warning: old_cloud_panel_target not found!')

    # 3. Add Modal HTML before </body>
    modal_html = """
    <!-- GitHub Token Modal -->
    <div id="github-token-modal" class="modal-backdrop" style="display: none;">
        <div class="modal-card">
            <div class="modal-header">
                <h3>🔑 חיבור ישיר לשמירה בענן (GitHub)</h3>
                <button type="button" class="modal-close" onclick="closeGithubTokenModal()">✕</button>
            </div>
            <div class="modal-body">
                <p style="margin-bottom: 10px;">כדי שהשינויים שלך יישמרו ישירות למאגר ה-GitHub ויעדכנו את האתר החי באוויר, נדרש מפתח <strong>GitHub Personal Access Token</strong> (עם הרשאת <code>repo</code>).</p>
                <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 10px; margin: 10px 0; font-size: 0.82rem; line-height: 1.4;">
                    💡 <strong>קיים כבר במחשב שלך:</strong> אם אתה מחובר ב-GitHub CLI, הרץ בטרמינל <code>gh auth token</code> והדבק את המפתח שמופיע כאן.<br>
                    🔒 המפתח נשמר אך ורק בדפדפן המקומי שלך (LocalStorage) ואינו מועבר לאיש.
                </div>
                <div class="form-group" style="margin: 12px 0;">
                    <label style="display: block; margin-bottom: 5px; font-weight: 600;">הדבק כאן את מפתח ה-GitHub Token:</label>
                    <input type="password" id="modal-gh-token-input" placeholder="ghp_... או gho_..." style="width: 100%; padding: 8px; font-size: 0.9rem; background: var(--bg-main); border: 1px solid var(--border); color: #fff; border-radius: 6px;">
                </div>
                <div style="display: flex; gap: 8px; margin-top: 16px;">
                    <button type="button" class="gold" onclick="confirmSaveWithModalToken()" style="flex: 1; justify-content: center; padding: 8px;">
                        🚀 שמור וסנכרן עכשיו ל-GitHub
                    </button>
                    <button type="button" class="tool-btn" onclick="exportStoryboardJson(); closeGithubTokenModal();" style="font-size: 0.82rem;">
                        📥 הורד JSON למחשב
                    </button>
                </div>
            </div>
        </div>
    </div>
    """
    if 'id="github-token-modal"' not in content:
        content = content.replace('</body>', modal_html + '\n</body>')
        print('Added modal HTML before body end!')

    # 4. Replace saveStoryboardToCloud and add GitHub direct sync functions in JS
    old_save_function_regex = r'// Dynamic cloud save \(GitHub / API\)[\s\S]*?function exportStoryboardJson'
    
    new_save_functions = """// --- DIRECT GITHUB & CLOUD PERSISTENCE ---
        const GITHUB_TOKEN_KEY = 'dad_studio_github_token';
        const GITHUB_REPO_OWNER = 'guycoful';
        const GITHUB_REPO_NAME = 'dad-birthday-studio';

        const savedGithubToken = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
        const ghTokenInput = document.getElementById('github-sync-token');
        if (ghTokenInput) {
            ghTokenInput.value = savedGithubToken;
        }

        function saveGithubToken(val) {
            const trimmed = val.trim();
            localStorage.setItem(GITHUB_TOKEN_KEY, trimmed);
            const input = document.getElementById('github-sync-token');
            if (input) input.value = trimmed;
            if (trimmed) {
                showCloudStatus('מפתח GitHub נשמר בהצלחה בדפדפן ✅');
            } else {
                showCloudStatus('מפתח GitHub הוסר');
            }
        }

        function toggleGithubTokenVisibility() {
            const input = document.getElementById('github-sync-token');
            if (!input) return;
            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';
            document.getElementById('btn-toggle-gh-token').textContent = isPassword ? '🔒' : '👁️';
        }

        function openGithubTokenModal() {
            const modal = document.getElementById('github-token-modal');
            const input = document.getElementById('modal-gh-token-input');
            const saved = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
            if (input) input.value = saved;
            if (modal) modal.style.display = 'flex';
        }

        function closeGithubTokenModal() {
            const modal = document.getElementById('github-token-modal');
            if (modal) modal.style.display = 'none';
        }

        function confirmSaveWithModalToken() {
            const input = document.getElementById('modal-gh-token-input');
            const token = input ? input.value.trim() : '';
            if (!token) {
                alert('נא להדביק מפתח GitHub Token תקף.');
                return;
            }
            saveGithubToken(token);
            closeGithubTokenModal();
            saveStoryboardToCloud();
        }

        function utf8ToBase64(str) {
            const bytes = new TextEncoder().encode(str);
            let binary = '';
            const len = bytes.byteLength;
            for (let i = 0; i < len; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }

        async function syncFileToGithub(filePath, b64Content, token, commitMsg) {
            const apiUrl = `https://api.github.com/repos/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}/contents/${filePath}`;
            
            // Get current SHA of existing file
            let sha = null;
            const getRes = await fetch(apiUrl, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (getRes.status === 401 || getRes.status === 403) {
                const err = new Error('הרשאה נדחתה ב-GitHub (בדוק את תקינות ה-Token והרשאת repo)');
                err.status = getRes.status;
                throw err;
            }

            if (getRes.ok) {
                const fileData = await getRes.json();
                sha = fileData.sha;
            }

            const putBody = {
                message: commitMsg,
                content: b64Content
            };
            if (sha) putBody.sha = sha;

            const putRes = await fetch(apiUrl, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(putBody)
            });

            if (!putRes.ok) {
                const errData = await putRes.json().catch(() => ({}));
                const err = new Error(errData.message || `HTTP ${putRes.status}`);
                err.status = putRes.status;
                throw err;
            }

            return await putRes.json();
        }

        // Dynamic cloud save (GitHub Direct REST API + LocalStorage)
        async function saveStoryboardToCloud() {
            autoSaveState();
            showCloudStatus('⏳ שומר ומסנכרן לענן...');

            const token = (document.getElementById('github-sync-token')?.value || localStorage.getItem(GITHUB_TOKEN_KEY) || '').trim();

            if (!token) {
                // If running on custom server / localhost where /api/storyboard exists, try it first
                if (window.location.hostname !== 'guycoful.github.io') {
                    try {
                        const res = await fetch('/api/storyboard', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(slides)
                        });
                        const data = await res.json();
                        if (res.ok && data.status === 'ok') {
                            showCloudStatus(data.synced_to_github ? 'נשמר בענן וב-GitHub בהצלחה ✅' : 'נשמר בשרת בהצלחה ✅');
                            return;
                        }
                    } catch(err) {
                        console.log('Local api check fallback:', err);
                    }
                }
                
                // On GitHub Pages without token, show helpful modal prompt
                openGithubTokenModal();
                showCloudStatus('נדרש מפתח GitHub Token לשמירה בענן 🔑');
                return;
            }

            try {
                showCloudStatus('⏳ מתחבר ל-GitHub ומסנכרן קבצים...');

                const payloadData = {
                    title: "סטודיו סרטון יום הולדת 60 לאבא צחי",
                    total_slides: slides.length,
                    slides: slides,
                    last_updated: new Date().toISOString()
                };
                const jsonStr = JSON.stringify(payloadData, null, 2);
                const b64 = utf8ToBase64(jsonStr);

                // 1. Commit public/storyboard.json
                await syncFileToGithub('public/storyboard.json', b64, token, 'עדכון שקפים מתוך סטודיו הענן 🎬');

                // 2. Commit public/default_storyboard.json as backup sync
                try {
                    await syncFileToGithub('public/default_storyboard.json', b64, token, 'סנכרון default_storyboard.json 🎬');
                } catch(e) {
                    console.warn('default_storyboard sync note:', e);
                }

                showCloudStatus('נשמר בענן וב-GitHub בהצלחה! פריסה אוטומטית החלה באוויר 🚀');
                alert('✅ השינויים נשמרו ונדחפו בהצלחה ישירות למאגר GitHub!\\nתהליך הפריסה האוטומטי (GitHub Actions) החל כעת ויעדכן את האתר החי תוך כ-20 שניות.');
            } catch(err) {
                console.error('GitHub Sync Error:', err);
                showCloudStatus(`❌ שגיאה בשמירה ל-GitHub: ${err.message}`);
                if (err.status === 401 || err.status === 403) {
                    alert('❌ שגיאת הרשאה ב-GitHub (401/403): המפתח אינו תקין או שחסרה הרשאת repo.\\nאנא עדכן את המפתח.');
                    openGithubTokenModal();
                } else {
                    alert(`❌ שגיאה בשמירה ל-GitHub: ${err.message}\\nהשינויים נשמרו מקומית בדפדפן, אך לא הגיעו למאגר.`);
                }
            }
        }

        function exportStoryboardJson"""

    m = re.search(old_save_function_regex, content)
    if m:
        content = content[:m.start()] + new_save_functions + content[m.end():]
        print('Replaced saveStoryboardToCloud with direct GitHub REST API sync!')
    else:
        print('Warning: old_save_function_regex did not match!')

    # Save to both public/index.html and index.html
    with open('projects/dad-birthday-studio/public/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated projects/dad-birthday-studio/public/index.html')

    with open('projects/dad-birthday-studio/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated projects/dad-birthday-studio/index.html')

if __name__ == '__main__':
    apply_github_cloud_sync()
