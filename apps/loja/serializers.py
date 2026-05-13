from rest_framework import serializers
from .models import ItemLoja, Compra


class ItemLojaSerializer(serializers.ModelSerializer):
    disponivel = serializers.BooleanField(read_only=True)

    class Meta:
        model = ItemLoja
        fields = ['id', 'horta', 'nome', 'descricao', 'foto', 'preco_moedas', 'estoque', 'ativo', 'disponivel']


class CompraSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField(read_only=True)
    item_nome = serializers.CharField(source='item.nome', read_only=True)

    class Meta:
        model = Compra
        fields = ['id', 'usuario', 'item', 'item_nome', 'quantidade', 'total_moedas', 'realizada_em']
        read_only_fields = ['usuario', 'total_moedas', 'realizada_em']

    def validate(self, data):
        item = data['item']
        quantidade = data.get('quantidade', 1)

        if not item.disponivel:
            raise serializers.ValidationError({'item': 'Item indisponível no momento.'})

        if item.estoque < quantidade:
            raise serializers.ValidationError(
                {'quantidade': f'Estoque insuficiente. Disponível: {item.estoque}.'}
            )

        usuario = self.context['request'].user
        custo_total = item.preco_moedas * quantidade
        if usuario.moedas < custo_total:
            raise serializers.ValidationError(
                {'quantidade': f'Moedas insuficientes. Necessário: {custo_total}, seu saldo: {usuario.moedas}.'}
            )

        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantidade = validated_data.get('quantidade', 1)
        usuario = self.context['request'].user

        custo_total = item.preco_moedas * quantidade
        validated_data['usuario'] = usuario
        validated_data['total_moedas'] = custo_total

        # desconta estoque e moedas do usuário
        item.estoque -= quantidade
        item.save(update_fields=['estoque'])

        usuario.moedas -= custo_total
        usuario.save(update_fields=['moedas'])

        return super().create(validated_data)
