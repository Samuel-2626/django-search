# Basic and Full-text Search with Django and Postgres

Unlike relation databases, full-text search is not standardized. There are a number of open-source options like ElasticSearch, Solr, and Xapian. ElasticSearch is probably the most popular solution; however, it's complicated to set up and maintain. Further, if you're not taking advantage of some of the advanced features that ElasticSearch offers, you should stick with the full-text search capabilities than many relational (Postgres, MySQL, SQLite) and non-relational databases (MongoDB and CouchDB) offer. Postgres in particular is well-suited for full-text search. [Django supports it out-of-the-box](https://docs.djangoproject.com/en/3.2/topics/db/search/#postgresql-support) as well.

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

We'll be adding a bunch of quotes to our database about 10k records to be precise. This will take a couple of minutes.

```bash
$ docker-compose exec web python manage.py shell
$ from quote.faker import add_fake_data
$ add_fake_data()
```

Once done, navigate to [http://127.0.0.1:8000/quotes/](http://127.0.0.1:8000/quotes/) to see the data.

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/homepage_2.png)

In the *quote/templates/quote.html* file, we have a basic form with a search input field:

```html
<form action="{% url 'search_results' %}" method="get">
  <input type="search" name="q" placeholder="Search by name or quote..." class="form-control">
</form>
```

On submit, the search form sends a `GET` request rather than a `POST` so we have access to the query string both in the URL and in the Django view. Having the query string appear in the URL enables us to be able to share it with others as a link.

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

Add the code to your `views.py` under the quote app and navigate to the homepage to try it out. In my example, I searched for the word `Django`.

![Search Page 1](https://github.com/Samuel-2626/django-search/blob/main/images/search.png)

For small data sets, this is a great way to add basic search functionality to your app. Once your data sets become large and the contents that you are searching against are also many, you'll then want to look at adding __full-text__ search.

Note also that, we should have created some URLs for our project and application level, but the code forked comes baked already with some URLs which can be seen below.

```python
from django.urls import path
from .views import QuoteList, SearchResultsList

urlpatterns = [
    path("", QuoteList.as_view(), name="all_quotes"),
    path("search/", SearchResultsList.as_view(), name="search_results"),
]
```

## Full-text Search

The basic search that we saw earlier has some limitations especially when we consider matching against large data sets. Let's take a look at some of its limitations.

In this example, bear in mind that my database has at least 10k of records, it's fairly large I should say. If a user tries to search for the letter __a__ the basic search implemented above will not ignore such words and still perform search lookups so far an exact match is gotten. This is very limited and can slow down the search query. With full-text search that will be implemented shortly, it takes care of this issue.

Another scenario is that of similar words, with the basic search only exact matches are returned. This is quite limited. With full-text search, we can have better matches as it can take into account similar words and therefore providing better results. In my database, I have a quote containing the word __pony__ and __ponies__. They should be treated as similar words but with a basic search, they are not.

![Search Page 1](https://github.com/Samuel-2626/django-search/blob/main/images/search.png)

And finally, in the example we say earlier in the previous section we couldn't give our users the most relevant result, this couldn't be done with just basic search, but with full-text search again it's possible.

Hence, [Full-text search](https://en.wikipedia.org/wiki/Full-text_search) is an advanced searching technique that examines all the words in every stored document as it tries to match the search criteria. In full-text search [stop words](https://www.postgresql.org/docs/current/textsearch-dictionaries.html#TEXTSEARCH-STOPWORDS) such as "a", "and", "the" are ignored because they are both common and insufficiently meaningful. In addition, with full-text search we can employ language-specific __stemming__ on the words being indexed for example the drives, drove, and driven will be recorded under the single concept word drive. [Stemming](https://en.wikipedia.org/wiki/Stemming) is the process of reducing words to their word stem, base, or root form.

It suffices to say that full-text search is not perfect and one of the limitations is that it is likely to retrieve many documents that are not relevant to the intended search question such documents are called __false positives__. However, techniques such as Bayesian algorithms can help reduce the problem of __false positive__.

To take advantage of Postgres full-text search with Django, add `django.contrib.postgres` to your `INSTALLED_APPS` list:

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

In the next section, we will be performing a full-text search on a single field in the quote table of our database.

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

Here, we're only searching the quote field. 

![Search Page 4](https://github.com/Samuel-2626/django-search/blob/main/images/search_4.png)

As we can also see it takes account of similar words. In my search example, __ponies__ and __pony__ are treated as similar words.

In the next section, we would take a look at performing a full-text search on multiple fields in the quote table of our database.

### Multi-Field Search

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

The `Search Vector` basically gives us the ability to search against multiple fields in the table of our database. Here, we're searching against the `name` and `quote` fields.

In the next section, we will be combining several methods such as `SearchVector`, `SearchQuery`, `SearchRank` to produce a very robust search functionality by __stemming__ and __ranking__ our search queries.

## Stemming and Ranking

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

In this example, we took advantage of some new methods. We have seen the `SearchVector` in action earlier. The `SearchQuery` translates the words provided to us as a query from the form and passes it through a stemming algorithm and then it looks for matches for all of the resulting terms while the `SearchRank` allows us to order the results by relevancy. It takes into account how often the query terms appear in the document, how close the terms are on the document, and how important the part of the document is where they occur.

![Search Page 3](https://github.com/Samuel-2626/django-search/blob/main/images/search_3.png)

In this example, I searched for the word `django`. If we compare this result with the one we got earlier with the basic search, we could see that the fields with the highest word Django are shown first.

## Adding Weights

In addition, a full-text search gives us the ability to add more importance to some fields in our table in the database over other fields. We can do this by adding weight to our queries.

The [weight](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#postgresql-fts-weighting-queries) should be one of the following letters D, C, B, A. By default, these weights refer to the numbers 0.1, 0.2, 0.4, and 1.0, respectively.

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchResultsList(ListView):
    model = Quote
    context_object_name = 'quotes'
    template_name = 'search.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        search_vector = SearchVector('name', weight='B') + SearchVector('quote', weight='A')
        search_query = SearchQuery(query)
        return Quote.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.3).order_by('-rank')
```

Here, we added weights to the `SearchVector` using both the `name` and `quote` fields. We applied weights of 0.4 and 1.0 to the name and quote field respectively. Therefore, quote matches will prevail over name content matches. We then filtered the results to display only the ones that are greater than 0.3.

## Conclusion

In this article, we guided you through setting up a basic search feature for your Django app and then took it up a notch to a full-text search using the Postgres module from Django.

Full-text is an intensive process, learn more about [perfomance with full-text search](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#performance).

Grab the code from the [repo](https://github.com/Samuel-2626/django-search).