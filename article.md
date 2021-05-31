# Add search functionality to your Django app using Docker and PostgreSQL

As your web app grows to include many rows in your database, adding a search functionality is a given to have.
In this tutorial, we will be adding a basic search feature and scaling it up to a more complex search the PostgreSQL provides with the `django.contrib.postgres` module.

## Dependencies

* Docker v19.03.8

## Contents

- Objective
- Project Setup and Overview
- Q objects and icontains django filter
- Stemming as well as ranking functionality
- Adding weights to our queries
- Conclusion

## Objectives

By the end of this tutorial, you should be able to:

1. Setup a basic search feature using the Q objects module.
2. add full-text search to your app.
3. Stem and rank your query result.
4. And finally add weights to your queries.

## Project Setup and Overview

Clone down the base project from the [django-search](https://github.com/Samuel-2626/django-search) repo.

```
git clone https://github.com/Samuel-2626/django-search.git

cd django-search
```

Since we would be using PostgreSQL as our database to tap into some added features it provides, we would be using Docker as it is easy to set up and configure with it.

From the project root, create the images and spin up the Docker containers.

```
docker-compose up -d --build
```

Next, apply the migrations:

```
docker-compose exec web python manage.py makemigrations
```

Once the build is complete, navigate to `http://127.0.0.1:8000/quotes/` to ensure the app works as expected. You should see the following HTML page. Your own database would be empty.

![Quote Home Page](https://github.com/Samuel-2626/django-search/blob/main/images/homepage.png)

Take a look at the project structure and code before moving on.

We created a basic quote taking application that you can use to practice what we will be creating. You can as well add quotes from the admin page.

```html
<form action="{% url 'search_results' %}" method="get">
  <input type="search" name="q" placeholder="Search by name or quote..." class="form-control">
</form>
```

In our `quote.html` file, we have a basic form with a search input field.

The search form would be using the `GET` method rather than the `POST` method so we can have access to the query string both in the URL and in our view `class` or `function`. Having the query string appear in the URL enables us to be able to share it with others as a link vividly. We gave our search input field a name called `q`. This would allow us to be able to reference this field in our view class later on.


## Q objects and icontains Django filter

We will start off our search journey by taking a look at the __Q objects__. The __Q objects__ allow us to create complex lookups that can use `"OR"` not just `"AND"` logical operator. The `|` symbol represents the `"OR"` logical operator.

```py
from django.db.models import Q

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

From the code above we use the filter method to filter against the **_name_** or **_quote_** field, and we also use the `icontains django filter`. When we use this filter, the query we are looking up in the database just only need to contain the word (case insensitive) even if there is little correlation between the words.

This works great if we are trying to match a string containing few characters. This becomes limited when we want to match a large block of text. To solve this we can adopt several methods, but since we are using PostgreSQL, Django provides a selection of database-specific tools to allow you to leverage more complex querying options.

`Note that` Other databases have several selections of tools, maybe via plugins or user-defined functions, but Django doesn't include support for them at this point in time.

In the meantime add this code to your `views.py` under the quote app and navigate to the homepage to try it out.

## Stemming as well as ranking functionality

We would be diving now into performing full-text searches.

Words like __child__ and __children__ should be considered similar by any search engine right? We would be taking advantage of the __full-text search__ Django provides using the `PostgreSQL module`.

__Full-text search__ allows us to perform complex search lookups, retrieving results by similarity, or by weighting terms based on how frequent they appear in the text or how important different fields are.

In our previous example under the __Q objects__, if we type just a letter in our search field so far that letter is found in any word in the database we are trying to match it perceives it as a good match, but this is not so right. With full-text searches, it prevents this as well as gives us other benefits by ignoring __stop words__ such as “a”, “the”, “and”.

To use the `search` lookup `django.contrib.postgres` must added to your `INSTALLED_APPS`list.

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
    return QuoteTaking.objects.filter(name__search=query)
```

From the example above, we are only searching the name field in our database, we could as well search for the quote field.

#### To filter on a combination of fields

To filter on a combination of fields and on related models we use the `SearchVector` method.

```py
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

Let's take a look at a more complex example using more additional methods combined.

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

`SearchQuery` translates the words provided to us as a query from the form and passes it through the __stemming algorithm__, and then it looks for matches for all of the resulting terms. __Stemming__ is the process of reducing words to their word stem, base, or root form. Wherefore, words like *child* and *children* would be considered similar words.

The `SearchRank` allows us to order the results by relevancy. It takes into account how often the query terms appear in the document, how close the terms are on the document, and how important the part of the document is where they occur.

In this section, you were introduced to full-text search using the PostgreSQL module supported by Django to create complex lookups like searching similar words, ranking words, etc. In the concluding section, we would add weights to our fields in the database.

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

When performance starts to become a problem i.e. you are becoming to have a very large database and the full-text search starts to become slow, you can check out the [SearchVectorField](https://docs.djangoproject.com/en/3.2/ref/contrib/postgres/search/#performance) and add it to your model.

Grab the code from the [repo](https://github.com/Samuel-2626/django-search).