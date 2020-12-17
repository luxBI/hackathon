

import pandas as pd
import numpy as np

from collections import defaultdict
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from scipy.spatial.distance import euclidean

def recommend_price(df_XY, product_name, rating, brand_name, product_cat, parent_cat, size):
  X = df_XY.iloc[:, :5]
  Y = df_XY.cost_usd
  bow = df_XY.bow

  def nearest_k(query, objects, k, dist):
      return np.argsort([dist(query, o) for o in objects])[:k]
  
  # One Hot Encode filters.
  ohe = OneHotEncoder().fit(X)
  filters = ohe.transform(X).toarray()
  filters_feat_names = ohe.get_feature_names()
  filters_df = pd.DataFrame(filters,
              columns=filters_feat_names)

  # TFIDF - vectorize product name
  tfidf = TfidfVectorizer(stop_words='english', 
                          min_df=0.001,
                          max_df=0.999)
  tfidf.fit(bow)

  bow_name_idf  = tfidf.transform(bow).toarray()
  bow_feat_names = tfidf.get_feature_names()

  df = pd.concat([pd.DataFrame(bow_name_idf, 
              columns=bow_feat_names),
                filters_df],
                axis=1)

  query = [product_name.lower()]

  # format: rating, brand_name, product_cat, parent_cat, idx_size, 
  input = [rating, brand_name, product_cat, parent_cat, size]
  input = [text.lower() for text in input]

  a = tfidf.transform(query).toarray()[0].reshape(1,-1)
  b = ohe.transform(np.array(input).reshape(1,-1)).toarray()
  q = np.hstack([a, b])[0]
  search_results = nearest_k(q, df.values, 10, 
                                euclidean)
  product_cost_result = Y.iloc[search_results]

  return product_cost_result.min(), product_cost_result.max()