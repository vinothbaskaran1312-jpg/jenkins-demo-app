#cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hello from Jenkins CI/CD Pipeline! v1.0</h1>'

@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '1.0'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
#EOF