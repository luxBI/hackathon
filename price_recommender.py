

# data manipulation, low-level computing, graphing.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict

# feature engineering.
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from scipy.spatial.distance import euclidean, cityblock, cosine

def recommend_price(df_raw, product_name, rating, brand_name, product_cat, parent_cat, size):

  df_index = df_raw.copy()
  def nearest_k(query, objects, k, dist):
      """Return the indices to objects most similar to query

      Parameters
      ----------
      query : ndarray
          query object represented in the same form vector representation as the
          objects
      objects : ndarray
          vector-represented objects in the database; rows correspond to
          objects, columns correspond to features
      k : int
          number of most similar objects to return
      dist : function
          accepts two ndarrays as parameters then returns their distance

      Returns
      -------
      ndarray
          Indices to the most similar objects in the database
      """
      return np.argsort([dist(query, o) for o in objects])[:k]

  def split_1(x):
    try:
      y = x[1]
    except IndexError:
      y = np.nan
    return y

  def split_2(x):
    try:
      y = x[2]
    except IndexError:
      y = np.nan
    return y

  # prepare the dataset.

  # convert text features into lower.
  df_index.drop([
                'published_date'
  ], axis=1, inplace=True)

  # fill na in rating with most frequent.
  df_index.rating.fillna(df_index.rating.value_counts().index[0],
                        inplace=True)

  # convert text features into lower.
  col_names = ['product_name',
              'rating',
              'brand_name',
              'product_category',
              'parent_category',
              'idx_mat',
              'idx_style',
              'idx_size',
              'idx_color']

  for col in col_names:
    df_index[col] = df_index[col].str.lower()

  # create subtypes for idx_mat.
  df_index['idx_mat_1'] = df_index.idx_mat.str.split(':').apply(lambda x: x[0])

  df_index['idx_mat_2'] = df_index.idx_mat.str.split(':').apply(split_1)
  df_index['idx_mat_2'] = df_index.idx_mat_2.replace(to_replace='coated canvas',
                                                    value='canvas')
  df_index['idx_style_1'] = df_index.idx_style.str.split(' ').apply(lambda x: x[0])

  df_index['idx_style_2'] = df_index.idx_style.str.split(' ').apply(split_1)
  df_index['idx_style_3'] = df_index.idx_style.str.split(' ').apply(split_2)

  # replace bags by bag in parent_category.
  df_index.parent_category = df_index.parent_category.replace(
      to_replace='bags',
      value='bag'
  )

  df_index.fillna('', inplace=True)

  # create bow feature
  df_index['bow'] = df_index.product_name + ' ' +\
                    df_index.idx_color + ' ' +\
                    df_index.idx_mat_1 + ' ' +\
                    df_index.idx_mat_2 + ' ' +\
                    df_index.idx_style_1 + ' ' +\
                    df_index.idx_style_2 + ' ' +\
                    df_index.idx_style_3

  df_index.drop([
                'index_id',
                'idx_code',
                'idx_mat',
                'idx_style',
                'sku'
  ], axis=1, inplace=True)

  X = df_index.drop(['cost_usd',
                    'acquire_date',
                    'idx_var',
                    'product_name',
                    'idx_color',
                    'idx_mat_1',
                    'idx_mat_2',
                    'idx_style_1',
                    'idx_style_2',
                    'idx_style_3',
                    'bow'],
                    axis=1)
  Y = df_index.cost_usd

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
  tfidf.fit(df_index.bow)

  bow_name_idf  = tfidf.transform(df_index.bow).toarray()
  bow_feat_names = tfidf.get_feature_names()

  df = pd.concat([pd.DataFrame(bow_name_idf,
              columns=bow_feat_names),
                filters_df],
                axis=1)

  query = [product_name.lower()]

  # format: rating, brand_name, product_cat, parent_cat, idx_size,
  input = [rating, brand_name, product_cat, parent_cat, size]
  # input = [text.lower() for text in input]

  a = tfidf.transform(query).toarray()[0].reshape(1,-1)
  b = ohe.transform(np.array(input).reshape(1,-1)).toarray()
  q = np.hstack([a, b])[0]
  search_results = nearest_k(q, df.values, 10,
                                euclidean)

  product_cost_result = df_index.iloc[search_results].cost_usd

  return product_cost_result.min(), product_cost_result.max()
