from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Count, Value
from django.db.models.functions import Coalesce
from .models import Tarefas, Perfil, Recompensas, PerfilRecompensas


def get_active_profile():
    return Perfil.objects.order_by('id').first()


def get_profile_balance(perfil):
    if not perfil:
        return 0

    total_moedas = Tarefas.objects.filter(
        id_perfil=perfil,
        concluido=True,
    ).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total']

    total_gasto = PerfilRecompensas.objects.filter(
        id_perfil=perfil,
    ).aggregate(total=Coalesce(Sum('id_recompensa__preco'), Value(0)))['total']

    return total_moedas - total_gasto


def landing_page(request):
    context = {
        'total_perfis': Perfil.objects.count(),
        'total_tarefas': Tarefas.objects.count(),
        'tarefas_abertas': Tarefas.objects.filter(id_perfil__isnull=True).count(),
        'total_recompensas': Recompensas.objects.count(),
    }
    return render(request, 'app/landing.html', context)


def home(request):
    perfil = get_active_profile()
    context = {
        'greeting_name': perfil.nome if perfil else 'visitante',
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'minhas_tarefas': Tarefas.objects.filter(id_perfil=perfil, concluido=False).order_by('titulo') if perfil else [],
        'total_perfis': Perfil.objects.count(),
        'total_tarefas': Tarefas.objects.count(),
        'tarefas_abertas': Tarefas.objects.filter(id_perfil__isnull=True).count(),
        'total_recompensas': Recompensas.objects.count(),
    }
    return render(request, 'app/home.html', context)


def tarefas_page(request):
    perfil = get_active_profile()
    context = {
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'tarefas_abertas': Tarefas.objects.filter(id_perfil__isnull=True).order_by('tipo', 'titulo'),
    }
    return render(request, 'app/tarefas.html', context)


def recompensas_page(request):
    perfil = get_active_profile()
    estoque_por_recompensa = {
        item['id_recompensa_id']: item['total']
        for item in PerfilRecompensas.objects.filter(id_perfil__isnull=True)
        .values('id_recompensa_id')
        .annotate(total=Count('id'))
    }

    recompensas = list(Recompensas.objects.all().order_by('preco', 'nome'))
    for recompensa in recompensas:
        recompensa.estoque = estoque_por_recompensa.get(recompensa.id, 0)

    context = {
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'recompensas': recompensas,
    }
    return render(request, 'app/recompensas.html', context)


def perfil_page(request):
    perfil = get_active_profile()
    context = {
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'tarefas_concluidas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).count() if perfil else 0,
        'moedas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total'] if perfil else 0,
        'mudas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).aggregate(total=Coalesce(Sum('mudas'), Value(0)))['total'] if perfil else 0,
        'recompensas_resgatadas': PerfilRecompensas.objects.filter(id_perfil=perfil).count() if perfil else 0,
        'tarefas_concluidas_lista': Tarefas.objects.filter(id_perfil=perfil, concluido=True).order_by('titulo') if perfil else [],
        'recompensas_resgatadas_lista': PerfilRecompensas.objects.filter(id_perfil=perfil).select_related('id_recompensa').order_by('id_recompensa__nome') if perfil else [],
    }
    return render(request, 'app/perfil.html', context)


@transaction.atomic
def aceitar_tarefa_page(request, tarefa_id):
    if request.method != 'POST':
        return redirect('tarefas')

    perfil = get_active_profile()
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para aceitar tarefas.')
        return redirect('tarefas')

    tarefa = get_object_or_404(Tarefas, pk=tarefa_id)
    if tarefa.id_perfil_id is not None:
        messages.warning(request, 'Essa tarefa já foi aceita por outro perfil.')
    else:
        tarefa.id_perfil = perfil
        tarefa.save(update_fields=['id_perfil'])
        messages.success(request, f'Tarefa "{tarefa.titulo}" aceita com sucesso.')

    return redirect('tarefas')


@transaction.atomic
def concluir_tarefa_page(request, tarefa_id):
    next_page = request.POST.get('next', 'tarefas')

    if request.method != 'POST':
        return redirect(next_page)

    perfil = get_active_profile()
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para concluir tarefas.')
        return redirect(next_page)

    tarefa = get_object_or_404(Tarefas, pk=tarefa_id)
    if tarefa.id_perfil_id != perfil.id:
        messages.error(request, 'Você só pode concluir tarefas que já aceitou.')
    elif tarefa.concluido:
        messages.warning(request, 'Essa tarefa já foi concluída.')
    else:
        tarefa.concluido = True
        tarefa.save(update_fields=['concluido'])
        messages.success(request, f'Tarefa "{tarefa.titulo}" concluída. As moedas já entraram no saldo.')

    return redirect(next_page)


