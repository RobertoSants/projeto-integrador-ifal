from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Q, F, Case, When, BooleanField
from workers.models import Worker
from workers.serializers import WorkerListSerializer


class SearchView(APIView):
    def get(self, request):
        # avg_rating calculado no banco — evita trazer tudo pra memória
        queryset = Worker.objects.annotate(avg_rating=Avg("reviews__rating"))

        # Filtro por texto livre usando Q — uma única query com OR
        q = request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(full_name__icontains=q) | Q(bio__icontains=q)
            )

        # Filtro exclusivo por cidade
        city = request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__iexact=city)

        # Filtro por categoria de serviço
        service = request.query_params.get("service")
        if service:
            queryset = queryset.filter(services__id=service)

        # Filtro por nota mínima — agora feito no banco via anotação
        rating = request.query_params.get("rating")
        if rating:
            try:
                queryset = queryset.filter(avg_rating__gte=float(rating))
            except ValueError:
                pass

        # Determina a cidade do contratante para priorização
        # 1. Usuário autenticado → usa a cidade do perfil dele
        # 2. Parâmetro manual → usa ?contratante_city=
        contratante_city = None
        if request.user.is_authenticated and request.user.city:
            contratante_city = request.user.city
        elif request.query_params.get("contratante_city"):
            contratante_city = request.query_params.get("contratante_city")

        # Priorização e ordenação no banco: locais primeiro, depois rating desc
        # Workers sem avaliação ficam no fim (nulls_last)
        if contratante_city:
            queryset = queryset.annotate(
                is_local=Case(
                    When(city__iexact=contratante_city, then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            ).order_by("-is_local", F("avg_rating").desc(nulls_last=True))
        else:
            queryset = queryset.order_by(F("avg_rating").desc(nulls_last=True))

        queryset = queryset.distinct()

        serializer = WorkerListSerializer(
            queryset,
            many=True,
            context={"contratante_city": contratante_city, "request": request},
        )

        return Response({
            "count": queryset.count(),
            "contratante_city": contratante_city,
            "results": serializer.data,
        })
