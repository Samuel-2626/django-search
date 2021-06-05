from .models import Quote
from django.views.generic import ListView
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

# Create your views here.

class QuoteList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name='quote.html'


""" Q objects """

class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Quote.objects.filter(
            Q(name__icontains=query) | Q(quote__icontains=query)
        )


""" Searching for a single field in our database  """

# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         return Quote.objects.filter(quote__search=query)


""" Filter on a combination of fields in our database  """

# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         return Quote.objects.annotate(
#             search=SearchVector('name', 'quote')
#         ).filter(search=query)


""" Stemming and Ranking Feature """

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
  

""" Weighting Queries """


# class SearchResultsList(ListView):
#     model = Quote
#     context_object_name = 'quotes'
#     template_name = 'search.html'

#     def get_queryset(self):
#         query = self.request.GET.get('q')
#         search_vector = SearchVector('name', weight='B') + SearchVector('quote', weight='B')  
#         search_query = SearchQuery(query)
#         return Quote.objects.annotate(
#             rank=SearchRank(search_vector, search_query)
#         ).filter(rank__gte=0.3).order_by('-rank')



