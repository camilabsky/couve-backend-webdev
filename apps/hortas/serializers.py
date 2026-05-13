from rest_framework import serializers
from .models import Horta


class HortaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horta
        fields = ['id', 'nome', 'descricao', 'endereco', 'latitude', 'longitude', 'gestor', 'ativa', 'criada_em']
        read_only_fields = ['criada_em']
