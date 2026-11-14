
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Music, UserPrefrence
from .recommendation import order_music_for_user
from .serializers import MusicSerializer


# class RecommendationConsumer(AsyncJsonWebsocketConsumer):

#     async def connect(self):
#         user = self.scope.get("user")

#         if not user or not user.is_authenticated:
#             await self.close(code=4401)
#             return

#         self.user = user
#         self.group_name = f"recommendations_user_{user.pk}"

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         await self.accept()

#         await self.send_json({
#             "type": "connected",
#             "message": "Recommendation WebSocket connected",
#             "user_id": user.pk,
#             "supported_events": [
#                 "play",
#                 "progress",
#                 "skip",
#                 "like",
#                 "complete"
#             ]
#         })

#     async def disconnect(self, close_code):
#         if hasattr(self, "group_name"):
#             await self.channel_layer.group_discard(
#                 self.group_name,
#                 self.channel_name
#             )

#     async def receive_json(self, content, **kwargs):

      
#         if not isinstance(content, dict):
#             await self.send_error(
#                 "Message must be a JSON object."
#             )
#             return

#         action = content.get("type")

#         allowed_events = {
#             "play",
#             "progress",
#             "skip",
#             "like",
#             "complete"
#         }

#         if action not in allowed_events:
#             await self.send_error(
#                 "Unsupported event type."
#             )
#             return

#         # Validate music ID and listening duration
#         try:
#             music_id = int(content.get("music_id"))
#             listened_duration = int(
#                 content.get("listened_duration", 0)
#             )

#             if music_id <= 0 or listened_duration < 0:
#                 raise ValueError

#         except (TypeError, ValueError):
#             await self.send_error(
#                 "Invalid music_id or listened_duration."
#             )
#             return

#         # Save event and calculate recommendations
#         try:
#             result = await self.save_event_and_recommend(
#                 user_id=self.user.pk,
#                 action=action,
#                 music_id=music_id,
#                 listened_duration=listened_duration
#             )

#         except Music.DoesNotExist:
#             await self.send_error(
#                 "Music was not found or is inactive."
#             )
#             return

#         except (ValidationError, ValueError) as exc:
#             await self.send_error(str(exc))
#             return

#         # Send acknowledgement
#         await self.send_json({
#             "type": "event_saved",
#             "event": action,
#             "music_id": music_id,
#             "event_id": result["event_id"]
#         })

#         # Send updated recommendations
#         if result["recommendations"] is not None:

#             await self.channel_layer.group_send(
#                 self.group_name,
#                 {
#                     "type": "recommendations.updated",
#                     "payload": {
#                         "type": "recommendations_updated",
#                         "trigger": action,
#                         "music_id": music_id,
#                         "recommendations": result["recommendations"]
#                     }
#                 }
#             )

#     async def recommendations_updated(self, event):

#         await self.send_json(
#             event["payload"]
#         )

#     async def send_error(self, message):

#         await self.send_json({
#             "type": "error",
#             "message": message
#         })

#     @database_sync_to_async
#     def save_event_and_recommend(
#         self,
#         user_id,
#         action,
#         music_id,
#         listened_duration
#     ):

#         User = get_user_model()

#         user = User.objects.get(pk=user_id)

#         music = Music.objects.get(
#             pk=music_id,
#             is_active=True
#         )

#         with transaction.atomic():

#             # PROGRESS EVENT
#             if action == "progress":

#                 event = (
#                     UserPrefrence.objects.filter(
#                         user=user,
#                         music=music
#                     )
#                     .order_by("-created_at", "-id")
#                     .first()
#                 )

#                 if event is None:

#                     event = UserPrefrence.objects.create(
#                         user=user,
#                         music=music,
#                         listened_duration=listened_duration,
#                         completed=False,
#                         skipped=False,
#                         liked=False
#                     )

#                 else:

#                     event.listened_duration = max(
#                         event.listened_duration or 0,
#                         listened_duration
#                     )

#                     event.save(
#                         update_fields=["listened_duration"]
#                     )

#             # OTHER EVENTS
#             else:

#                 event = UserPrefrence.objects.create(
#                     user=user,
#                     music=music,
#                     listened_duration=listened_duration,
#                     completed=(action == "complete"),
#                     skipped=(action == "skip"),
#                     liked=(action == "like")
#                 )

