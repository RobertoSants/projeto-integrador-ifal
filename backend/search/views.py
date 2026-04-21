from rest_framework.views import APIView
from rest_framework.response import Response
from workers.models import Worker
from workers.serializers import WorkerListSerializer


class SearchView(APIView):
    def get(self, request):
        queryset = Worker.objects.all()

        # Filtro por texto livre
        q = request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                full_name__icontains=q
            ) | queryset.filter(
                bio__icontains=q
            )

        # Filtro exclusivo por cidade
        city = request.query_params.get("city")
        if city:
            queryset = queryset.filter(city__iexact=city)

        # Filtro por categoria de serviço
        service = request.query_params.get("service")
        if service:
            queryset = queryset.filter(services__id=service)

        # Filtro por nota mínima
        rating = request.query_params.get("rating")

        # Determina a cidade do contratante para priorização
        # 1. Usuário autenticado → usa a cidade do perfil dele
        # 2. Parâmetro manual → usa ?contratante_city=
        contratante_city = None
        if request.user.is_authenticated and request.user.city:
            contratante_city = request.user.city
        elif request.query_params.get("contratante_city"):
            contratante_city = request.query_params.get("contratante_city")

        # Converte queryset para lista para poder ordenar com priorização
        workers = list(queryset.distinct())

        # Filtra por rating mínimo (feito em Python pois avg_rating é @property)
        if rating:
            try:
                min_rating = float(rating)
                workers = [w for w in workers if w.avg_rating and w.avg_rating >= min_rating]
            except ValueError:
                pass

        # Priorização: locais primeiro, depois por avg_rating decrescente
        if contratante_city:
            def sort_key(w):
                is_local = w.city.lower() == contratante_city.lower()
                avg = w.avg_rating or 0
                return (not is_local, -avg)  # locais primeiro (False < True)
            workers.sort(key=sort_key)
        else:
            workers.sort(key=lambda w: -(w.avg_rating or 0))

        serializer = WorkerListSerializer(
            workers,
            many=True,
            context={"contratante_city": contratante_city}
        )

        return Response({
            "count": len(workers),
            "contratante_city": contratante_city,
            "results": serializer.data,
        })
