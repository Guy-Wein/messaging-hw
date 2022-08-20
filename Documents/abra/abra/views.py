from .serializers import MessageSerializer
from .models import Message
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User

from django.http import Http404, HttpResponseNotAllowed
from rest_framework.views import APIView


# # write a new message
class Write(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        # serialize the json
        serializer = MessageSerializer(data=request.data)
        # check if the JSON is valid
        if serializer.is_valid():
            # save to db
            serializer.save(sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)

# Get all messages for a specific user
class AllMessages(APIView):
    
    def get(self, request, username):
        # get the user's object 
        user = User.objects.get(username=username)
        # query all messages for a specific user
        messages = Message.objects.filter(receiver=user)
        # check if messages is empty
        if not messages:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # serialize data
        serializer = MessageSerializer(messages, many=True)
        # return json
        return Response(serializer.data)

# # Get all unread messages for a specific user
class UnreadMessages(APIView):
    def get(self, request, username):
        # get the user's object 
        user = User.objects.get(username=username)
        # query all messages for a specific user
        messages = Message.objects.filter(receiver=user, read=False)
        # check if messages is empty
        if not messages:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # serialize data
        serializer = MessageSerializer(messages, many=True)
        # return json
        return Response(serializer.data)

# read message or delete 
class MessageDetails(APIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
            #check if message exists
            try:
                return Message.objects.get(pk=id)
            except Message.DoesNotExist:
                raise Http404

    def put(self, request, id):
        message = self.get_object(id)
        # check if read is False
        if not message.read:
            # update read to True in db
            message.read = True
            message.save()
        # serialize and return
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def delete(self, request, id):
        message = self.get_object(id)
        # check if requester is sender/receiver
        if request.user == message.sender or request.user == message.receiver:
            # delete from db
            message.delete()
            # return 204
            return Response({"message":"Deleted."},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error":"you must be the sender/receiver of this message to do this action."},status=status.HTTP_403_FORBIDDEN)
