from rest_framework import serializers


class WeatherCheckSerializer(serializers.Serializer):
    user_ip = serializers.CharField(max_length=45, required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)

    def validate(self, attrs):
        # not (A and B) = not A or not B
        if "user_ip" not in attrs and not ("latitude" in attrs and "longitude" in attrs):
            raise serializers.ValidationError(
                "You must provide either the user's IP address or the lat & long coordinates."
            )
        return attrs
