from rest_framework import serializers

class RecommendationSerializer(serializers.Serializer):
    first_value = serializers.CharField()
    second_value = serializers.CharField()
    third_value = serializers.CharField()
    fourth_value = serializers.CharField()
    fifth_value = serializers.CharField()
