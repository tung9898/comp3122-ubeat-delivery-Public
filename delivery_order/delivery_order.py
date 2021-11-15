import flask, json, redis
from pymongo import MongoClient

##############################
# Init library / connections
##############################

flask_app = flask.Flask(__name__)
deliveriesdb = MongoClient('mongodb://comp3122:23456@delivery_order_db:27017')

################
# Redis events
################

def add_shipped(message):
    load = json.loads(message['data'])
    delivery = deliveriesdb.delivery_orders.deliveries.find_one({'delivery_id': load['delivery_id']})
    delivery['orders'].append({'order_id': load['order_id'], 'customer_id': load['customer_id'], 'restaurant_id': load['restaurant_id'], 'taken': 0})
    deliveriesdb.delivery_orders.deliveries.replace_one({'_id': delivery['_id']}, delivery)

###################
# Flask endpoints
###################

@flask_app.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    orders = deliveriesdb.delivery_orders.deliveries.find_one({'orders.order_id': order_id}, { '_id': 0})
    if not orders:
        return {'error': 'not found'}, 404
    orders = orders['orders']
    for order in orders:
        if order['order_id'] == order_id:
            return order, 200

##############################
# Main: Run flask, establish subscription
##############################
#       
if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True, port=15000)

