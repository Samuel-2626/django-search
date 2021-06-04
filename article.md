# Search in Django

As your web app grows to include many rows in your database, adding a search functionality for your users is a given to have.

In this article, we will be adding a basic search feature and scaling it up to a more complex search the PostgreSQL provides using the `django.contrib.postgres` module.

## Dependencies

- Docker v19.03.8

## Contents

- Objective
- Project Setup and Overview
- Q objects and icontains django filter
- Understanding full-text search
- Stemming and ranking our queries
- Adding weights to our queries
- Conclusion

## Objectives

By the end of this tutorial, you should be able to:

1. Setup a basic search feature using the Q objects module,
2. add full-text search to your app,
3. stem and rank your query result,
4. add weights to your queries.

## Project Setup and Overview

Clone down the base project from the [django-search](https://github.com/Samuel-2626/django-search) repo.

```bash
git clone https://github.com/Samuel-2626/django-search.git

cd django-search
```

Since we would be using PostgreSQL as our database to tap into some added features it provides, we would be using Docker as it's easy to set up and configure with it.

From the project root, create the images and spin up the Docker containers.

```bash
docker-compose up -d --build
```

Next, apply the migrations:

```bash
docker-compose exec web python manage.py migrate
```

Next, create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

Once it has been created, navigate to `http://127.0.0.1:8000/quotes/` to ensure the app works as expected. You should see the following HTML page. 

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/homepage.png)

Take a look at the project structure and code before moving on.

We created a basic quote-taking model that we can use to practice what we will be building. 

```py
from django.db import models

# new

class QuoteTaking(models.Model):
  name = models.CharField(max_length=250)
  quote = models.TextField(max_length=1000)

  def __str__(self):
    return self.quote
```

Next, add some quotes from the admin page:

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/admin.png)

After adding them navigate back to quote homepage.

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/homepage_2.png)


In our `quote.html` file, we have a basic form with a search input field.

```html
<form action="{% url 'search_results' %}" method="get">
  <input type="search" name="q" placeholder="Search by name or quote..." class="form-control">
</form>
```

The search form would be using the `GET` method rather than the `POST` method so we can have access to the query string both in the URL and in our view `class` or `function`. Having the query string appear in the URL enables us to be able to share it with others as a link vividly. We gave our search input field a name called `q`. This would allow us to be able to reference this field in our view class later on.


## Q objects and icontains Django filter

We will start off our search journey by taking a look at the __Q objects__. The __Q objects__ allow us to search words using the `"OR"` or `"AND"` logical operator. The `|` symbol represents the `"OR"` logical operator while the `&` symbol represents the `"AND"` logical operator.

```py
from django.db.models import Q

# new

class SearchResultsList(ListView):
  model = QuoteTaking
  context_object_name = 'quotes'
  template_name = 'search.html'

  def get_queryset(self):
    query = self.request.GET.get('q')
    return QuoteTaking.objects.filter(
      Q(name__icontains=query) | Q(quote__icontains=query)
    )
```

From the code above we use the filter method to filter against the **_name_** or **_quote_** field, and we also use the `icontains django filter` to check if the word is contained in the field (case insensitive). If it is contained, the field will be returned.

Add the code to your `views.py` under the quote app and navigate to the homepage to try it out. In my example I searched for the word `django`

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/search.png)

For hobby projects that uses the default database that comes installed with Django (sqlite3), this could be a very good way of adding a search functionality to your app. 

For more complex project, we would be taking a look at full-text search in the next section.

## Understanding full-text search

__Full-text search__ allows us to perform even more complex search lookups, we can retrieve similar words. For example words like __child__ and __childern__ should be treated as similar words. We can also place more importance to a particular field in our database over others, we can as well rank our result by our relevant they are.

They are useful when you start considering large blocks of text.

With full-text search, words such as “a”, “the”, “and”, etc are ignored. These words are known as __stop words__ .

Also, full-text search are case insensitive.

To use this feature `django.contrib.postgres` must added to your `INSTALLED_APPS`list.

