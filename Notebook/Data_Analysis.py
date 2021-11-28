#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import seaborn as sns

review_data = pd.read_csv('waikiki_hotels_reviews_all.csv', sep=';')


# In[2]:


review_data.head()


# In[3]:


review_data.info()


# In[4]:


review_data['Lang'].unique()


# In[5]:


review_data['Hotel Name'].unique()


# In[6]:


Eng_Review = review_data.loc[(review_data['Lang'] == 'en')]


# In[7]:


len(Eng_Review)


# # Visualization: plotting a pie chart of ratings

# In[8]:


#Viz Data preparation 
Viz = Eng_Review['Review Stars'].value_counts().rename_axis(['Review Stars']).reset_index(name='counts')
    


# In[9]:


# Plotting  pie chart for ratings
import plotly
import plotly.express as px
fig_pie = px.pie(values=Viz.counts, names=Viz['Review Stars'], title='Rating Distribution of the Data',color_discrete_sequence=px.colors.qualitative.Pastel)
fig_pie.show()


# # Bigram_model

# In[10]:


Review_DF = Eng_Review[['Review','Review Stars']]


# In[11]:


Review_DF.isnull().sum()


# ### Review Text Processing using NLTK

# In[12]:


def cleanText(text, tokenization = True):
    ''' standardize text to extract words
    '''
    # text to lowercase
    text = text.lower()
    # remove numbers
    text = ''.join([i for i in text if not i.isdigit()]) 
    # remove punctuation
    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'\w+') # preserve words and alphanumeric
    text = tokenizer.tokenize(text)
    # remove stopwords
    from nltk.corpus import stopwords
    stop = set(stopwords.words('english'))
    text = [w for w in text if w not in stop] 
    # lemmatization
    from nltk.stem import WordNetLemmatizer 
    lemmatizer = WordNetLemmatizer() 
    text = [lemmatizer.lemmatize(word) for word in text]
    text=' '.join(text)
    # return clean token
    return(text)


# In[13]:


Review_DF['cleaned_review']=pd.DataFrame(Review_DF.Review.apply(cleanText))


# In[14]:


Review_DF.head(10)


# ### Model Training

# In[15]:


from sklearn.model_selection import train_test_split
Independent_var=Review_DF.cleaned_review
Dependent_var=Review_DF['Review Stars']
IV_train,IV_test, DV_train, DV_test = train_test_split(Independent_var, Dependent_var, test_size=0.2, random_state=42)

print('IV_train :', len(IV_train))
print('IV_test :', len(IV_test))
print('DV_train :', len(DV_train))
print('DV_test :', len(DV_test))


# In[16]:


from sklearn.base import TransformerMixin
from sklearn.base import BaseEstimator, RegressorMixin
import pandas as pd

class ToDataFrame(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X,y=None):
        return pd.DataFrame(X)


# In[73]:


from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer
tfvec_test = TfidfVectorizer(max_features=10000,
                         max_df = 0.9,
                         ngram_range=(1,2),)
bigram_test = make_column_transformer((tfvec_test, 'cleaned_review'))


# In[74]:


from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
bigram_model_test = Pipeline([
    ('todataframe', ToDataFrame()),
    ('bigram', bigram_test),
    ('Ridge',Ridge()),
])


# In[75]:


bigram_model_test.get_params().keys()


# In[76]:


parameters_bigram= {
  'bigram__tfidfvectorizer__max_df':(0.5,1,0.1),
  'bigram__tfidfvectorizer__min_df':[0,10,50,100,500],  
  }


# In[77]:


from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV

bigram_ridge = GridSearchCV(bigram_model_test, parameters_bigram, n_jobs=2, cv=3)
bigram_ridge.fit(IV_train, DV_train)


# In[22]:


bigram_ridge.best_params_


# In[23]:


from sklearn.compose import make_column_transformer
from sklearn.feature_extraction.text import TfidfVectorizer
tfvec = TfidfVectorizer(max_features=10000,
                        ngram_range=(1,2),
                        max_df=0.8,
)
preprocess_bigram = make_column_transformer((tfvec, 'cleaned_review'))


# In[24]:


from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
ridge=Ridge(alpha=1)
bigram_model = Pipeline([
    ('todataframe', ToDataFrame()),
    ('bigram', preprocess_bigram),
    ('Ridge',ridge),
])


# In[25]:


bigram_model.fit(IV_train, DV_train)


# In[26]:


bigram_model.score(IV_train, DV_train)


# In[27]:


bigram_model.score(IV_test, DV_test)


# # Predicting Review Scores for Kaggle data

# In[28]:


kaggle_data = pd.read_csv('Kaggle Hotel Review train.csv')


# In[29]:


