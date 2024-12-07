from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, Namespace, join_room, leave_room
import yfinance as yf
import json
from datetime import datetime, timedelta
import asyncio
import math



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite 데이터베이스
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=False, cors_allowed_origins='*')


app.secret_key = 'thisiskey'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=30)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    ticker_history = db.Column(db.Text, nullable=True)  # 티커 리스트 저장
    name_history = db.Column(db.Text, nullable=True)    # 이름 리스트 저장

with app.app_context():
    db.create_all()

tickers = {}

class ChartNamespace(Namespace):
    def on_connect(self):
        print("Chart Client connected.", request.sid, request.remote_addr)
        socketio.emit('welcome', request.remote_addr, namespace='/chart', to=request.sid)

    def on_disconnect(self):
        print("Chart Client disconnected.", request.sid, request.remote_addr)
        leave_room(tickers[request.sid])
        del tickers[request.sid]

    def on_join(self, ticker):
        dat = yf.Ticker(ticker)
        test = dat.info
        if test['trailingPegRatio'] == None:
            print("티커를 찾지 못했습니다.")
            socketio.emit('notFound', namespace='/chart', to=request.sid)
        else:
            if ticker != '':
                join_room(ticker)
                tickers[request.sid] = ticker


# @socketio.on('connect', namespace='/header')
# def handle_connect():
#     print("Header Client connected.", request.sid, request.remote_addr)

# @socketio.on('disconnect', namespace='/header')
# def handle_disconnect():
#     leave_room(ticker)
    
# @socketio.on('join', namespace='/header')
# def handle_join(ticker):
#     join_room(ticker)


# @app.route("/SignUp", methods=['POST'])
# def get_Data():
#     return "you are an idiot!"

# 주식 데이터 삭제 후 새로 추가

@app.route('/api/add', methods=['POST'])
def add_stock():
    data = request.json
    ticker = data.get('ticker')
    dat = yf.Ticker(ticker)
    name = dat.info['shortName']

    user = User.query.filter_by(email=session['user']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 400
    
    try:
        history_ticker = json.loads(user.ticker_history) if user.ticker_history else []
        if ticker in history_ticker: history_ticker.remove(ticker)
        history_ticker.append(ticker)
        history_ticker = history_ticker[-10:]
        user.ticker_history = json.dumps(history_ticker)

        history_name = json.loads(user.name_history) if user.name_history else []
        if ticker in history_name: history_name.remove(name)
        history_name.append(name)
        history_name = history_name[-10:]
        user.name_history = json.dumps(history_name)

        db.session.commit()
        return jsonify({'message': 'Success.'}), 201
    except:
        return jsonify({'message': 'Failed'}), 400


# @app.route('/api/recent', methods=['GET'])
# def recent_stocks():
    

# @app.route('/api/remove', methods=['GET'])
# def remove_stocks():
#     data = request.json
#     ticker = data.get('ticker')
#     user = User.query.filter_by(email=session['user']).first()
#     if not user:
#         return jsonify({'message': 'User not found'}), 400
    


    
@app.route('/api/register', methods=['POST'])
def get_Data():
    data = request.json
    username = data.get('name')
    email = data.get('email')
    password = data.get('password')
    print(username, email, password)

    # 유효성 검사
    # if not username or not email or not password:
    #     return jsonify({'message': 'All fields are required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
    # if User.query.filter_by(username=username).first():
    #     return jsonify({'message': 'Username already exists'}), 400

    # 비밀번호 해싱
    hashed_password = generate_password_hash(password)

    # 사용자 저장
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print("db 추가됨!")

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 사용자 인증
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    session['user'] = email
    return jsonify({'message': f'Welcome!', 'username': user.username}), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)  # 세션에서 사용자 정보 제거
    return jsonify({'message': 'Logged out successfully!'}), 200

@app.route('/api/protected', methods=['GET'])
def protected():
    if 'user' in session:  # 세션 유효성 확인
        user = User.query.filter_by(email=session['user']).first()
        return jsonify({'username': user.username, "email": user.email, 'ticker': list(reversed(json.loads(user.ticker_history))), 'name': list(reversed(json.loads(user.name_history)))}), 200
    else:
        return jsonify({'message': 'Unauthorized'}), 401

def get_chart_data():
    print("서버 시작됨!!")
    while True:
        try:
            if len(tickers) != 0:
                print(tickers)
                roomData = set(tickers.values())
                ticker_info = yf.Tickers(' '.join(roomData))
                stock_data = yf.download(roomData, period=None, interval='1m', group_by='ticker')
                for ticker in roomData:
                    print(roomData)
                    if len(roomData) == 1: ticker_data = stock_data
                    else: ticker_data = stock_data[ticker]
                    header_info = ticker_info.tickers[ticker].info
                    initialData = []
                    for index, row in ticker_data.iterrows():
                        if not math.isnan(row['Open']):
                            data = {
                                "date": str(index),
                                "open": row['Open'],
                                "low": row['Low'],
                                "high": row['High'],
                                "close": row['Close'],
                                "volume": row['Volume']
                            }
                            initialData.append(data)
                    event = {
                        'name': header_info['shortName'],
                        'current': 0.00,
                        'diff': 0.00,
                        '%': 0.00,
                        'isAfter': 1,
                        'afterClosed': 0.00,
                        'diff2': 0.00,
                        '%2': 0.00
                    }
                    socketio.emit('chart', json.dumps(initialData), namespace='/chart', to=ticker)
                    try:
                        after = yf.Ticker(ticker).history(prepost=True, period=None, interval='1m')
                        afterData = []
                        for index, row in after.iterrows():
                            if not math.isnan(row['Open']):
                                data = {
                                    "date": str(index),
                                    "open": row['Open'],
                                    "low": row['Low'],
                                    "high": row['High'],
                                    "close": row['Close'],
                                    "volume": row['Volume']
                                }
                                afterData.append(data)
                        event['current'] = header_info['currentPrice']
                        event['diff'] = float(header_info['currentPrice']) - float(header_info['previousClose'])
                        event['%'] = event['diff'] / float(header_info['previousClose']) * 100
                        event['afterClosed'] = afterData[-1]['close']
                        event['diff2'] = afterData[-1]['close'] - float(header_info['currentPrice'])
                        event['%2'] = event['diff2'] / float(header_info['currentPrice']) * 100
                        socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
                    except: 
                        event['current'] = float(initialData[-1]['close'])
                        event['diff'] = float(initialData[-1]['close']) - float(header_info['previousClose'])
                        # print(initialData[-1]['date'])
                        # diff_data = ''
                        # for entry in initialData:
                        #     if entry['date'] == str(datetime.fromisoformat(initialData[-1]['date']) - timedelta(days=1)):
                        #         diff_data = entry['close']
                        #         event['diff'] = float(event['current']) - float(diff_data)
                        #         break
                        event['%'] = event['diff'] / float(header_info['previousClose']) * 100
                        event['isAfter'] = 0
                        socketio.emit('header', json.dumps(event), namespace='/chart', to=ticker)
                        
                    #socketio.emit('header', json.dumps(initialData), namespace='/header', to=ticker)
        except Exception as e:
            print('err :', e)
        socketio.sleep(1)

# @socketio.on('connect', namespace='/*')
# def handle_connect():
#     print("Client connected.")

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Client disconnected.")

socketio.on_namespace(ChartNamespace('/chart'))

if __name__ == '__main__':
    socketio.start_background_task(get_chart_data)
    socketio.run(app, host='localhost', port=5000)
