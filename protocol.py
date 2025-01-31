from flask import jsonify
import MetaTrader5 as mt5
import logging
from datetime import datetime

DESCRIPTION = "Ordine caricato da Server API"

def get_account_info():
    account_info = mt5.account_info()
    if account_info:
        account_info_dict = {
            "login": account_info.login,
            "trade_mode": account_info.trade_mode,
            "leverage": account_info.leverage,
            "limit_orders": account_info.limit_orders,
            "margin_so_mode": account_info.margin_so_mode,
            "trade_allowed": account_info.trade_allowed,
            "trade_expert": account_info.trade_expert,
            "margin_mode": account_info.margin_mode,
            "currency_digits": account_info.currency_digits,
            "fifo_close": account_info.fifo_close,
            "balance": account_info.balance,
            "credit": account_info.credit,
            "profit": account_info.profit,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "margin_free": account_info.margin_free,
            "margin_level": account_info.margin_level,
            "margin_so_call": account_info.margin_so_call,
            "margin_so_so": account_info.margin_so_so,
            "margin_initial": account_info.margin_initial,
            "margin_maintenance": account_info.margin_maintenance,
            "assets": account_info.assets,
            "commission_blocked": account_info.commission_blocked,
            "name": account_info.name,
            "server": account_info.server,
            "currency": account_info.currency,
            "company": account_info.company
        }

        logging.info(f"Account info: {account_info_dict}")
        return jsonify({"success": True, "info": account_info_dict}), 200
    else:
        error_message = f"Errore account: {mt5.last_error()}"
        logging.error(error_message)
        return jsonify({"success": False, "message": error_message}), 500

def get_orders():
    orders = mt5.positions_get()

    if orders is None or len(orders) == 0:
        message = "Non esistono ordini pendenti" if orders is None else f"Errore: {mt5.last_error()}"
        logging.error(message)
        return jsonify({"success": True, "message": message, "orders": []}), 200

    orders_readable = []
    for order in orders:
        orders_readable.append({
            "ticket": order.ticket,
            "time_setup": order.time,
            "symbol": order.symbol,
            "volume": order.volume,
            "price_open": order.price_open,
            "sl": order.sl,
            "tp": order.tp,
            "price_current": order.price_current,
            "profit": order.profit,
            "comment": order.comment
        })

    return jsonify({"success": True, "orders": orders_readable}), 200

