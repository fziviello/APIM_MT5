from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import socket
import logging
from protocol import get_account_info, get_orders, get_history_deals_orders, get_history_orders, get_placed_orders, create_order, update_order, delete_order

logging.basicConfig(
    filename="trading_api.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)

@app.route('/order', methods=['POST'])
def create_order_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
        
        data = request.get_json()
        symbol = data['symbol']
        order_type = data['type']
        volume = data['volume']
        
        if order_type in ['buy', 'sell']:
            order_result = create_order(symbol, order_type, volume)
        else:
            price = data.get('price')
            take_profit = data.get('take_profit')
            stop_loss = data.get('stop_loss')
            order_result = create_order(symbol, order_type, volume, price, stop_loss, take_profit)
        
        if order_result["success"]:
            return jsonify({"status": "success", "order_id": order_result["order"]}), 200
        else:
            return jsonify({"status": "error", "message": order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella creazione dell'ordine")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/update', methods=['PUT'])
def update_order_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
        
        data = request.get_json()
        order_ticket = data['ticket']
        price = data.get('price') or None
        take_profit = data.get('take_profit') or None
        stop_loss = data.get('stop_loss') or None
        
        update_result = update_order(order_ticket, price, stop_loss, take_profit)
        if update_result["success"]:
            return jsonify({"status": "success", "message": update_result["message"]}), 200
        else:
            return jsonify({"status": "error", "message": update_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nell'aggiornamento dell'ordine")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/delete', methods=['DELETE'])
def delete_order_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
        
        data = request.get_json()
        order_ticket = data['ticket']
        
        delete_result = delete_order(order_ticket)
        if delete_result["success"]:
            return jsonify({"status": "success", "message": delete_result["message"]}), 200
        else:
            return jsonify({"status": "error", "message": delete_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella cancellazione dell'ordine")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/active', methods=['GET'])
def get_orders_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
         
        get_placed_order_result = get_orders()
       
        if get_placed_order_result["success"]:
            return jsonify({"status": "success", "orders": get_placed_order_result["orders"]}), 200
        else:
            return jsonify({"status": "error", "message":  get_placed_order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione della lista degli ordini posizionati")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/placed', methods=['GET'])
def get_placed_orders_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
                
        get_placed_order_result = get_placed_orders()
       
        if get_placed_order_result["success"]:
            return jsonify({"status": "success", "orders": get_placed_order_result["orders"]}), 200
        else:
            return jsonify({"status": "error", "message":  get_placed_order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione della lista degli ordini pendenti")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/history', methods=['POST'])
def get_history_orders_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
         
        data = request.get_json()
        from_date = data.get('from_date')
        to_date = data.get('to_date') or None

        get_history_order_result = get_history_orders(from_date, to_date)
       
        if get_history_order_result["success"]:
            return jsonify({"status": "success", "orders": get_history_order_result["orders"]}), 200
        else:
            return jsonify({"status": "error", "message":  get_history_order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione della cronologia degli ordini")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/order/historyDeals', methods=['POST'])
def get_history_deals_orders_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500
         
        data = request.get_json()
        from_date = data.get('from_date')
        to_date = data.get('to_date') or None

        get_history_order_result = get_history_deals_orders(from_date, to_date)
       
        if get_history_order_result["success"]:
            return jsonify({"status": "success", "orders": get_history_order_result["orders"]}), 200
        else:
            return jsonify({"status": "error", "message":  get_history_order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione della cronologia degli ordini")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/account/info', methods=['GET'])
def get_account_info_api():
    try:
        if not mt5.initialize():
            return jsonify({"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}), 500

        getInfo_result = get_account_info()
       
        if getInfo_result["success"]:
            return jsonify({"status": "success", "info": getInfo_result["info"]}), 200
        else:
            return jsonify({"status": "error", "message":  getInfo_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione delle informazioni dell' account")
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Server in esecuzione su IP: {ip_address}")
    logging.info(f"Server in esecuzione su IP: {ip_address}")
    app.run(debug=True, host='0.0.0.0', port=5000)