kaggle_data['cleaned_review']=pd.DataFrame(kaggle_data.Description.apply(cleanText))


# In[30]:


Predict_data=kaggle_data[:1000]


# In[31]:


bigram_model.fit(Independent_var, Dependent_var)


# In[32]:


Kaggle_predict=bigram_model.predict(Predict_data)


# In[33]:


Predict_data


# In[34]:


Predict_data['predict_score']= Kaggle_predict


# In[35]:


Predict_data


# In[36]:


def score(x):
    if x >=5:
        return 5
    if 1<x<5:
        return int(x)
    if x<=1:
        return 1
    
    
    
    


# In[37]:


Predict_data['predict_score']=Predict_data['predict_score'].apply(score)


# In[38]:


Predict_data['predict_score'].unique()


# In[39]:


Predict_data['Review_ID'] = Predict_data.index+1


# In[40]:


Predict_data


# # Visualization of Prediction Result

# In[42]:


import matplotlib.pyplot as plt


# Add some formatting to the plot:
plt.xlabel('Review_ID')
plt.ylabel('Predict_Review_Score')
plt.title('Prediction of Review stars')

g=sns.scatterplot(x='Review_ID', y='predict_score', data=Predict_data, hue='Is_Response')

g.legend(loc='center right',bbox_to_anchor=(1.3,0.5))


# In[43]:


plt.show(g)


# # WordCloud for Polarity Reviews

# In[44]:


def cleanText2(text, tokenization = True):
    ''' standardize text to extract words
    '''
    # text to lowercase
    text = text.lower()
    # remove numbers
    text = ''.join([i for i in text if not i.isdigit()]) 
    # remove punctuation
    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'\w+') # preserve words and alphanumeric
    text = tokenizer.tokenize(text)
    # remove stopwords
    from nltk.corpus import stopwords
    stop = set(stopwords.words('english'))
    stop = stop.union({'th', 'would','ll', 've'})
    text = [w for w in text if w not in stop] 
    # lemmatization
    from nltk.stem import WordNetLemmatizer 
    lemmatizer = WordNetLemmatizer() 
    text = [lemmatizer.lemmatize(word) for word in text]
    text=' '.join(text)
    # return clean token
    return(text)


# In[45]:


Review_DF['cleaned_review2']=pd.DataFrame(Review_DF.Review.apply(cleanText2))


# In[46]:


Review_DF.head(10)


# ### Positive Reviews

# In[47]:


from sklearn.feature_extraction.text import CountVectorizer
max_features = 10000
tf_vectorizer = CountVectorizer(min_df=0.01, max_df=0.9, ngram_range=(2,2), max_features=max_features)




# In[48]:


star_5 = Review_DF.loc[Review_DF['Review Stars']==5] 


# In[49]:


star_5


# In[50]:


ft_5= tf_vectorizer.fit_transform(star_5['cleaned_review2'])


# In[51]:


word_5_list=tf_vectorizer.get_feature_names()
count_5_list=ft_5.toarray().sum(axis=0)


# In[52]:


count_5_list


# In[53]:


word_5_df=pd.DataFrame(
    {
      'word':  word_5_list,
     'count':count_5_list     
    })


# In[54]:


Top_word_star5=word_5_df.sort_values('count',ascending=False)[:25]


# In[55]:


Top_word_star5


# In[58]:


pos_fr25=dict(zip(Top_word_star5['word'], Top_word_star5['count']))


# In[59]:


pos_fr25


# ### Visualization: WordCloud of Top 25 Words in Positive Reviews

# In[60]:


from wordcloud import WordCloud
wordcloud = WordCloud(background_color='white').fit_words(pos_fr25)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()


# ### Negative Reviews

# In[61]:


neg_review = Review_DF.loc[Review_DF['Review Stars']<=2] 


# In[62]:


neg_review


# In[63]:


tf_neg= tf_vectorizer.fit_transform(neg_review['cleaned_review2'])


# In[64]:


neg_text_list=tf_vectorizer.get_feature_names()
count_neg_list=tf_neg.toarray().sum(axis=0)


# In[65]:


count_neg_list


# In[66]:


word_neg_df=pd.DataFrame(
    {
      'word':  neg_text_list,
     'count':count_neg_list     
    })


# In[68]:


Top_word_neg=word_neg_df.sort_values('count',ascending=False)[:25]


# In[69]:


Top_word_neg


# In[70]:


neg_fr25=dict(zip(Top_word_neg['word'], Top_word_neg['count']))


# In[71]:


neg_fr25


# ### Visualization: WordCloud of Top 25 Words in Negative Reviews

# In[72]:


from wordcloud import WordCloud
wordcloud = WordCloud(background_color='white').fit_words(neg_fr25)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.margins(x=0, y=0)
plt.show()