@transaction.atomic
def resgatar_recompensa_page(request, recompensa_id):
    if request.method != 'POST':
        return redirect('recompensas')

    perfil = get_active_profile()
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para resgatar recompensas.')
        return redirect('recompensas')

    recompensa = get_object_or_404(Recompensas, pk=recompensa_id)
    saldo = get_profile_balance(perfil)
    if saldo < recompensa.preco:
        messages.error(request, 'Saldo insuficiente para resgatar essa recompensa.')
        return redirect('recompensas')

    item_estoque = PerfilRecompensas.objects.filter(
        id_perfil__isnull=True,
        id_recompensa=recompensa,
    ).select_for_update().first()

    if not item_estoque:
        messages.warning(request, 'Essa recompensa está sem estoque no momento.')
    else:
        item_estoque.id_perfil = perfil
        item_estoque.save(update_fields=['id_perfil'])
        messages.success(request, f'Recompensa "{recompensa.nome}" resgatada com sucesso.')

    return redirect('recompensas')

@api_view(['POST'])
def minhas_tarefas(request):
    id_perfil = request.data.get('id_perfil')
    if id_perfil is None:
        return Response({'error': 'id_perfil required'}, status=400)
    tarefas = Tarefas.objects.filter(id_perfil_id=id_perfil, concluido=False)
    data = list(tarefas.values())
    return Response(data)

@api_view(['POST'])
def tarefas_concluidas(request):
    id_perfil = request.data.get('id_perfil')
    if id_perfil is None:
        return Response({'error': 'id_perfil required'}, status=400)
    total = Tarefas.objects.filter(id_perfil_id=id_perfil, concluido=True).count()
    return Response({'Total': total})

@api_view(['POST'])
def minhas_moedas(request):
    id_perfil = request.data.get('id_perfil')
    if id_perfil is None:
        return Response({'error': 'id_perfil required'}, status=400)

    # Sum moedas from concluded tasks
    total_moedas = Tarefas.objects.filter(
        id_perfil_id=id_perfil, concluido=True
    ).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total']

    # Sum gasto from redeemed rewards
    total_gasto = PerfilRecompensas.objects.filter(
        id_perfil_id=id_perfil
    ).aggregate(
        total=Coalesce(Sum('id_recompensa__preco'), Value(0))
    )['total']

    saldo = total_moedas - total_gasto
    return Response({'Saldo': saldo, 'id_perfil': id_perfil})

@api_view(['POST'])
def minhas_mudas(request):
    id_perfil = request.data.get('id_perfil')
    if id_perfil is None:
        return Response({'error': 'id_perfil required'}, status=400)
    total = Tarefas.objects.filter(
        id_perfil_id=id_perfil, concluido=True
    ).aggregate(total=Coalesce(Sum('mudas'), Value(0)))['total']
    return Response({'Total': total})

@api_view(['POST'])
def minhas_recompensas(request):
    id_perfil = request.data.get('id_perfil')
    if id_perfil is None:
        return Response({'error': 'id_perfil required'}, status=400)
    total = PerfilRecompensas.objects.filter(id_perfil_id=id_perfil).count()
    return Response({'Total': total})

@api_view(['POST'])
def concluir_tarefa(request):
    id_tarefa = request.data.get('id_tarefa')
    if id_tarefa is None:
        return Response({'error': 'id_tarefa required'}, status=400)
    updated = Tarefas.objects.filter(id=id_tarefa, concluido=False).update(concluido=True)
    return Response({'affected': updated})

@api_view(['GET'])
def tarefas_disponiveis(request):
    tarefas = Tarefas.objects.filter(id_perfil__isnull=True)
    data = list(tarefas.values())
    return Response(data)

@api_view(['POST'])
def aceitar_tarefa(request):
    id_tarefa = request.data.get('id_tarefa')
    id_perfil = request.data.get('id_perfil')
    if id_tarefa is None or id_perfil is None:
        return Response({'error': 'id_tarefa and id_perfil required'}, status=400)
    updated = Tarefas.objects.filter(id=id_tarefa).update(id_perfil_id=id_perfil)
    return Response({'affected': updated})

@api_view(['GET'])
def recompensas_disponiveis(request):
    # Recreate the view logic: join Recompensas with count of available (id_perfil IS NULL)
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT Recompensas.*, cnt.total
            FROM Recompensas
            JOIN (
                SELECT COUNT(*) AS total, id_recompensa
                FROM PerfilRecompensas
                WHERE id_perfil IS NULL
                GROUP BY id_recompensa
            ) AS cnt
            ON Recompensas.id = cnt.id_recompensa
        """)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return Response(rows)

@api_view(['POST'])
def resgatar_recompensa(request):
    id_recompensa = request.data.get('id_recompensa')
    id_perfil = request.data.get('id_perfil')
    if id_recompensa is None or id_perfil is None:
        return Response({'error': 'id_recompensa and id_perfil required'}, status=400)

    perfil = Perfil.objects.filter(id=id_perfil).first()
    recompensa = Recompensas.objects.filter(id=id_recompensa).first()
    if not perfil or not recompensa:
        return Response({'error': 'profile or reward not found'}, status=404)

    if get_profile_balance(perfil) < recompensa.preco:
        return Response({'error': 'insufficient balance'}, status=400)

    # Update one PerfilRecompensas row where id_perfil is null and matches the recompensa
    updated = PerfilRecompensas.objects.filter(
        id_perfil__isnull=True,
        id_recompensa_id=id_recompensa
    ).select_for_update().first()

    if updated:
        updated.id_perfil_id = id_perfil
        updated.save(update_fields=['id_perfil'])
        return Response({'affected': 1})
    else:
        return Response({'affected': 0})