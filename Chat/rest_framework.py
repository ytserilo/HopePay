class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'id')

class MessageSerializer(serializers.ModelSerializer):
    tracks = UserSerializer(many=True, read_only=True)

    class Meta:
        model = MessageChat
        fields = ('message_text', 'photo_message', 'record_voice', 'date_created', 'tracks')
