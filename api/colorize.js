import fs from 'fs';
import path from 'path';

export const config = {
  maxDuration: 60,
};

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { image_path, image_base64, api_key } = req.body;
    const apiKey = api_key || process.env.GEMINI_API_KEY || "AQ.Ab8RN6K7mm1arshT3nkHmTgDbFkFzydZjaGYdn6myFJmJEFgAg";

    let b64Data = image_base64;

    if (!b64Data && image_path) {
      // Read from public directory
      const cleanPath = image_path.split('?')[0].replace(/^\//, '');
      const fullPath = path.join(process.cwd(), 'public', cleanPath);
      if (fs.existsSync(fullPath)) {
        b64Data = fs.readFileSync(fullPath).toString('base64');
      } else {
        return res.status(404).json({ error: `Image not found at ${cleanPath}` });
      }
    }

    if (!b64Data) {
      return res.status(400).json({ error: 'Missing image data' });
    }

    // Call Gemini 2.5 Flash Image with comprehensive edge-to-edge prompt
    const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key=${apiKey}`;
    const prompt = (
      "Fully and completely colorize every single part of this vintage photograph in high resolution with vibrant, natural colors.\n" +
      "CRITICAL REQUIREMENTS:\n" +
      "1. Colorize EVERY SINGLE PERSON across the entire frame without exception, including all people on the left side, right side, and background. Give everyone realistic, warm, healthy human skin tones and natural hair color.\n" +
      "2. Colorize all clothing: suits, floral shirts, striped tops, patterned blouses, and dresses for ALL guests and attendees.\n" +
      "3. Colorize all elements in the scene: the table, tablecloth, glasses, food, background curtains, wall, and lighting.\n" +
      "4. Do NOT leave any person, corner, face, or background in grayscale or sepia. Ensure 100% complete full-color coverage across the entire photograph edge-to-edge."
    );

    const payload = {
      contents: [{
        parts: [
          { text: prompt },
          { inline_data: { mime_type: "image/jpeg", data: b64Data } }
        ]
      }]
    };

    const geminiRes = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      return res.status(502).json({ error: `Gemini API error: ${errText}` });
    }

    const data = await geminiRes.json();
    let outB64 = null;

    for (const c of data.candidates || []) {
      for (const p of c.content?.parts || []) {
        if (p.inlineData?.data) {
          outB64 = p.inlineData.data;
          break;
        } else if (p.inline_data?.data) {
          outB64 = p.inline_data.data;
          break;
        }
      }
    }

    if (!outB64) {
      return res.status(500).json({ error: 'No colorized image returned from AI model' });
    }

    // Return the colorized image as a data URI or base64 so it can be viewed and saved instantly in the browser!
    const dataUri = `data:image/png;base64,${outB64}`;
    return res.status(200).json({
      status: 'ok',
      colorized_data_url: dataUri,
      message: 'התמונה נצבעה בהצלחה מלאה !'
    });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
