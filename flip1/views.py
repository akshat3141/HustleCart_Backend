from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RecommendationSerializer
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.shortcuts import render, redirect
import csv
import random



tfidf_vectorizer = TfidfVectorizer(stop_words='english')

# class RecommendationAPIView(APIView):

#     def get(self, request, entered_id):
#         L = self.ok(entered_id)
#         serializer = RecommendationSerializer({
#             'first_value': L[0],
#             'second_value': L[1],
#             'third_value': L[2],
#             'fourth_value': L[3],
#             'fifth_value': L[4]
#         })
#         return Response(serializer.data, status=status.HTTP_200_OK)


def home(request):
    if request.method == 'POST':
        entered_id = request.POST['number_input']
        return redirect('recc', entered_id=entered_id)
    return render(request, 'flip1/home.html')

def ok(entered_id):
    new_df1 = pd.read_csv('static/final_df.csv')
    new_df = new_df1[['id','productDisplayName','tags','link']]  
    idx = new_df[new_df['id']==entered_id].index[0]
    tfidf_vector = tfidf_vectorizer.fit_transform([new_df.iloc[idx]['tags']])
    distances = cosine_similarity(tfidf_vector, tfidf_vectorizer.transform(new_df['tags']))
    distances = distances.flatten()
    # print(distances)
    similar_indices = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:6]
    # print(similar_indices)
    L = []
    for i in similar_indices:
        display_name = (new_df.iloc[i[0]].productDisplayName)
        product_id = (new_df.iloc[i[0]].id)
        link = (new_df.iloc[i[0]].link)
        pair = (display_name,product_id,link)
        L.append(pair)
    return L

class RecommendationAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Retrieve 'entered_id' from the query parameters
            entered_id = request.GET.get('entered_id')
            
            # Check if 'entered_id' is provided
            if entered_id is None:
                return Response({'error': 'Please provide the entered_id'}, status=400)
            
            # Call the function to process the entered_id and get recommendations
            recommendations = ok(int(entered_id))
            
            # Check if recommendations were obtained successfully
            if not recommendations:
                return Response({'error': 'Failed to get recommendations'}, status=500)
            
            # Create a context dictionary with recommendation values

            # Return the context as a JSON response
            return Response(recommendations)
        except Exception as e:
            # Handle any unexpected exceptions and return an error response
            error_message = str(e)
            return Response({'error': error_message}, status=500)


class ProductDetailView(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')  # Get the product_id from query parameter

        if not product_id:
            return Response({"error": "product_id parameter is required"}, status=400)

        # Replace 'your_csv_file_path' with the actual path to your CSV file
        # so this will look into the dataset 
        # this will revert the matched row
        with open('static/final_df.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['id'] == product_id:
                    return Response(row)

        return Response({"error": "Product not found"}, status=404)


class ProductSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if query:
            query = query.lower()
            results = self.search_by_tags(query)[:5]
        else:
            results = []
        return Response(results)

    def search_by_tags(self, query):
        new_df1 = pd.read_csv('static/final_df.csv')
        new_df = new_df1[['id', 'productDisplayName', 'tags', 'link']]

        # Create a TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(new_df['tags'])

        # Transform the query using the same vectorizer
        query_vector = tfidf_vectorizer.transform([query])

        # Calculate cosine similarity between query vector and all tags vectors
        similarities = cosine_similarity(query_vector, tfidf_matrix)

        # Get indices of the most relevant results
        relevant_indices = similarities.argsort()[0][::-1][:10]

        results = []
        for idx in relevant_indices:
            display_name = new_df.iloc[idx]['productDisplayName']
            product_id = new_df.iloc[idx]['id']
            link = new_df.iloc[idx]['link']
            results.append({ 'key': str(product_id),'value': display_name})

        return results


class AutocompleteView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if query:
            query = query.lower()
            suggestions = [result['display_name'] for result in self.search_by_tags(query)[:5]]
            return Response(suggestions)
        return Response([])

    def search_by_tags(self, query):
        new_df1 = pd.read_csv('static/final_df.csv')
        new_df = new_df1[['id', 'productDisplayName', 'tags', 'link']]

        # Create a TF-IDF vectorizer
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(new_df['tags'])

        # Transform the query using the same vectorizer
        query_vector = tfidf_vectorizer.transform([query])

        # Calculate cosine similarity between query vector and all tags vectors
        similarities = cosine_similarity(query_vector, tfidf_matrix)

        # Get indices of the most relevant results
        relevant_indices = similarities.argsort()[0][::-1][:10]

        results = []
        for idx in relevant_indices:
            display_name = new_df.iloc[idx]['productDisplayName']
            product_id = new_df.iloc[idx]['id']
            link = new_df.iloc[idx]['link']
            results.append({'display_name': display_name, 'product_id': product_id, 'link': link})

        return results

def recom2(id):
    result_list = []
    new_df = pd.read_csv('static/final_df.csv')
    type_of_id = new_df.loc[new_df['id'] == id, '1'].values[0]
    candidates = new_df[new_df['Type'] == type_of_id].index.tolist()
    random_row_index = random.choice(candidates)
    random_row = new_df.loc[random_row_index]
    result_list.append((random_row['productDisplayName'], random_row['id'],random_row['link']))

    type_of_id2 = new_df.loc[new_df['id'] == id, '2'].values[0]
    candidates2 = new_df[new_df['Type'] == type_of_id2].index.tolist()
    random_row_index2 = random.choice(candidates2)
    random_row2 = new_df.loc[random_row_index2]
    result_list.append((random_row2['productDisplayName'],random_row['id'], random_row2['link']))

    type_of_id3 = new_df.loc[new_df['id'] == id, '3'].values[0]
    candidates3 = new_df[new_df['Type'] == type_of_id3].index.tolist()
    random_row_index3 = random.choice(candidates3)
    random_row3 = new_df.loc[random_row_index3]
    result_list.append(( random_row3['productDisplayName'],random_row['id'],random_row3['link']))

    return result_list

class ProductRelatedSuggestionsView(APIView):
    def get(self, request, *args, **kwargs):
        _id = request.GET.get('id')
        print(_id)
        res =  recom2(int(_id))
        return Response(res)
