from rest_framework import serializers

from .models import Recompensas


class RecompensasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recompensas
        fields = ["id", "nome", "descricao", "preco", "tipo", "src"]
