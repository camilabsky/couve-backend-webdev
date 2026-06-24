from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Sum, Count, Value
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncWeek
from .models import Tarefas, Perfil, Recompensas, PerfilRecompensas
from .serializers import RecompensasSerializer
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
User = get_user_model()

# # Endpoint público para teste
# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def home(request):
#     return Response({"mensagem": "Bem-vindo à API pública!"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    # Retorna os dados básicos do usuário que já está autenticado.
    return Response({
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    })
    
def get_or_create_user_profile(user):
    if not user.is_authenticated:
        return None

    # Se o perfil ainda não existir, ele é criado com os dados do usuário.
    profile, _ = Perfil.objects.get_or_create(
        user=user,
        defaults={
            'nome': user.get_full_name() or user.username,
            'email': user.email or None,
        },
    )

    return profile


def get_profile_balance(perfil):
    if not perfil:
        return 0

    # O saldo é a soma das moedas ganhas menos o que já foi gasto em recompensas.
    total_moedas = Tarefas.objects.filter(
        id_perfil=perfil,
        concluido=True,
    ).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total']

    total_gasto = PerfilRecompensas.objects.filter(
        id_perfil=perfil,
    ).aggregate(total=Coalesce(Sum('id_recompensa__preco'), Value(0)))['total']

    return total_moedas - total_gasto


def build_admin_reports(request):
    # Report 1 filters
    r_user = (request.GET.get('r_user') or '').strip()
    r_recompensa = (request.GET.get('r_recompensa') or '').strip()
    r_data_inicio = (request.GET.get('r_data_inicio') or '').strip()
    r_data_fim = (request.GET.get('r_data_fim') or '').strip()

    report_recompensas = PerfilRecompensas.objects.filter(id_perfil__isnull=False).select_related('id_perfil', 'id_recompensa')
    if r_user:
        report_recompensas = report_recompensas.filter(id_perfil_id=r_user)
    if r_recompensa:
        report_recompensas = report_recompensas.filter(id_recompensa_id=r_recompensa)
    if r_data_inicio:
        report_recompensas = report_recompensas.filter(data_resgate__date__gte=r_data_inicio)
    if r_data_fim:
        report_recompensas = report_recompensas.filter(data_resgate__date__lte=r_data_fim)

    recompensas_detalhadas = report_recompensas.order_by('-data_resgate', '-id')

    recompensas_resumo_usuario = (
        report_recompensas
        .values('id_perfil', 'id_perfil__nome', 'id_perfil__email')
        .annotate(
            total_resgates=Count('id'),
            total_gasto=Coalesce(Sum('id_recompensa__preco'), Value(0)),
        )
        .order_by('-total_resgates', 'id_perfil__nome')
    )

    recompensas_agrupadas = (
        report_recompensas
        .values(
            'id_perfil',
            'id_perfil__nome',
            'id_perfil__email',
            'id_recompensa',
            'id_recompensa__nome',
            'id_recompensa__tipo',
            'id_recompensa__preco',
        )
        .annotate(quantidade=Count('id'))
        .order_by('id_perfil__nome', 'id_recompensa__nome')
    )

    report_tarefas = Tarefas.objects.filter(concluido=True, id_perfil__isnull=False).select_related('id_perfil')

    # Abaixo ficam os dados que alimentam os blocos de relatório do perfil admin.
    tarefas_detalhadas = report_tarefas.order_by('-data_conclusao', '-id')

    tarefas_serie_temporal = (
        report_tarefas
        .exclude(data_conclusao__isnull=True)
        .annotate(periodo=TruncWeek('data_conclusao'))
        .values('periodo')
        .annotate(total=Count('id'))
        .order_by('periodo')
    )

    tarefas_ranking = (
        report_tarefas
        .values('id_perfil', 'id_perfil__nome', 'id_perfil__email')
        .annotate(total_concluidas=Count('id'))
        .order_by('-total_concluidas', 'id_perfil__nome')
    )

    tarefas_tipos = Tarefas.objects.values_list('tipo', flat=True).distinct().order_by('tipo')

    return {
        'is_admin': True,
        'report_recompensas_detalhadas': recompensas_detalhadas,
        'report_recompensas_resumo_usuario': recompensas_resumo_usuario,
        'report_recompensas_agrupadas': recompensas_agrupadas,
        'report_tarefas_detalhadas': tarefas_detalhadas,
        'report_tarefas_serie_temporal': tarefas_serie_temporal,
        'report_tarefas_ranking': tarefas_ranking,
        'report_filtros': {
            'r_user': r_user,
            'r_recompensa': r_recompensa,
            'r_data_inicio': r_data_inicio,
            'r_data_fim': r_data_fim,
        },
        'report_perfis': Perfil.objects.order_by('nome'),
        'report_recompensas': Recompensas.objects.order_by('nome'),
        'report_tipos_tarefa': tarefas_tipos,
    }


