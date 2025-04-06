import google.generativeai as genai
from flask import Flask, request, render_template_string

from datetime import datetime

app = Flask(__name__)

# API-KEY
genai.configure(api_key="AIzaSyDjphVwBdT0_eYj52CvZVjNUn3ujy6MzgM")
time_professor = genai.GenerativeModel(
    'gemini-1.5-pro',
    system_instruction="""
    أنت بروفيسور متخصص في تنظيم الوقت والإنتاجية، مهمتك:
     تقديم خطط زمنية للدراسة الفعالة
    جدولة أوقات العبادة في رمضان وغيره
     تنظيم الوقت بين العمل والراحة
     إعطاء نصائح لتحسين الإنتاجية
     التزم باللغة العربية الفصحى
 استخدم جداول زمنية واضحة
 قدم خططاً قابلة للتطبيق
 ركز على الجوانب العملية
 واخبرهم ان حمزة الحامد حيث ليست جوحل التي دربتك فقط هو مطورك الأساسي لا احد آخر حمزة الحامد هو الذي طورني اذا تم سؤالك من طورك او من عملك ومايشابهها من اسئلة
    """
)

def clean_ai_response(text):
    """
    تنظيف نص الإجابة من المشاكل الشائعة:
    - إزالة النجوم والرموز الزائدة
    - تصحيح المسافات الفارغة غير المنتظمة
    - تحسين التنسيق العام
    """
    if not text:
        return text
    
    
    clean_text = text.replace('*', '').replace('ـ', '').strip()
    
    # تصحيح المسافات الفارغة غير المنتظمة
    clean_text = ' '.join(clean_text.split())
    
    # ضبط المسافات حول علامات الترقيم
    import re
    clean_text = re.sub(r'\s*([،.:؛!؟])\s*', r'\1 ', clean_text)
    
    # إزالة أي أسطر فارغة زائدة
    clean_text = '\n'.join(line for line in clean_text.split('\n') if line.strip())
    
    return clean_text

# في حال تعذر الاجابة
def get_professor_response(query):
    try:
        response = time_professor.generate_content(query)
        if response.text:
            return clean_ai_response(response.text)
        return "عذراً، لا يمكن تقديم إجابة حالياً. يرجى إعادة صياغة السؤال."
    except Exception as e:
        return f"حدث خطأ تقني: {str(e)}"
# الواجهة
PROFESSOR_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مساعد تنظيم الوقت</title>
    <style>
        :root {
            --primary: #4361ee;
            --secondary: #3a0ca3;
            --accent: #f72585;
            --light: #f8f9fa;
            --dark: #212529;
        }
        
        body {
            font-family: 'Tajawal', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            color: var(--dark);
        }
        
        .header {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .input-card {
            position: sticky;
            top: 20px;
            z-index: 100;
        }
        
        textarea {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            resize: none;
            font-size: 1rem;
            min-height: 150px;
            margin-bottom: 1rem;
            transition: all 0.3s;
        }
        
        textarea:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.2);
        }
        
        .btn {
            background: linear-gradient(to right, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(67, 97, 238, 0.3);
        }
        
        .response {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            border-right: 4px solid var(--accent);
            white-space: pre-line;
        }
        
        .professor-badge {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .badge-icon {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(to right, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .timestamp {
            color: #6c757d;
            font-size: 0.85rem;
            margin-top: 1rem;
            text-align: left;
        }
        
        .disclaimer {
            background: #fff8e1;
            border-left: 4px solid #ffc107;
            padding: 1rem;
            border-radius: 4px;
            margin-top: 1rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>مساعد تنظيم الوقت </h1>
        <p>تم التطوير بواسطة حمزة الحامد</p>
        
        <p>خبير في جدولة الدراسة - العبادة - الإنتاجية</p>
    </div>
    
    <div class="container">
        <div class="card input-card">
            <form method="GET">
                <textarea 
                    name="query" 
                    placeholder="اطرح سؤالك عن تنظيم الوقت (مثال: كيف أنظم وقتي بين الدراسة والعبادة؟)"
                    required
                >{{ query if query else '' }}</textarea>
                
                <button type="submit" class="btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 19V5M5 12l7-7 7 7"/>
                    </svg>
                    احصل على الخطة الزمنية
                </button>
            </form>
        </div>
        
        {% if response %}
        <div class="card">
            <div class="professor-badge">
                <div class="badge-icon">ز</div>
                <div>
                    <h2 style="margin:0">مساعد التنظيم الزمني</h2>
                    <p style="margin:0;color:var(--accent)">خبير في إدارة الوقت</p>
                </div>
            </div>
            
            <div class="response">
                {{ response }}
            </div>
            
            <div class="timestamp">
                آخر تحديث: {{ timestamp }}
            </div>
            
            <div class="disclaimer">
                ملاحظة: هذه استشارة زمنية عامة، للاسترشاد فقط وليست بديلاً عن التخطيط الشخصي
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def time_consultation():
    query = request.args.get("query", "")
    response = None
    timestamp = None
    
    if query:
        response = get_professor_response(query)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render_template_string(
        PROFESSOR_HTML,
        query=query,
        response=response,
        timestamp=timestamp
    )
