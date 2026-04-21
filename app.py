import json, os, time
from flask import Flask, request, jsonify

app = Flask(__name__)

# 内存存储（Railway 免费版重启会清空，生产用 Railway 的 PostgreSQL 插件）
DATA = {
    "menu": [
        {"id":1,"name":"羊肉串","price":8,"cat":"冻品"},
        {"id":2,"name":"牛肉串","price":10,"cat":"冻品"},
        {"id":3,"name":"猪五花","price":6,"cat":"冻品"},
        {"id":4,"name":"鸡翅","price":12,"cat":"鲜货"},
        {"id":5,"name":"大虾","price":15,"cat":"鲜货"},
        {"id":6,"name":"生蚝","price":12,"cat":"鲜货"},
        {"id":7,"name":"金针菇","price":5,"cat":"蔬菜"},
        {"id":8,"name":"玉米","price":6,"cat":"蔬菜"},
        {"id":9,"name":"茄子","price":5,"cat":"蔬菜"},
        {"id":10,"name":"啤酒","price":8,"cat":"酒水"},
        {"id":11,"name":"饮料","price":5,"cat":"酒水"},
    ],
    "orders": {},
    "next_id": 12
}

def cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@app.after_request
def after(resp): return cors(resp)

@app.route('/api/menu', methods=['GET'])
def get_menu(): return jsonify(DATA['menu'])

@app.route('/api/orders', methods=['GET'])
def get_orders(): return jsonify(DATA['orders'])

@app.route('/api/order', methods=['GET'])
def get_order():
    table = request.args.get('table','')
    return jsonify(DATA['orders'].get(table, {}))

@app.route('/api/menu/add', methods=['POST'])
def add_menu():
    b = request.json
    item = {"id": DATA['next_id'], "name": b['name'],
            "price": float(b['price']), "cat": b.get('cat','其他')}
    DATA['menu'].append(item); DATA['next_id'] += 1
    return jsonify(item)

@app.route('/api/menu/update', methods=['POST'])
def update_menu():
    b = request.json
    for i, m in enumerate(DATA['menu']):
        if m['id'] == b['id']:
            DATA['menu'][i].update({k:v for k,v in b.items() if k!='id'}); break
    return jsonify({'ok': True})

@app.route('/api/menu/delete', methods=['POST'])
def delete_menu():
    DATA['menu'] = [m for m in DATA['menu'] if m['id'] != request.json['id']]
    return jsonify({'ok': True})

@app.route('/api/order/submit', methods=['POST'])
def submit_order():
    b = request.json
    table = b['table']
    note = b.get('note', '')
    menu_prices = {m['name']: m['price'] for m in DATA['menu']}
    total = sum(menu_prices.get(n, 0) * q for n, q in b['items'].items())
    record = {'items': b['items'], 'status': 'pending',
              'time': time.strftime('%H:%M'), 'note': note, 'total': total}
    # 同一桌用列表存多次点单
    if table not in DATA['orders']:
        DATA['orders'][table] = []
    DATA['orders'][table].append(record)
    print(f"🔔 新订单: {table} {b['items']}")
    return jsonify({'ok': True})

@app.route('/api/order/status', methods=['POST'])
def order_status():
    b = request.json
    table, idx = b['table'], b.get('idx', 0)
    if table in DATA['orders'] and idx < len(DATA['orders'][table]):
        DATA['orders'][table][idx]['status'] = b['status']
    return jsonify({'ok': True})

@app.route('/api/order/delete', methods=['POST'])
def delete_order():
    b = request.json
    table, idx = b.get('table',''), b.get('idx', None)
    if table in DATA['orders']:
        if idx is not None:
            DATA['orders'][table].pop(idx)
            if not DATA['orders'][table]:
                del DATA['orders'][table]
        else:
            del DATA['orders'][table]
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
