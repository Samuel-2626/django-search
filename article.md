# Basic and Full-text Search with Django and Postgres

Unlike relation databases, full-text search is not standardized. There are a number of open-source options like ElasticSearch, Solr, and Xapian. ElasticSearch is probably the most popular solution; however, it's complicated to set up and maintain. Further, if you're not taking advantage of some of the advanced features that ElasticSearch offers, you should stick with the full-text search capabilities than many relational (Postgres, MySQL, SQLite) and non-relational databases (MongoDB and CouchDB) offer. Postgres in particular is well-suited for full-text search. [Django supports it out-of-the-box](https://docs.djangoproject.com/en/3.1/ref/contrib/postgres/search/) as well.

For the vast majority of your Django apps, you should at the very least start out with leveraging full-text search from Postgres before looking to a more powerful solution like ElasticSearch or Solr.

In this article, we'll add basic and advanced full-text search to a Django app with Postgres.

## Objectives

By the end of this article, you should be able to:

1. Set up basic search functionality in a Django app with the Q object
2. Add full-text search to a Django app
3. Stem and rank your query results
4. Add weights to your search queries

## Project Setup and Overview

Clone down the base project from the [django-search](https://github.com/Samuel-2626/django-search) repo:

```bash
$ git clone https://github.com/Samuel-2626/django-search.git
$ cd django-search
```

TODO: I would use a `v1` or `base` branch for the `base` code and keep the final code on `main`. Also, much of your code doesn't conform to PEP8 standards. I recommend applying black and flake8.

We'll be using Docker to simplify setting up and running Postgres along with Django.

From the project root, create the images and spin up the Docker containers:

```bash
$ docker-compose up -d --build
```

Next, apply the migrations and create a superuser:

```bash
$ docker-compose exec web python manage.py migrate
$ docker-compose exec web python manage.py createsuperuser
```

Once done, navigate to [http://127.0.0.1:8000/quotes/](http://127.0.0.1:8000/quotes/) to ensure the app works as expected. You should see the following:

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/homepage.png)

Take note of the `Quote` model:

```python
from django.db import models

class Quote(models.Model):
    name = models.CharField(max_length=250)
    quote = models.TextField(max_length=1000)

    def __str__(self):
        return self.quote
```

TODO: `QuoteTaking` is a bit odd for a model name. I updated it to just `Quote`.

TODO: rather than having them manually add quotes, I would create a management command that adds a number of quotes. Use faker (https://faker.readthedocs.io/en/master/) to add like 10k records.

In the *quote/templates/quote.html* file, we have a basic form with a search input field:

```html
<form action="{% url 'search_results' %}" method="get">
  <input type="search" name="q" placeholder="Search by name or quote..." class="form-control">
</form>
```

On submit, the search form sends a `GET` request rather than a`POST` so we have access to the query string both in the URL and in the Django view. Having the query string appear in the URL enables us to be able to share it with others as a link.

Take a quick look at the project structure and the rest of the code before moving on.

## Basic Search

We'll start our search journey off by taking a look at the [Q objects](https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects), which allow us to search words using the "AND" (`&`) or "OR" (`|`) logical operator.

Add the following view to *quote/views.py*:

```python
from django.db.models import Q

class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Quote.objects.filter(
            Q(name__icontains=query) | Q(quote__icontains=query)
        )
```

Here, we used the [filter](https://docs.djangoproject.com/en/3.2/topics/db/queries/#retrieving-specific-objects-with-filters) method to filter against the `name` or `quote` field. We also used [icontains](https://docs.djangoproject.com/en/3.2/ref/models/querysets/#icontains) to check if the word is contained in the field (case insensitive). If it's contained, the field will be returned.

Add the code to your `views.py` under the quote app and navigate to the homepage to try it out. In my example I searched for the word `django`

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/search.png)

TODO: why didn't we wire up a URL?

For small data sets, this is a great way to add basic search functionality to your app. You'll find that as the data grows, the search will become slower and slower. You'll then want to look at adding full-text search.

## Full-text Search

TODO: I don't love the transition here between basic and full-text search. You can set this up better by showing how basic search is an exact search. Maybe add a quote with the word "child". Then do a search for "children". Show that it doesn't come up with anything.

[Full-text search](https://en.wikipedia.org/wiki/Full-text_search) allows us to perform even more complex search lookups, we can retrieve similar words. For example words like __child__ and __children__ should be treated as similar words. We can also place more importance to a particular field in our database over others, we can as well rank our result by our relevant they are.

TODO: You can do better with your definition of full text search. Performance, relevance, and stemming are the major differentiators from a basic, exact search.

They are useful when you start considering large blocks of text.

With full-text search, words such as “a”, “the”, “and”, etc. are ignored. These words are known as [stop words](https://www.postgresql.org/docs/current/textsearch-dictionaries.html#TEXTSEARCH-STOPWORDS).

TODO: explain why it's important to ignore these words

Also, full-text search is case insensitive.

To use full-text search with Django, add `django.contrib.postgres` to your `INSTALLED_APPS` list:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # new
    'django.contrib.postgres',

]
```

### Single Field Search

```python
class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

  def get_queryset(self):
      query = self.request.GET.get('q')
      return Quote.objects.filter(quote__search=query)
```

TODO: you're still not leveraging full-text search here, right? I'm confused. Why is this in the full-text search section then?

Here, we're only searching the quote field in our database.

TODO: I guess you're wanting readers to replace the previous view?

### Multi Field Search

To filter on a combination of fields and on related models, you can use the `SearchVector` method:

```python
from django.contrib.postgres.search import SearchVector

class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

  def get_queryset(self):
      query = self.request.GET.get('q')
      return Quote.objects.annotate(
          search=SearchVector('name', 'quote')
      ).filter(search=query)
```

We're now searching against the `name` and `quote` fields.

TODO: Can you explain what a search vector is.

TODO: the single and multi field search sections don't add much. I'd remove them and explain what a search vector is below.

## Stemming and Ranking

[Stemming](https://en.wikipedia.org/wiki/Stemming) is the process of reducing words to their word stem, base, or root form. With stemming, words like *child* and *children* will be considered similar words. Ranking, on the other hand, allows us to order results by relevancy.

We can combining both these concepts to make a very robust search.

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        search_vector = SearchVector('name', 'quote')
        search_query = SearchQuery(query)
        return Quote.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=search_query).order_by('-rank')
```

What's happening here?

1. `SearchVector` - again we used a search vector to search against multiple fields.
1. `SearchQuery` - translates the words provided to us as a query from the form and passes it through a stemming algorithm and then it looks for matches for all of the resulting terms.
1. `SearchRank` - allows us to order the results by relevancy. It takes into account how often the query terms appear in the document, how close the terms are on the document, and how important the part of the document is where they occur.

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/search_2.png)

Compare the results from the Q objects to that of the full-text search. There's a clear difference. In the full-text search, the query with the highest results are shown first. This is the power of the `SearchRank`. Combining `SearchVector`, `SearchQuery`, and `SearchRank` is quick way to produce a much more powerful and precise search than the basic search.

TODO: might be worth adding django debug toolbar so one can see the search speed difference

## Adding Weights

If you want to give more importance to a particular field in your database, you can add weight to your queries.

The [weight](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#postgresql-fts-weighting-queries) should be one of the following letters D, C, B, A. By default, these weights refer to the numbers 0.1, 0.2, 0.4, and 1.0, respectively.

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        search_vector = SearchVector('name', weight='B') + SearchVector('quote', weight='B')
        search_query = SearchQuery(query)
        return Quote.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.3).order_by('-rank')
```

Here, we added weights to the `SearchVector` using both the `name` and `quote` fields. We applied weights of 0.4 and 0.3 to the name and quote field respectively. Therefore, name matches will prevail over quote content matches. We then filtered the results to display only the ones that are greater than 0.3.

TODO: they are both using a weight of B?

## Conclusion

In this article, we guided you through setting up a basic search feature for your Django app and then took it up a notch to a full-text search using the Postgres module from Django.

Read more about [Q objects](https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects) .

Read more about [Perfomance with full-text search](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#performance) .

Grab the code from the [repo](https://github.com/Samuel-2626/django-search).
