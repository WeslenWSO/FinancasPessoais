from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .defaults import DEFAULT_CATEGORIAS_DESPESA, DEFAULT_CATEGORIAS_RECEITA
from .models import Categoria, gerar_legacy_id

User = get_user_model()


def criar_categorias_padrao(user):
    if Categoria.objects.filter(user=user).exists():
        return
    for item in DEFAULT_CATEGORIAS_RECEITA:
        Categoria.objects.create(
            user=user,
            legacy_id=gerar_legacy_id(),
            nome=item['nome'],
            cor=item['cor'],
            tipo=Categoria.TIPO_RECEITA,
        )
    for item in DEFAULT_CATEGORIAS_DESPESA:
        Categoria.objects.create(
            user=user,
            legacy_id=gerar_legacy_id(),
            nome=item['nome'],
            cor=item['cor'],
            tipo=Categoria.TIPO_DESPESA,
        )


@receiver(post_save, sender=User)
def seed_categorias_usuario(sender, instance, created, **kwargs):
    if created:
        criar_categorias_padrao(instance)
