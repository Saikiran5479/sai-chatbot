from starlette.responses import JSONResponse

from food_chatbot.pythonProject import db_helper, generic_helper


def add_to_order(parameters: dict, session_id: str, inprogress_orders=None) -> JSONResponse:
    """Processes requests to add items to an ongoing order"""
    food_items = parameters.get("food-item", [])  # Handle potential missing key
    quantities = parameters.get("number", [])  # Handle potential missing key

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry, I need both food items and quantities. Please specify them clearly."
    else:
        new_food_dict = dict(zip(food_items, quantities))

        # Update or create order based on session ID
        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far you have: {order_str}. Do you need anything else?"

    return JSONResponse(content={"fulfillmentText": fulfillment_text})


def remove_from_order(parameters: dict, session_id: str, inprogress_orders=None) -> JSONResponse:
    """Processes requests to remove items from an ongoing order"""
    if session_id not in inprogress_orders:
        return JSONResponse(content={"fulfillmentText": "Couldn't find your order. Please place a new one."})

    food_items = parameters.get("food-item", [])  # Handle potential missing key
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    response_text = ""
    if len(removed_items) > 0:
        response_text += f' Removed "{", ".join(removed_items)}" from your order!'

    if len(no_such_items) > 0:
        response_text += f' Your current order does not have "{", ".join(no_such_items)}"'

    if len(current_order.keys()) == 0:
        response_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        response_text += f" Here is what is left in your order: {order_str}"

    return JSONResponse(content={"fulfillmentText": response_text})


def track_order(parameters: dict, session_id: str) -> JSONResponse:
    """Processes requests to track order status"""
    try:
        order_id = int(parameters["order_id"])
        order_status = db_helper.get_order_status(order_id)
        if order_status:
            fulfillment_text = f"The order status for order ID: {order_id} is: {order_status}"
        else:
            fulfillment_text = f"No order found with order ID: {order_id}"
    except ValueError:  # Handle potential invalid order ID format
        fulfillment_text = "Invalid order ID. Please enter a valid number."
    return JSONResponse(content={"fulfillmentText": fulfillment_text})