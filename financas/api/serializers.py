from rest_framework import serializers

from financas.models import (
    Bem,
    Cartao,
    Categoria,
    Conta,
    Despesa,
    Investimento,
    Orcamento,
    Receita,
)


class UserOwnedSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ContaSerializer(UserOwnedSerializer):
    class Meta:
        model = Conta
        fields = '__all__'
        read_only_fields = ('user',)


class CartaoSerializer(UserOwnedSerializer):
    class Meta:
        model = Cartao
        fields = '__all__'
        read_only_fields = ('user',)


class CategoriaSerializer(UserOwnedSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('user',)


class ReceitaSerializer(UserOwnedSerializer):
    class Meta:
        model = Receita
        fields = '__all__'
        read_only_fields = ('user',)


class DespesaSerializer(UserOwnedSerializer):
    class Meta:
        model = Despesa
        fields = '__all__'
        read_only_fields = ('user',)


class InvestimentoSerializer(UserOwnedSerializer):
    class Meta:
        model = Investimento
        fields = '__all__'
        read_only_fields = ('user',)


class BemSerializer(UserOwnedSerializer):
    class Meta:
        model = Bem
        fields = '__all__'
        read_only_fields = ('user',)


class OrcamentoSerializer(UserOwnedSerializer):
    class Meta:
        model = Orcamento
        fields = '__all__'
        read_only_fields = ('user',)
