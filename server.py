from flask import Flask, request
import MetaTrader5 as mt5
import socket
import logging
from flask_restx import Api, Resource, fields, reqparse
from protocol import get_account_info, get_orders, get_history_deals_orders, get_history_orders, get_placed_orders, create_order, update_order, delete_order

logging.basicConfig(
    filename="trading_api.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
api = Api(app, version="1.0", title="APIM MT5", description="API per la gestione degli ordini su MetaTrader5")

order_model = api.model('Order', {
    'symbol': fields.String(required=True, description='Simbolo dell\'asset (es. EURUSD)'),
    'type': fields.String(required=True, description='Tipo di ordine (buy, sell, limit, stop)'),
    'volume': fields.Float(required=True, description='Volume dell\'ordine'),
    'price': fields.Float(description='Prezzo (necessario per ordini limit/stop)'),
    'take_profit': fields.Float(description='Livello Take Profit'),
    'stop_loss': fields.Float(description='Livello Stop Loss'),
})

update_model = api.model('UpdateOrder', {
    'ticket': fields.Integer(required=True, description='ID dell\'ordine da aggiornare'),
    'price': fields.Float(description='Nuovo prezzo'),
    'take_profit': fields.Float(description='Nuovo livello Take Profit'),
    'stop_loss': fields.Float(description='Nuovo livello Stop Loss'),
})

history_model = api.model('HistoryRequest', {
    'from_date': fields.String(required=True, description='Data di inizio (formato: YYYY-MM-DD HH:MM:SS)'),
    'to_date': fields.String(description='Data di fine (formato: YYYY-MM-DD HH:MM:SS)'),
})

@api.route('/order')
class CreateOrder(Resource):
    @api.expect(order_model)
    def post(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
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
            
            response = order_result[0] if isinstance(order_result, tuple) else order_result
            data = response.get_json()

            if data["success"]:
                return {"status": "success", "order_id": data["order"]}
            else:
                return {"status": "error", "message": data["message"]}
        except Exception as e:
            logging.exception("Errore nella creazione dell'ordine")
            return {"status": "error", "message": str(e)}

@api.route('/order')
class UpdateOrder(Resource):
    @api.expect(update_model)
    def put(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            data = request.get_json()
            order_ticket = data['ticket']
            price = data.get('price') or None
            take_profit = data.get('take_profit') or None
            stop_loss = data.get('stop_loss') or None
            
            update_result = update_order(order_ticket, price, stop_loss, take_profit)
            response = update_result[0] if isinstance(update_result, tuple) else update_result
            data = response.get_json()

            if data["success"]:
                return {"status": "success", "message": data["message"]}
            else:
                return {"status": "error", "message": data["message"]}
        except Exception as e:
            logging.exception("Errore nell'aggiornamento dell'ordine")
            return {"status": "error", "message": str(e)}

@api.route('/order')
class DeleteOrder(Resource):
    @api.expect(api.model('DeleteRequest', {
        'ticket': fields.Integer(required=True, description='ID dell\'ordine da cancellare'),
    }))
    def delete(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            data = request.get_json()
            order_ticket = data['ticket']
            
            delete_result = delete_order(order_ticket)
            response = delete_result[0] if isinstance(delete_result, tuple) else delete_result
            data = response.get_json()

            if data["success"]:
                return {"status": "success", "message": data["message"]}
            else:
                return {"status": "error", "message": data["message"]}
        except Exception as e:
            logging.exception("Errore nella cancellazione dell'ordine")
            return {"status": "error", "message": str(e)}

@api.route('/order/active')
class ActiveOrders(Resource):
    def get(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            get_active_order_result = get_orders()
            response = get_active_order_result[0] if isinstance(get_active_order_result, tuple) else get_active_order_result
            data = response.get_json()
        
            if data["success"]:
                return {"status": "success", "orders": data["orders"]}
            else:
                return {"status": "error", "message":  data["message"]}
        except Exception as e:
            logging.exception("Errore nella ricezione della lista degli ordini posizionati")
            return {"status": "error", "message": str(e)}

@api.route('/order/placed')
class PlacedOrders(Resource):
    def get(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            get_placed_order_result = get_placed_orders()
            response = get_placed_order_result[0] if isinstance(get_placed_order_result, tuple) else get_placed_order_result
            data = response.get_json()
        
            if data["success"]:
                return {"status": "success", "orders": data["orders"]}
            else:
                return {"status": "error", "message":  data["message"]}
        except Exception as e:
            logging.exception("Errore nella ricezione della lista degli ordini pendenti")
            return {"status": "error", "message": str(e)}

@api.route('/order/history')
class HistoryOrders(Resource):
    @api.expect(history_model)
    def post(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            data = request.get_json()
            from_date = data.get('from_date')
            to_date = data.get('to_date') or None

            get_history_order_result = get_history_orders(from_date, to_date)
            response = get_history_order_result[0] if isinstance(get_history_order_result, tuple) else get_history_order_result
            data = response.get_json()
        
            if data["success"]:
                return {"status": "success", "orders": data["orders"]}
            else:
                return {"status": "error", "message":  data["message"]}
        except Exception as e:
            logging.exception("Errore nella ricezione della cronologia degli ordini")
            return {"status": "error", "message": str(e)}

@api.route('/order/historyDeals')
class HistoryDealsOrders(Resource):
    @api.expect(history_model)
    def post(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}
            
            data = request.get_json()
            from_date = data.get('from_date')
            to_date = data.get('to_date') or None

            get_history_order_result = get_history_deals_orders(from_date, to_date)
            response = get_history_order_result[0] if isinstance(get_history_order_result, tuple) else get_history_order_result
            data = response.get_json()

            if data["success"]:
                return {"status": "success", "orders": data["orders"]}
            else:
                return {"status": "error", "message":  data["message"]}
        except Exception as e:
            logging.exception("Errore nella ricezione della cronologia degli ordini")
            return {"status": "error", "message": str(e)}

@api.route('/account')
class AccountInfo(Resource):
    def get(self):
        try:
            if not mt5.initialize():
                return {"success": False, "message": f"Errore inizializzazione MT5: {mt5.last_error()}"}

            getInfo_result = get_account_info()
            response = getInfo_result[0] if isinstance(getInfo_result, tuple) else getInfo_result
            data = response.get_json()
        
            if data["success"]:
                return {"status": "success", "info": data["info"]}
            else:
                return {"status": "error", "message":  data["message"]}
        except Exception as e:
            logging.exception("Errore nella ricezione delle informazioni dell' account")
            return {"status": "error", "message": str(e)}

if __name__ == '__main__':
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Server in esecuzione su IP: {ip_address}")
    logging.info(f"Server in esecuzione su IP: {ip_address}")
    app.run(debug=True, host='0.0.0.0', port=5000)