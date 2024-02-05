import aiohttp
# import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)

HUBSPOT_API_KEY = 'pat-eu1-df67527e-714a-4eb5-ba74-b2fa20d58664'
HUBSPOT_API_URL = 'https://api.hubapi.com/crm/v3/objects/tickets'

async def create_ticket(data):
    async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HUBSPOT_API_KEY}'}) as session:
        async with session.post(HUBSPOT_API_URL, json=data) as response:
            return await response.json()

async def update_ticket(ticket_id, data):
    async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HUBSPOT_API_KEY}'}) as session:
        async with session.patch(f'{HUBSPOT_API_URL}/{ticket_id}', json=data) as response:
            return await response.json()

async def delete_ticket(ticket_id):
    async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HUBSPOT_API_KEY}'}) as session:
        async with session.delete(f'{HUBSPOT_API_URL}/{ticket_id}') as response:
            return await response.json()

async def get_ticket(ticket_id):
    async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HUBSPOT_API_KEY}'}) as session:
        async with session.get(f'{HUBSPOT_API_URL}/{ticket_id}') as response:
            return await response.json()

async def get_all_tickets():
    async with aiohttp.ClientSession(headers={'Authorization': f'Bearer {HUBSPOT_API_KEY}'}) as session:
        async with session.get(f'{HUBSPOT_API_URL}') as response:
            return await response.json()

# @app.route('/create_ticket', methods=['POST'])
# def create_ticket_route():
#     data = request.get_json()
#     ticket = asyncio.run(create_ticket(data))
#     return jsonify(ticket)

# @app.route('/update_ticket/<int:ticket_id>', methods=['PUT'])
# def update_ticket_route(ticket_id):
#     data = request.get_json()
#     asyncio.run(update_ticket(ticket_id, data))
#     return jsonify({'message': 'Ticket updated successfully'})

# @app.route('/delete_ticket/<int:ticket_id>', methods=['DELETE'])
# def delete_ticket_route(ticket_id):
#     asyncio.run(delete_ticket(ticket_id))
#     return jsonify({'message': 'Ticket deleted successfully'})

# @app.route('/view_ticket/<int:ticket_id>', methods=['GET'])
# def view_ticket_route(ticket_id):
#     ticket = asyncio.run(get_ticket(ticket_id))
#     return jsonify(ticket)

# @app.route('/view_all_tickets', methods=['GET'])
# def view_all_tickets_route():
#     tickets = asyncio.run(get_all_tickets())
#     return jsonify(tickets)


# if __name__ == '__main__':
#     app.run(debug=True)