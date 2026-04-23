import json, os, time
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# 内存存储（Railway 免费版重启会清空，生产用 Railway 的 PostgreSQL 插件）
DATA = {
    "menu": [
        {"id":1,"name":"羊肉串","price":8,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1529193591184-b1d58069ecdd?w=200&q=80"},
        {"id":2,"name":"牛肉串","price":10,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1558030006-450675393462?w=200&q=80"},
        {"id":3,"name":"猪五花","price":6,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1544025162-d76694265947?w=200&q=80"},
        {"id":4,"name":"鸡翅","price":12,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=200&q=80"},
        {"id":5,"name":"大虾","price":15,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=200&q=80"},
        {"id":6,"name":"生蚝","price":12,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1606731219412-3b1e7a5e3e3e?w=200&q=80"},
        {"id":7,"name":"金针菇","price":5,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=200&q=80"},
        {"id":8,"name":"玉米","price":6,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=200&q=80"},
        {"id":9,"name":"茄子","price":5,"cat":"招牌烤肉","img":"https://images.unsplash.com/photo-1615484477778-ca3b77940c25?w=200&q=80"},
        {"id":10,"name":"青岛啤酒","price":8,"cat":"酒水","img":"https://images.unsplash.com/photo-1608270586620-248524c67de9?w=200&q=80"},
        {"id":11,"name":"雪花啤酒","price":7,"cat":"酒水","img":"https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=200&q=80"},
        {"id":12,"name":"可乐","price":5,"cat":"饮料","img":"https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=200&q=80"},
        {"id":13,"name":"雪碧","price":5,"cat":"饮料","img":"https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=200&q=80"},
        {"id":14,"name":"矿泉水","price":3,"cat":"饮料","img":"https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=200&q=80"},
    ],
    "orders": {},
    "next_id": 12,
    "cats": ["招牌烤肉", "酒水", "饮料"],
    "shop": {"phone": "", "qrcode": ""}
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
            "price": float(b['price']), "cat": b.get('cat','其他'),
            "img": b.get('img','')}
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

@app.route('/api/cats', methods=['GET'])
def get_cats(): return jsonify(DATA['cats'])

@app.route('/api/cats/add', methods=['POST'])
def add_cat():
    name = request.json.get('name','').strip()
    if name and name not in DATA['cats']:
        DATA['cats'].append(name)
    return jsonify(DATA['cats'])

@app.route('/api/cats/delete', methods=['POST'])
def delete_cat():
    name = request.json.get('name','')
    if name in DATA['cats']: DATA['cats'].remove(name)
    return jsonify(DATA['cats'])

@app.route('/api/shop', methods=['GET'])
def get_shop(): return jsonify(DATA['shop'])

@app.route('/api/shop/update', methods=['POST'])
def update_shop():
    b = request.json
    DATA['shop'].update({k:v for k,v in b.items() if k in ('phone','qrcode')})
    return jsonify({'ok': True})

@app.route('/ping', methods=['GET'])
def ping(): return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
