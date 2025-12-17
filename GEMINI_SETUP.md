# 🔑 Gemini API Setup Guide

## Quick Setup

### 1. Get Your API Key
Visit: https://aistudio.google.com/app/apikey

Click "Create API Key" (it's FREE!)

### 2. Add to .env File
In `backend/.env`:
```bash
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### 3. Restart Server
```bash
# Kill the server (Ctrl+C)
# Start again
cd backend
uvicorn app.main:app --reload
```

---

## Available Models (as of Dec 2024)

Choose ONE for `GEMINI_MODEL`:

### Recommended:
- `gemini-2.0-flash-exp` - Latest, fastest, best (experimental)
- `gemini-1.5-flash` - Stable, fast, good
- `gemini-1.5-pro` - More powerful, slower

### Testing:
```bash
# Test if your model works:
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=YOUR_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"contents":[{"parts":[{"text":"Say hello"}]}]}'
```

---

## Common Errors

### Error 429 - Rate Limit
```
✗ Rate limit exceeded (429)
```
**Fix:** 
- Free tier: 15 requests per minute
- Wait 1 minute and try again
- Or upgrade to paid tier

### Error 404 - Model Not Found
```
✗ Model not found (404)
```
**Fix:**
- Check model name spelling in .env
- Use one of: `gemini-2.0-flash-exp`, `gemini-1.5-flash`, `gemini-1.5-pro`

### Error 403 - Invalid Key
```
✗ Invalid API key (403)
```
**Fix:**
- Check your API key in .env
- Make sure it's the full key (starts with "AI...")
- No quotes around the key

---

## Rate Limits

### Free Tier:
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per minute

### Paid Tier:
- 1,000 requests per minute
- Higher token limits
- More reliable

---

## Current Configuration

Your settings:
```bash
GEMINI_API_KEY=<your_key>
GEMINI_MODEL=gemini-2.0-flash-exp
```

The system will:
1. Use ONLY this model
2. Show clear error if it fails
3. Never try other models automatically

---

## Troubleshooting

### Check if API key is set:
```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Key:', os.getenv('GEMINI_API_KEY')[:20] if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

### Test the model:
```bash
cd backend
python -c "
import os, requests
from dotenv import load_dotenv
load_dotenv()
key = os.getenv('GEMINI_API_KEY')
model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
r = requests.post(url, params={'key': key}, json={'contents':[{'parts':[{'text':'Hi'}]}]})
print(f'Status: {r.status_code}')
print(f'Response: {r.text[:200]}')
"
```

---

## What Works Now

✅ Uses ONLY your configured model  
✅ Clear error messages  
✅ No automatic fallbacks  
✅ Fast and simple  

---

## Need Help?

1. **Check logs** - Look for `[PromptWorkflow]` messages
2. **Verify API key** - Make sure it's valid
3. **Check rate limits** - Wait if you hit 429
4. **Try different model** - Change GEMINI_MODEL in .env

---

Happy analyzing! 🚀