def get_history_deals_orders(from_date, to_date):
    try:
        from_date_dt = datetime.strptime(from_date, '%d/%m/%Y')
        to_date_dt = datetime.strptime(to_date, '%d/%m/%Y')
        deals_orders = mt5.history_deals_get(from_date_dt, to_date_dt)

        if deals_orders is None or len(deals_orders) == 0:
            message = "Nessuna cronologia ordini trovata" if deals_orders is None else f"Errore: {mt5.last_error()}"
            logging.error(message)
            return jsonify({"success": True, "message": message, "orders": []}), 200

        orders_readable = []
        for deal in deals_orders:
            orders_readable.append({
                "ticket": deal.ticket,
                "order": deal.order,
                "time": deal.time,
                "time_msc": deal.time_msc,
                "type": deal.type,
                "entry": deal.entry,
                "magic": deal.magic,
                "position_id": deal.position_id,
                "reason": deal.reason,
                "volume": deal.volume,
                "price": deal.price,
                "commission": deal.commission,
                "swap": deal.swap,
                "profit": deal.profit,
                "fee": deal.fee,
                "symbol": deal.symbol,
                "comment": deal.comment,
                "external_id": deal.external_id,
            })

        return jsonify({"success": True, "orders": orders_readable}), 200

    except Exception as e:
        logging.error(f"Errore nella funzione get_history_deals_orders: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_history_orders(from_date, to_date):
    try:

        from_date_dt = datetime.strptime(from_date, '%d/%m/%Y')
        to_date_dt = datetime.strptime(to_date, '%d/%m/%Y')
        orders = mt5.history_orders_get(from_date_dt, to_date_dt)

        if orders is None or len(orders) == 0:
            message = "Nessuna cronologia ordini trovata" if orders is None else f"Errore: {mt5.last_error()}"
            logging.error(message)
            return jsonify({"success": True, "message": message, "orders": []}), 200

        orders_readable = []
        for order in orders:
            orders_readable.append({
                "ticket": order.ticket,
                "time_setup": order.time_setup,
                "time_setup_msc": order.time_setup_msc,
                "time_done": order.time_done,
                "time_done_msc": order.time_done_msc,
                "time_expiration": order.time_expiration,
                "type": order.type,
                "type_time": order.type_time,
                "type_filling": order.type_filling,
                "state": order.state,
                "magic": order.magic,
                "position_id": order.position_id,
                "reason": order.reason,
                "volume_initial": order.volume_initial,
                "volume_current": order.volume_current,
                "price_open": order.price_open,
                "sl": order.sl,
                "tp": order.tp,
                "price_current": order.price_current,
                "price_stoplimit": order.price_stoplimit,
                "symbol": order.symbol,
                "comment": order.comment,
                "external_id": order.external_id
            })

        return jsonify({"success": True, "orders": orders_readable}), 200

    except Exception as e:
        logging.error(f"Errore nella funzione get_history_orders: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

def get_placed_orders():
    try:
        orders = mt5.orders_get()

        if orders is None or len(orders) == 0:
            message = f"Non esistono ordini pendenti: {mt5.last_error()}"
            logging.info(message)
            return jsonify({"success": True, "message": message, "orders": []}), 200

        orders_readable = []
        for order in orders:
            orders_readable.append({
                "ticket": order.ticket,
                "time_setup": order.time_setup,
                "time_setup_msc": order.time_setup_msc,
                "time_done": order.time_done,
                "time_done_msc": order.time_done_msc,
                "time_expiration": order.time_expiration,
                "type": order.type,
                "type_time": order.type_time,
                "type_filling": order.type_filling,
                "state": order.state,
                "magic": order.magic,
                "position_id": order.position_id,
                "position_by_id": order.position_by_id,
                "reason": order.reason,
                "volume_initial": order.volume_initial,
                "volume_current": order.volume_current,
                "price_open": order.price_open,
                "sl": order.sl,
                "tp": order.tp,
                "price_current": order.price_current,
                "price_stoplimit": order.price_stoplimit,
                "symbol": order.symbol,
                "comment": order.comment,
                "external_id": order.external_id
            })

        return jsonify({"success": True, "orders": orders_readable}), 200

    except Exception as e:
        logging.error(f"Errore nella funzione get_placed_orders: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

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
        return jsonify({"success": False, "message": message}), 500

    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        message = f"Simbolo {symbol} non trovato."
        logging.error(message)
        return jsonify({"success": False, "message": message}), 400
    if not symbol_info.visible and not mt5.symbol_select(symbol, True):
        message = f"Errore nell'attivare il simbolo {symbol}."
        logging.error(message)
        return jsonify({"success": False, "message": message}), 400

    stops_level = symbol_info.trade_stops_level
    point = symbol_info.point

    if stops_level is None:
        message = f"Impossibile ottenere il livello minimo di stop per il simbolo {symbol}."
        logging.error(message)
        return jsonify({"success": False, "message": message}), 400

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
        return jsonify({"success": False, "message": message}), 500

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        message = f"Errore nell'invio dell'ordine: {result.comment}"
        logging.error(message)
        return jsonify({"success": False, "message": message}), 400

    logging.info(f"Ordine creato con successo: {result}")
    return jsonify({"success": True, "order": result.order}), 200

def update_order(ticket, price=None, stop_loss=None, take_profit=None):
    orders = mt5.orders_get()
    if not orders:
        message = f"Nessun ordine pendente trovato: {mt5.last_error()}"
        logging.info(message)
        return jsonify({"success": False, "message": message}), 404

    order = next((o for o in orders if o.ticket == ticket), None)
    if not order:
        message = f"Ordine con ticket {ticket} non trovato."
        logging.error(message)
        return jsonify({"success": False, "message": message}), 404

    request = {
        "action": mt5.TRADE_ACTION_MODIFY,
        "symbol": order.symbol,
        "order": ticket,
        "price": price if price is not None else order.price_open,
        "sl": stop_loss if stop_loss is not None else order.sl,
        "tp": take_profit if take_profit is not None else order.tp,
    }

    result = mt5.order_send(request)
    if result is None:
        message = f"Errore di comunicazione con il server: {mt5.last_error()}"
        logging.error(message)
        return jsonify({"success": False, "message": message}), 500

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        message = f"Errore nell'aggiornamento dell'ordine. Retcode: {result.retcode}, Details: {result.comment}"
        logging.error(f"Errore nell'aggiornamento dell'ordine. Retcode: {result.retcode}, Details: {result.comment}")
        return jsonify({"success": False, "message": message}), 500

    logging.info(f"Ordine con ticket {ticket} aggiornato con successo")
    return jsonify({"success": True, "message": "Ordine aggiornato con successo"}), 200

def delete_order(ticket):      
    orders = mt5.orders_get(ticket=ticket)
   
    if not orders:
        message = f"Nessun ordine trovato o errore: {mt5.last_error()}"
        logging.error(message)
        return jsonify({"success": False, "message": message}), 500

    logging.info(f"Ordine {ticket} da eliminare")
    
    request = {
        "action": mt5.TRADE_ACTION_REMOVE,
        "order": ticket,
    }
    
    result = mt5.order_send(request)
    if result is None:
        error_message = f"Errore di comunicazione con il server: {mt5.last_error()}"
        logging.error(error_message)
        return jsonify({"success": False, "message": error_message}), 500

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        error_message = f"Errore nell'annullamento dell'ordine. Retcode: {result.retcode}, Commento: {result.comment}"
        logging.error(error_message)
        return jsonify({"success": False, "message": error_message}), 500

    logging.info(f"Ordine con ticket {ticket} cancellato con successo.")
    return jsonify({"success": True, "message": "Ordine cancellato con successo"}), 200