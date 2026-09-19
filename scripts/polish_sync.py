import re

def polish_sync():
    paths = ['projects/dad-birthday-studio/public/index.html', 'projects/dad-birthday-studio/index.html']
    
    for path in paths:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Update utf8ToBase64 to chunked
        old_utf8 = """function utf8ToBase64(str) {
            const bytes = new TextEncoder().encode(str);
            let binary = '';
            const len = bytes.byteLength;
            for (let i = 0; i < len; i++) {
                binary += String.fromCharCode(bytes[i]);
            }
            return btoa(binary);
        }"""

        new_utf8 = """function utf8ToBase64(str) {
            const bytes = new TextEncoder().encode(str);
            let binary = '';
            const CHUNK_SIZE = 0x8000;
            for (let i = 0; i < bytes.length; i += CHUNK_SIZE) {
                binary += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK_SIZE));
            }
            return btoa(binary);
        }"""

        if old_utf8 in content:
            content = content.replace(old_utf8, new_utf8)
            print(f'Updated chunked utf8ToBase64 in {path}')

        # 2. Update saveStoryboardToCloud to single clean commit
        old_save_block = """// 1. Commit public/storyboard.json
                await syncFileToGithub('public/storyboard.json', b64, token, 'עדכון שקפים מתוך סטודיו הענן 🎬');

                // 2. Commit public/default_storyboard.json as backup sync
                try {
                    await syncFileToGithub('public/default_storyboard.json', b64, token, 'סנכרון default_storyboard.json 🎬');
                } catch(e) {
                    console.warn('default_storyboard sync note:', e);
                }"""

        new_save_block = """// Commit public/storyboard.json to trigger single automated deployment
                await syncFileToGithub('public/storyboard.json', b64, token, 'עדכון שקפים מתוך סטודיו הענן 🎬');"""

        if old_save_block in content:
            content = content.replace(old_save_block, new_save_block)
            print(f'Optimized to single commit in {path}')

        # 3. Update initial badge status on load
        old_init_status = """const savedGithubToken = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
        const ghTokenInput = document.getElementById('github-sync-token');
        if (ghTokenInput) {
            ghTokenInput.value = savedGithubToken;
        }"""

        new_init_status = """const savedGithubToken = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
        const ghTokenInput = document.getElementById('github-sync-token');
        if (ghTokenInput) {
            ghTokenInput.value = savedGithubToken;
        }
        if (savedGithubToken) {
            showCloudStatus('סנכרון ענן (GitHub) מחובר ✅');
        } else {
            showCloudStatus('נדרש GitHub Token לסנכרון ענן 🔑');
        }"""

        if old_init_status in content:
            content = content.replace(old_init_status, new_init_status)
            print(f'Updated initial badge status in {path}')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == '__main__':
    polish_sync()