#             event_id = event.pk

#             # Calculate recommendations after transaction commits.
#             # This prevents recommendation logic from running
#             # before the preference changes are committed.

#         recommendation_data = None

#         # IMPORTANT:
#         # Progress also triggers recommendation updates.
#         if action in {
#             "play",
#             "progress",
#             "skip",
#             "like",
#             "complete"
#         }:

#             ordered = order_music_for_user(
#                 user,
#                 Music.objects.filter(
#                     is_active=True
#                 ).order_by("id")
#             )

#             recommendation_data = MusicSerializer(
#                 ordered[:5],
#                 many=True
#             ).data

#             # Convert serializer data to JSON-safe Python objects
#             recommendation_data = json.loads(
#                 json.dumps(recommendation_data)
#             )

#         return {
#             "event_id": event_id,
#             "recommendations": recommendation_data
#         }
class RecommandationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user=self.scope['user']
        self.user=user
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return ValidationError('No User Login Found')
        self.group_name = f"recommendations_user_{user.pk}"
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        
        await self.accept()

        await self.send_json({
            'message':'Connected'
        })
    async def send_error(self):
        await self.send_json({'type':'error','message':'Error in Details'})
        return

    async def receive_json(self,content,**kwargs):
       
        # listen_duration=int(content['listen_duration'] , 0)
        listen_duration = int(content.get('listen_duration', 0))
        # user=User.objects.filter(pk=)
        try:
            # music_id,event_id,action_type=map(int,self.content['music_id'],self.content['event_id']),self.content['action_type']
            music_id = int(content['music_id'])
            event_id = content.get('event_id')
            action_type = content['action_type']
            if action_type not in {"progress",'skip','like','complete'}:
                await self.send_error()
                return
        except:
            return await self.send_error()
        result = await self.save_and_recommand(self.user.pk,music_id,action_type,listen_duration)
        await self.send_json({'message':'Recommandation_updated'})
        await self.send_json({'music_id':music_id,'action_type':action_type,'listen_duration':listen_duration,'event_id':event_id})

        if result['recommandations'] is not None:
            await self.channel_layer.group_send(self.group_name,{
                    "type":"recommandations.updated",
                    "payload":{"type":"recommandations_updated",
                           "trigger":action_type,
                            'recommandations':result['recommandations']

                    },
            })
    async def recommandations_updated(self,event):
        await self.send_json({'message':event['payload']})
        return 
        

        

    async def disconnect(self,disconnect):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    @database_sync_to_async
    def save_and_recommand(self,user_id,music_id,action,listen_duration):
        
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        music = Music.objects.get(pk=music_id, is_active=True)
        
        with transaction.atomic():
            if action=='progress':
                   # Update the most recent play/listening event for this song.
                try:
                    event = (
                        UserPrefrence.objects.filter(user=user, music=music)
                        .order_by("-created_at", "-id")
                        .first()
                    )
                except Music.DoesNotExist:
                    self.send_error()
                if event is None:
                    event = UserPrefrence.objects.create(
                        user=user, music=music, 
                        listened_duration=listen_duration,
                        completed=False, skipped=False, liked=False,
                    )
                else:
                    event.listen_duration = max(
                        event.listen_duration or 0, listen_duration
                    )
                    event.save(update_fields=["listen_duration"])
            else:
                # Each meaningful action is retained as a separate history event.
                event = UserPrefrence.objects.create(
                    user=user,
                    music=music,
                    listened_duration=listen_duration,
                    completed=(action == "complete"),
                    skipped=(action == "skip"),
                    liked=(action == "like"),
                )
            recommendation_data=None
            if action  in {"play", "progress", "skip", "like", "complete"}:
                ordered = order_music_for_user(
                user, Music.objects.filter(is_active=True).order_by("id")
                )
                recommendation_data = MusicSerializer(ordered[:5], many=True).data
                # Convert DRF ReturnDict/ReturnList to JSON-safe primitives.
                recommendation_data = json.loads(json.dumps(recommendation_data))
            return {
                "event_id": event.pk,
                "recommandations": recommendation_data,
            }


            




