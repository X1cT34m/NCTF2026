from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in request.args or 'password' in request.args:
        username = request.args.get('username', '')
        password = request.args.get('password', '')

        if not username or not password:
            login_msg = """
            <div>
                </br>
                <div>这是个登录界面</div>
                </br>
                <div>用户名或密码不能为空</div>
            </div>
            """
        else:
            login_msg = f"""
            <div>
                </br>
                <div>这是个登录界面</div>
                </br>
                <div>Welcome: {username}</div>
            </div>
            """
            render_template_string(login_msg)
    else:
        login_msg = ""

    return render_template("index.html", login_msg=login_msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)