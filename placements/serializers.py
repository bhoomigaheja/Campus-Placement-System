from rest_framework import serializers
from .models import Job, Application, Interview

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

    def validate_min_cgpa(self, value):
        if value < 0 or value > 10.0:
            raise serializers.ValidationError("CGPA must be between 0 and 10.0")
        return value

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('match_score', 'applied_at')
