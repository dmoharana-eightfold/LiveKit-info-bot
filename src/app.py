from flask import Flask, request
from flask_restx import Resource, Api
from livekit import api as lk_api
import os 
import asyncio
from flask_cors import CORS
from collections import deque
from datetime import datetime

app = Flask(__name__)
CORS(app)
api = Api(app)

# Store recent metrics in memory (for demo purposes)
# In production, you might want to use Redis or a database
metrics_history = deque(maxlen=100)

ns = api.namespace('api', description='API endpoints')

@ns.route('/token')
class CreateRoom(Resource):
    def get(self):
        async def create_room():
            async with lk_api.LiveKitAPI() as lkapi:
                await lkapi.room.create_room(
                    lk_api.CreateRoomRequest(
                        name="info-bot-2",
                        empty_timeout=10 * 60,
                        max_participants=20,
                    )
                )
        asyncio.run(create_room())
    

        token = lk_api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
            .with_identity("user-" + str(os.urandom(8).hex())) \
            .with_name("user") \
            .with_grants(lk_api.VideoGrants(
                room_join=True,
                room="info-bot-2",
            )).to_jwt()

        return {
            "serverUrl": os.getenv('LIVEKIT_URL'),
            "roomName": "info-bot-2",
            "participantToken": token,
            "participantName": "user",
        }

if __name__ == '__main__':
    app.run(debug=True)