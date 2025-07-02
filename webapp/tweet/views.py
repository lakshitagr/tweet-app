from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.db.models import Q
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import WebAuthnCredential
from django.contrib.auth import login
import requests

def index(request):
    return render(request, 'index.html')



def tweet_list(request):
    search_query = request.GET.get('q', '')

    if search_query:
        tweets = Tweet.objects.filter(
            user__username__icontains=search_query
        ).order_by('-created_at')
    else:
        tweets = Tweet.objects.all().order_by('-created_at')

    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'search_query': search_query
    })





@login_required
def tweet_create(request):
    # if not WebAuthnCredential.objects.filter(user=request.user).exists():
    #     return redirect('fingerprint_register')  # ⛔ Block if fingerprint not set
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data['text']
            photo = form.cleaned_data.get('photo')

            tweet = Tweet(user=request.user)
            tweet.text = text
            if photo:
                tweet.set_photo(photo)
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form, 'tweet_id': None})


@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet.text = form.cleaned_data['text']
            if form.cleaned_data.get('photo'):
                tweet.set_photo(form.cleaned_data['photo'])
            tweet.save()
            return redirect('tweet_list')
    else:
        # Pre-fill form with decrypted values
        form = TweetForm(initial={
            'text': tweet.text,
        })

    return render(request, 'tweet_form.html', {
        'form': form,
        'tweet_id': tweet.id,
        'tweet_image_url': request.build_absolute_uri(
            reverse('view_tweet_image', args=[tweet.id])
        ) if tweet.get_photo_bytes() else None
    })

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})




def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('tweet_list')  # ✅ Redirect here
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})





# 🔐 New view: Serve encrypted image
def view_tweet_image(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    image_data = tweet.get_photo_bytes()
    if not image_data:
        raise Http404("No image found")
    return HttpResponse(image_data, content_type='image/jpeg')





def news_list(request):
    api_url = "https://newsapi.org/v2/top-headlines"
    params = {
        'country': 'us',
        'apiKey': 'ac19266c18c74d18aa6bf3090636ae29',
        'pageSize': 100,     # optional: limit articles
        'language': 'en',   # optional
    }

    response = requests.get(api_url, params=params)

    articles = []
    if response.status_code == 200:
        data = response.json()
        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'image_url': article.get('urlToImage'),
                'published_at': article.get('publishedAt'),
                'author': article.get('author'),
                'location': article.get('source', {}).get('name'),
                'category': 'Top Headlines',  # optional static label
                'url': article.get('url'),    # add article URL for "Read" links
            })
    else:
        print("Error fetching news:", response.text)

    return render(request, 'news_list.html', {'articles': articles})
