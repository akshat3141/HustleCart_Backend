from django.urls import path
from . import views

urlpatterns = [
    path('recommendation', views.RecommendationAPIView.as_view(), name='recommendation'),
    path('product', views.ProductDetailView.as_view(), name='product-detail'),
    path('search/', views.ProductSearchView.as_view(), name = 'search_results'),
    path('productrelated', views.ProductRelatedSuggestionsView.as_view(), name = 'productrelated'),
    path('autocomplete/', views.AutocompleteView.as_view() , name = 'auto_complete'),
    path('', views.home, name='home'),
    # path('recc/', views.recc, name='recc'),
]