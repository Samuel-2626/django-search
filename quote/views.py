from .models import Quote
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

# Create your views here.


class QuoteList(ListView):
    model = Quote
    context_object_name = "quotes"
    template_name = "quote.html"
    paginate_by = 10


""" Q objects """


class SearchResultsList(ListView):
    model = Quote
    context_object_name = "quotes"
    template_name = "search.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Quote.objects.filter(
            Q(name__icontains=query) | Q(quote__icontains=query)
        )


# """ Single Field Search """

# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         return Quote.objects.filter(quote__search=query)


""" Multi Field Search """

# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         return Quote.objects.annotate(
#             search=SearchVector('name', 'quote')
#         ).filter(search=query)


""" Stemming and Ranking """

# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         search_vector = SearchVector('name', 'quote')
#         search_query = SearchQuery(query)
#         return Quote.objects.annotate(
#             search=search_vector,
#             rank=SearchRank(search_vector, search_query)
#         ).filter(search=search_query).order_by('-rank')


""" Adding Weights """


# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         search_vector = SearchVector('name', weight='B') + SearchVector('quote', weight='A')
#         search_query = SearchQuery(query)
#         return Quote.objects.annotate(
#             rank=SearchRank(search_vector, search_query)
#         ).filter(rank__gte=0.3).order_by('-rank')
