from flask import Flask, request, jsonify
import MetaTrader5 as mt5
import socket
import logging

DESCRIPTION = "Ordine caricato da Server API"

logging.basicConfig(
    filename="trading_api.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)

if not mt5.initialize():
    logging.error("Errore nell'inizializzazione di MetaTrader5")
    raise RuntimeError("Errore nell'inizializzazione di MetaTrader5")
logging.info("MetaTrader5 inizializzato con successo")

account_info = mt5.account_info()
if account_info:
    logging.info(f"Account info:{account_info}")
else:
    logging.info(f"Errore account:{mt5.last_error()}")

def get_order():
    orders = mt5.orders_get()

    if orders is None or len(orders) == 0:
        message = f"Non esistono ordini: {mt5.last_error()}"
        logging.error(message)
        return {"success": True, "message": message, "orders": []}

    return {"success": True, "orders": orders}

def create_order(symbol, order_type, volume, price=None, sl=None, tp=None, magic=0):

    infoSymbol = mt5.symbol_info(symbol)

    order_type_mapping = {
        'buy': mt5.ORDER_TYPE_BUY,
        'sell': mt5.ORDER_TYPE_SELL,
        'buy_limit': mt5.ORDER_TYPE_BUY_LIMIT,
        'sell_limit': mt5.ORDER_TYPE_SELL_LIMIT,
        'buy_stop': mt5.ORDER_TYPE_BUY_STOP,
        'sell_stop': mt5.ORDER_TYPE_SELL_STOP,
    }

    if order_type not in order_type_mapping:
        message = f"Tipo di ordine '{order_type}' non valido."
        logging.error(message)
        return {"success": False, "message": message}

    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        message = f"Simbolo {symbol} non trovato."
        logging.error(message)
        return {"success": False, "message": message}
    if not symbol_info.visible and not mt5.symbol_select(symbol, True):
        message = f"Errore nell'attivare il simbolo {symbol}."
        logging.error(message)
        return {"success": False, "message": message}

    stops_level = symbol_info.trade_stops_level
    point = symbol_info.point

    if stops_level is None:
        message = f"Impossibile ottenere il livello minimo di stop per il simbolo {symbol}."
        logging.error(message)
        return {"success": False, "message": message}

    if price is None and order_type in ['buy', 'sell']:
        if order_type == 'buy':
            price = mt5.symbol_info_tick(symbol).ask
        elif order_type == 'sell':
            price = mt5.symbol_info_tick(symbol).bid
        logging.info(f"Prezzo calcolato automaticamente per {order_type}: {price}")

    if order_type in ['buy', 'sell']:
        request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": order_type_mapping[order_type],
                "price": price,
                "deviation": 10,
                "magic": magic,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling":mt5.ORDER_FILLING_IOC,
                "comment": DESCRIPTION
            }
    else:
        request = {
            "action": mt5.TRADE_ACTION_DEAL if order_type in ['buy', 'sell'] else mt5.TRADE_ACTION_PENDING,
            "symbol": symbol,
            "volume": volume,
            "type": order_type_mapping[order_type],
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
            "comment": DESCRIPTION
        }

    result = mt5.order_send(request)
    if result is None:
        message = mt5.last_error()
        message = f"Errore nell'invio dell'ordine: {message}"
        logging.error(message)
        return {"success": False, "message": message}

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        message = f"Errore nell'invio dell'ordine: {result.comment}"
        logging.error(message)
        return {"success": False, "message": message}

    logging.info(f"Ordine creato con successo: {result}")
    return {"success": True, "order": result.order}

def update_order(ticket, stop_loss=None, take_profit=None):

    orders = mt5.orders_get(ticket=ticket)
    if not orders:
        message = f"Nessun ordine pendente trovato: {mt5.last_error()}"
        logging.error(message)
        return {"success": False, "message": message}

    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "order": ticket,
        "sl": stop_loss,
        "tp": take_profit,
    }

    result = mt5.order_send(request)
    if result is None:
        message = f"Errore di comunicazione con il server: {mt5.last_error()}"
        logging.error(message)
        return {"success": False, "message": message}

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        message = f"Errore nell'aggiornamento dell'ordine. Retcode: {result.retcode}, Commento: {result.comment}"
        logging.error(message)
        return {"success": False, "message": message}

    logging.info(f"Ordine con ticket {ticket} aggiornato con successo.")
    return {"success": True, "message": "Ordine aggiornato con successo"}

def delete_order(ticket):      
    orders = mt5.orders_get(ticket=ticket)
   
    if not orders:
        message = f"Nessun ordine trovato o errore: {mt5.last_error()}"
        logging.error(message)
        return {"success": False, "message": message}

    logging.info(f"Ordine {ticket} da eliminare")
    
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
    }
    
    result = mt5.order_send(request)
    if result is None:
        error_message = f"Errore di comunicazione con il server: {mt5.last_error()}"
        logging.error(error_message)
        return {"success": False, "message": error_message}

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        error_message = f"Errore nell'annullamento dell'ordine. Retcode: {result.retcode}, Commento: {result.comment}"
        logging.error(error_message)
        return {"success": False, "message": error_message}

    logging.info(f"Ordine con ticket {ticket} cancellato con successo.")
    return {"success": True, "message": "Ordine cancellato con successo"}

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
        take_profit = data.get('take_profit')
        stop_loss = data.get('stop_loss')
        
        update_result = update_order(order_ticket, stop_loss, take_profit)
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

@app.route('/order', methods=['GET'])
def get_order_api():
    try:
        get_order_result = get_order()
       
        if get_order_result["success"]:
            return jsonify({"status": "success", "orders": get_order_result["orders"]}), 200
        else:
            return jsonify({"status": "error", "message":  get_order_result["message"]}), 400
    except Exception as e:
        logging.exception("Errore nella ricezione della lista degli ordini")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Server in esecuzione su IP: {ip_address}")
    logging.info(f"Server in esecuzione su IP: {ip_address}")
    app.run(debug=True, host='0.0.0.0', port=5000)