```py
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

#### To search for a single field in our database 

```py
class SearchResultsList(ListView):
  model = QuoteTaking
  context_object_name = 'quotes'
  template_name = 'search.html'

  def get_queryset(self):
    query = self.request.GET.get('q')
    return QuoteTaking.objects.filter(quote__search=query)
```

From the example above, we are only searching the quote field in our database, we could as well search using the name field.

#### To filter on a combination of fields

To filter on a combination of fields and on related models we use the `SearchVector` method.

```py
from django.contrib.postgres.search import SearchVector

class SearchResultsList(ListView):
  model = QuoteTaking
  context_object_name = 'quotes'
  template_name = 'search.html'

  def get_queryset(self):
    query = self.request.GET.get('q')
    return QuoteTaking.objects.annotate(
      search=SearchVector('name', 'quote')
    ).filter(search=query)
```

From the example above we are searching the name or quote field.

## Stemming and ranking our queries

__Stemming__ is the process of reducing words to their word stem, base, or root form. Wherefore, words like *child* and *children* would be considered similar words while ranking allows us to order our results by relevancy.

We would be combining both to make a very robust search.

```py
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchResultsList(ListView):
  model = QuoteTaking
  context_object_name = 'quotes'
  template_name = 'search.html'

  def get_queryset(self):
    query = self.request.GET.get('q')
    search_vector = SearchVector('name', 'quote')
    search_query = SearchQuery(query)
    return QuoteTaking.objects.annotate(
      search=search_vector,
      rank=SearchRank(search_vector, search_query)
    ).filter(search=search_query).order_by('-rank')
```

From the code above, the `SearchVector` allows us to search against multiple fields. In our example, we are searching either the __name__ or __quote__ field.

`SearchQuery` translates the words provided to us as a query from the form and passes it through a __stemming algorithm__, and then it looks for matches for all of the resulting terms.

The `SearchRank` allows us to order the results by relevancy. It takes into account how often the query terms appear in the document, how close the terms are on the document, and how important the part of the document is where they occur.

Add the code to your `views.py` under the quote app and navigate to the homepage to try it out.

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/search_2.png)

If we compare the result from the __Q objects__ to that of the __full-text search__, there is a clear difference. In the full-text search, the query with the highest results are shown first, this is the power of the `SearchRank`.

Combining these three method we get a powerful search functionality.

In this section, you were introduced to full-text search using the PostgreSQL module supported by Django to create complex lookups like searching similar words, ranking words, etc. In the concluding section, we would add weights to our queries.

## Adding weights to our queries

If you want to give more importance to a particular field in your database than the order, you can add weight to your queries.

The weight should be one of the following letters D, C, B, A. By default, these weights refer to the numbers 0.1, 0.2, 0.4, and 1.0 respectively.

```python
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

class SearchResultsList(ListView):
  model = QuoteTaking
  context_object_name = 'quotes'
  template_name = 'search.html'

  def get_queryset(self):
    query = self.request.GET.get('q')
    search_vector = SearchVector('name', weight='B') + SearchVector('quote', weight='B')  
    search_query = SearchQuery(query)
    return QuoteTaking.objects.annotate(
      rank=SearchRank(search_vector, search_query)
    ).filter(rank__gte=0.3).order_by('-rank')
```

From the code above, we added weights to the `SearchVector` using the __name__ and __quote__ fields. We applied weight of 0.4 and 0.3 to the name and quote field respectively. Therefore, name matches would prevail over quote content matches and we then filtered the results to display only the ones that are greater than 0.3

## Conclusion

In this article, we guided you through setting up a basic search feature for your Django app and then taking it up a notch to a full-text search using the PostgreSQL module.

Read more about [Q objects](https://docs.djangoproject.com/en/3.2/topics/db/queries/#complex-lookups-with-q-objects) .

Read more about [Perfomance with full-text search](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#performance) .

Grab the code from the [repo](https://github.com/Samuel-2626/django-search).