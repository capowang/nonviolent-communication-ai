from openai import OpenAI
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "sk-9106aa79fbe8424595078b861140c00d"),  
    base_url=os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>非暴力沟通 AI 助手</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .chat { max-width: 600px; margin: 0 auto; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background: #e3f2fd; text-align: right; }
            .ai { background: #f1f8e9; }
            input, button { margin: 10px 0; padding: 10px; }
            input { width: 70%; }
        </style>
    </head>
    <body>
        <div class="chat">
            <h1>非暴力沟通 AI 助手</h1>
            <div id="messages"></div>
            <input type="text" id="input" placeholder="输入你的问题...">
            <button onclick="sendMessage()">发送</button>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById('input');
                const message = input.value;
                if (!message) return;
                
                // 显示用户消息
                addMessage(message, 'user');
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    
                    const data = await response.json();
                    addMessage(data.response, 'ai');
                } catch (error) {
                    addMessage('抱歉，出现错误，请稍后再试。', 'ai');
                }
            }
            
            function addMessage(text, sender) {
                const messages = document.getElementById('messages');
                const div = document.createElement('div');
                div.className = 'message ' + sender;
                div.textContent = text;
                messages.appendChild(div);
                messages.scrollTop = messages.scrollHeight;
            }
            
            // 回车发送
            document.getElementById('input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400

        # 调用通义千问 API
        response = client.chat.completions.create(
            model="qwen-max",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位熟悉《非暴力沟通》的老师，请结合书中的内容和实例，耐心讲解，风格亲切。"
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            stream=False,
        )
        
        ai_response = response.choices[0].message.content
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 
