import requests

GEMINI_API_KEY = 'AIzaSyAkwXwDtQSHOiJoxw8UJIcFuZlYHzqb1Bw'

SYSTEM_PROMPT = """Write a blog post about: {user_question}

Include these REAL images in content:
<img src="https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600">
<img src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600">

At the END add working videos:
<div class="video-section">
<h3>Video Resources</h3>
<a href="https://www.youtube.com/watch?v=UGR0p7_30hM" target="_blank" class="video-btn">Flutter Tutorial for Beginners</a>
<a href="https://www.youtube.com/watch?v=5ajwWryN6gQ" target="_blank" class="video-btn">Flutter Full Course</a>
</div>

Write the post:"""

def get_ai_response(user_question, blog_context):
    url = 'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=' + GEMINI_API_KEY
    context_text = blog_context if blog_context else ""
    full_prompt = SYSTEM_PROMPT.format(user_question=user_question) + "\n\n" + context_text
    data = {"contents": [{"parts": [{"text": full_prompt}]}], "generationConfig": {"temperature": 0.8, "maxOutputTokens": 4096}}
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if 'candidates' in result:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "Error: " + str(result)
    except Exception as e:
        return "Error: " + str(e)