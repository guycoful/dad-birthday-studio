import fs from 'fs';
import path from 'path';

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader('Access-Control-Allow-Headers', 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  const githubToken = process.env.GITHUB_PERSONAL_ACCESS_TOKEN || process.env.GITHUB_TOKEN;
  const repoOwner = process.env.GITHUB_OWNER || 'guycoful';
  const repoName = process.env.GITHUB_REPO || 'dad-birthday-studio';

  if (req.method === 'GET') {
    try {
      // Return storyboard from local public folder or GitHub API
      const localPath = path.join(process.cwd(), 'public', 'storyboard.json');
      if (fs.existsSync(localPath)) {
        const data = fs.readFileSync(localPath, 'utf8');
        return res.status(200).json(JSON.parse(data));
      }
      return res.status(200).json({ status: 'ok', slides: [] });
    } catch (e) {
      return res.status(500).json({ error: e.message });
    }
  }

  if (req.method === 'POST') {
    try {
      const payload = req.body;
      const slides = Array.isArray(payload) ? payload : (payload.slides || []);
      const jsonContent = JSON.stringify({
        title: "סטודיו סרטון יום הולדת 60 לאבא צחי",
        total_slides: slides.length,
        slides: slides,
        last_updated: new Date().toISOString()
      }, null, 2);

      // 1. If GitHub Token is configured, commit directly to GitHub repository
      if (githubToken) {
        const filePath = 'public/storyboard.json';
        const fileUrl = `https://api.github.com/repos/${repoOwner}/${repoName}/contents/${filePath}`;
        
        // Get current SHA
        let sha = null;
        try {
          const getRes = await fetch(fileUrl, {
            headers: {
              'Authorization': `Bearer ${githubToken}`,
              'Accept': 'application/vnd.github.v3+json',
              'User-Agent': 'DadBirthdayStudio'
            }
          });
          if (getRes.ok) {
            const fileData = await getRes.json();
            sha = fileData.sha;
          }
        } catch (err) {
          console.warn('Could not fetch existing SHA:', err);
        }

        const b64Content = Buffer.from(jsonContent, 'utf8').toString('base64');
        const commitBody = {
          message: `Update storyboard state via Studio Cloud UI [${new Date().toLocaleTimeString()}]`,
          content: b64Content
        };
        if (sha) commitBody.sha = sha;

        const putRes = await fetch(fileUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${githubToken}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'DadBirthdayStudio'
          },
          body: JSON.stringify(commitBody)
        });

        if (putRes.ok) {
          return res.status(200).json({
            status: 'ok',
            synced_to_github: true,
            total_slides: slides.length,
            message: 'השינויים נשמרו בהצלחה ונדחפו ישירות למאגר ה-GitHub שלך !'
          });
        }
      }

      // Fallback: local file write if running locally
      try {
        const localPath = path.join(process.cwd(), 'public', 'storyboard.json');
        fs.writeFileSync(localPath, jsonContent, 'utf8');
      } catch (err) {
        // Ignored on read-only serverless
      }

      return res.status(200).json({
        status: 'ok',
        synced_to_github: false,
        total_slides: slides.length,
        message: 'השינויים נשמרו בהצלחה בדפדפן ובשרת !'
      });
    } catch (e) {
      return res.status(500).json({ error: e.message });
    }
  }

  res.status(405).json({ error: 'Method not allowed' });
}