def landing_page(request):
    # A tela inicial mostra um resumo público do sistema antes do login.
    context = {
        'total_perfis': Perfil.objects.count(),
        'total_tarefas': Tarefas.objects.count(),
        'tarefas_abertas': Tarefas.objects.filter(id_perfil__isnull=True).count(),
        'total_recompensas': Recompensas.objects.count(),
        'public_header': True,
    }
    return render(request, 'app/landing.html', context)

def login_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        # Permite entrar tanto com username quanto com e-mail.
        username = identifier
        if '@' in identifier:
            matched_user = User.objects.filter(email__iexact=identifier).first()
            if matched_user:
                username = matched_user.username

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        # Se não bater, a página volta com uma mensagem simples.
        messages.error(request, "Usuário ou senha inválidos.")

    context = {'hide_header': True}
    return render(request, "app/login.html", context)


def cadastro_page(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip().lower()
        nome_completo = (request.POST.get("nome_completo") or "").strip()
        password = request.POST.get("password") or ""
        password_confirm = request.POST.get("password_confirm") or ""

        if not username or not email or not password or not password_confirm:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return render(request, "app/cadastro.html", {'hide_header': True})

        if password != password_confirm:
            messages.error(request, "As senhas não coincidem.")
            return render(request, "app/cadastro.html", {'hide_header': True})

        # Evita repetir username ou e-mail já usados por outra conta.
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Este username já está em uso.")
            return render(request, "app/cadastro.html", {'hide_header': True})

        if User.objects.filter(email__iexact=email).exists() or Perfil.objects.filter(email__iexact=email).exists():
            messages.error(request, "Este e-mail já está em uso.")
            return render(request, "app/cadastro.html", {'hide_header': True})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        Perfil.objects.create(
            user=user,
            nome=nome_completo or username,
            email=email,
        )

        messages.success(request, "Cadastro realizado com sucesso. Faça login para continuar.")
        return redirect("login")

    return render(request, "app/cadastro.html", {'hide_header': True})

def logout_page(request):
    logout(request)
    return redirect("landing")


@login_required(login_url="login")
def home(request):
    perfil = get_or_create_user_profile(request.user)
    # A home concentra o resumo da pessoa e as tarefas já aceitas.
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

@login_required(login_url="login")
def tarefas_page(request):
    perfil = get_or_create_user_profile(request.user)
    # Aqui aparecem só as tarefas livres para alguém pegar.
    context = {
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'tarefas_abertas': Tarefas.objects.filter(id_perfil__isnull=True).order_by('tipo', 'titulo'),
    }
    return render(request, 'app/tarefas.html', context)

@login_required(login_url="login")
def recompensas_page(request):
    perfil = get_or_create_user_profile(request.user)
    # Primeiro contamos o estoque disponível de cada recompensa.
    estoque_por_recompensa = {
        item['id_recompensa_id']: item['total']
        for item in PerfilRecompensas.objects.filter(id_perfil__isnull=True)
        .values('id_recompensa_id')
        .annotate(total=Count('id'))
    }

    # Depois a lista recebe o estoque calculado para mostrar na tela.
    recompensas = list(Recompensas.objects.all().order_by('preco', 'nome'))
    for recompensa in recompensas:
        recompensa.estoque = estoque_por_recompensa.get(recompensa.id, 0)

    context = {
        'perfil': perfil,
        'saldo': get_profile_balance(perfil),
        'recompensas': recompensas,
    }
    return render(request, 'app/recompensas.html', context)

@login_required(login_url="login")
def perfil_page(request):
    perfil = get_or_create_user_profile(request.user)

    if request.method == 'POST' and perfil:
        nome = (request.POST.get('nome') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()

        if not nome or not email:
            messages.error(request, 'Nome e e-mail são obrigatórios.')
            return redirect('perfil')

        duplicated_user_email = User.objects.filter(email__iexact=email).exclude(id=request.user.id).exists()
        duplicated_profile_email = Perfil.objects.filter(email__iexact=email).exclude(id=perfil.id).exists()
        if duplicated_user_email or duplicated_profile_email:
            messages.error(request, 'Este e-mail já está em uso por outro usuário.')
            return redirect('perfil')

        # Atualiza os dados básicos do perfil e também o e-mail da conta.
        perfil.nome = nome
        perfil.email = email
        perfil.save(update_fields=['nome', 'email'])

        request.user.email = email
        request.user.save(update_fields=['email'])

        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('perfil')

    context = {
        'perfil': perfil,
        'is_admin': request.user.is_superuser,
        'saldo': get_profile_balance(perfil),
        'tarefas_concluidas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).count() if perfil else 0,
        'moedas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total'] if perfil else 0,
        'mudas': Tarefas.objects.filter(id_perfil=perfil, concluido=True).aggregate(total=Coalesce(Sum('mudas'), Value(0)))['total'] if perfil else 0,
        'recompensas_resgatadas': PerfilRecompensas.objects.filter(id_perfil=perfil).count() if perfil else 0,
        'tarefas_concluidas_lista': Tarefas.objects.filter(id_perfil=perfil, concluido=True).order_by('titulo') if perfil else [],
        'recompensas_resgatadas_lista': PerfilRecompensas.objects.filter(id_perfil=perfil).select_related('id_recompensa').order_by('id_recompensa__nome') if perfil else [],
    }
    if request.user.is_superuser:
        # O admin recebe também os relatórios adicionais da página.
        context.update(build_admin_reports(request))

    return render(request, 'app/perfil.html', context)


@transaction.atomic
@login_required(login_url="login")
def aceitar_tarefa_page(request, tarefa_id):
    if request.method != 'POST':
        return redirect('tarefas')

    perfil = get_or_create_user_profile(request.user)
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para aceitar tarefas.')
        return redirect('tarefas')

    tarefa = get_object_or_404(Tarefas, pk=tarefa_id)
    if tarefa.id_perfil_id is not None:
        messages.warning(request, 'Essa tarefa já foi aceita por outro perfil.')
    else:
        # A tarefa passa a pertencer ao perfil que a escolheu.
        tarefa.id_perfil = perfil
        tarefa.save(update_fields=['id_perfil'])
        messages.success(request, f'Tarefa "{tarefa.titulo}" aceita com sucesso.')

    return redirect('tarefas')


@transaction.atomic
@login_required(login_url="login")
def concluir_tarefa_page(request, tarefa_id):
    next_page = request.POST.get('next', 'tarefas')

    if request.method != 'POST':
        return redirect(next_page)

    perfil = get_or_create_user_profile(request.user)
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para concluir tarefas.')
        return redirect(next_page)

    tarefa = get_object_or_404(Tarefas, pk=tarefa_id)
    if tarefa.id_perfil_id != perfil.id:
        messages.error(request, 'Você só pode concluir tarefas que já aceitou.')
    elif tarefa.concluido:
        messages.warning(request, 'Essa tarefa já foi concluída.')
    else:
        # Marca a tarefa como concluída e salva o momento da finalização.
        tarefa.concluido = True
        tarefa.data_conclusao = timezone.now()
        tarefa.save(update_fields=['concluido', 'data_conclusao'])
        messages.success(request, f'Tarefa "{tarefa.titulo}" concluída. As moedas já entraram no saldo.')

    return redirect(next_page)


@transaction.atomic
@login_required(login_url="login")
def resgatar_recompensa_page(request, recompensa_id):
    if request.method != 'POST':
        return redirect('recompensas')

    perfil = get_or_create_user_profile(request.user)
    if not perfil:
        messages.error(request, 'Nenhum perfil disponível para resgatar recompensas.')
        return redirect('recompensas')

    recompensa = get_object_or_404(Recompensas, pk=recompensa_id)
    saldo = get_profile_balance(perfil)
    if saldo < recompensa.preco:
        messages.error(request, 'Saldo insuficiente para resgatar essa recompensa.')
        return redirect('recompensas')

    # Busca uma unidade livre da recompensa antes de confirmar o resgate.
    item_estoque = PerfilRecompensas.objects.filter(
        id_perfil__isnull=True,
        id_recompensa=recompensa,
    ).select_for_update().first()

    if not item_estoque:
        messages.warning(request, 'Essa recompensa está sem estoque no momento.')
    else:
        # Ao resgatar, o item deixa de estar livre e passa para o perfil.
        item_estoque.id_perfil = perfil
        item_estoque.data_resgate = timezone.now()
        item_estoque.save(update_fields=['id_perfil', 'data_resgate'])
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

    # Soma o que foi ganho nas tarefas concluídas.
    total_moedas = Tarefas.objects.filter(
        id_perfil_id=id_perfil, concluido=True
    ).aggregate(total=Coalesce(Sum('moedas'), Value(0)))['total']

    # Subtrai o que já foi gasto em recompensas.
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
    # A API marca a tarefa como concluída direto no banco.
    updated = Tarefas.objects.filter(id=id_tarefa, concluido=False).update(
        concluido=True,
        data_conclusao=timezone.now(),
    )
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
        updated.data_resgate = timezone.now()
        updated.save(update_fields=['id_perfil', 'data_resgate'])
        return Response({'affected': 1})
    else:
        return Response({'affected': 0})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def protected_resource(request):
    return Response({
        'message': 'Acesso autorizado.',
        'user': request.user.username,
    })


class RecompensasViewSet(viewsets.ModelViewSet):
    queryset = Recompensas.objects.all().order_by('id')
    serializer_class = RecompensasSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        # Leitura fica aberta; alterações pedem autenticação.
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]