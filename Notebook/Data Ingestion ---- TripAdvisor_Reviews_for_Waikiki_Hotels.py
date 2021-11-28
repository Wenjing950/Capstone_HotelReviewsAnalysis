#!/usr/bin/env python
# coding: utf-8

# # Import libraries

# In[68]:


from selenium import webdriver
import csv
import time
import requests
import re
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import math, time
import random


# # Get hotel links from Waikiki beach

# In[2]:


import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Android, 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0',
}


# In[7]:


url_waikiki = "https://www.tripadvisor.com/Hotels-g6999277-Waikiki_Oahu_Hawaii-Hotels.html"


# In[8]:


req_waikiki = requests.get(url_waikiki, headers=headers)


# In[10]:


soup_waikiki = BeautifulSoup(req_waikiki.text, "lxml")


# In[11]:


print(soup_waikiki)


# In[14]:


link_1 = soup_waikiki.find_all ('a', attrs={'class':'property_title prominent'})


# In[15]:


link_1


# In[27]:


links_1=['https://www.tripadvisor.com'+link.get('href') for link in link_1]
    


# In[28]:


links_1


# In[29]:


url_waikiki2='https://www.tripadvisor.com/Hotels-g6999277-oa30-Waikiki_Oahu_Hawaii-Hotels.html'
req_waikiki2 = requests.get(url_waikiki2, headers=headers)
soup_waikiki2 = BeautifulSoup(req_waikiki2.text, "lxml")
link_2 = soup_waikiki2.find_all ('a', attrs={'class':'property_title prominent'})
links_2=['https://www.tripadvisor.com'+link.get('href') for link in link_2]
    


# In[30]:


links_2


# In[31]:


links=links_1+links_2


# In[33]:


len(links)


# In[37]:


with open("waikiki_hotels_list.txt", "w") as f:
    f.write(str(links))


# # Get all the reviws from hotel links

# First of all, extract both the location ID and the geo ID from the hotel URL. 

# In[49]:


url_t='https://www.tripadvisor.com/Hotel_Review-g60982-d87119-Reviews-Hotel_La_Croix_Waikiki-Honolulu_Oahu_Hawaii.html'


# In[53]:


int(url_t.split('-')[1][1:])


# In[54]:


def get_ids_hotel_url(url):
    url=url.split('-')
    geo=url[1]
    loc=url[2]
    return (int(geo[1:]),int(loc[1:]))


# In[55]:


get_ids_hotel_url(url_t)


# Second, creat a function to get the GraphQL data from a certain hotel

# In[59]:


GRAPHQL_URL = 'https://www.tripadvisor.com/data/graphql/batched'

def request_graphql(url, page=0):
    geo, loc = get_ids_hotel_url(url)
    request = [
      {
          "query": "mutation LogBBMLInteraction($interaction: ClientInteractionOpaqueInput!) {\n  logProductInteraction(interaction: $interaction)\n}\n",
          "variables": {
              "interaction": {
                  "productInteraction": {
                      "interaction_type": "CLICK",
                      "site": {
                          "site_name": "ta",
                          "site_business_unit": "Hotels",
                          "site_domain": "www.tripadvisor.com"
                      },
                      "pageview": {
                          "pageview_request_uid": "X@2fPQokGCIABGTeHYoAAAES",
                          "pageview_attributes": {
                              "location_id": loc,
                              "geo_id": geo,
                              "servlet_name": "Hotel_Review"
                          }
                      },
                      "user": {
                          "user_agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
                          "site_persistent_user_uid": "web373a.83.56.0.34.17609EB3BAC",
                          "unique_user_identifiers": {
                              "session_id": '{1FC0FCEFC9A441E6BC8679486D235FA7}'
                          }
                      },
                      "search": {},
                      "item_group": {
                          "item_group_collection_key": "X@2fPQokGCIABGTeHYoAAAES"
                      },
                      "item": {
                          "product_type": "Hotels",
                          "item_id_type": "ta-location-id",
                          "item_id": loc,
                          "item_attributes": {
                              "element_type": "es",
                              "action_name": "REVIEW_FILTER_LANGUAGE"
                          }
                      }
                  }
              }
          }
      },
      {
          "query": "query ReviewListQuery($locationId: Int!, $offset: Int, $limit: Int, $filters: [FilterConditionInput!], $prefs: ReviewListPrefsInput, $initialPrefs: ReviewListPrefsInput, $filterCacheKey: String, $prefsCacheKey: String, $keywordVariant: String!, $needKeywords: Boolean = true) {\n  cachedFilters: personalCache(key: $filterCacheKey)\n  cachedPrefs: personalCache(key: $prefsCacheKey)\n  locations(locationIds: [$locationId]) {\n    locationId\n    parentGeoId\n    name\n    placeType\n    reviewSummary {\n      rating\n      count\n    }\n    keywords(variant: $keywordVariant) @include(if: $needKeywords) {\n      keywords {\n        keyword\n      }\n    }\n    ... on LocationInformation {\n      parentGeoId\n    }\n    ... on LocationInformation {\n      parentGeoId\n    }\n    ... on LocationInformation {\n      name\n      currentUserOwnerStatus {\n        isValid\n      }\n    }\n    ... on LocationInformation {\n      locationId\n      currentUserOwnerStatus {\n        isValid\n      }\n    }\n    ... on LocationInformation {\n      locationId\n      parentGeoId\n      accommodationCategory\n      currentUserOwnerStatus {\n        isValid\n      }\n      url\n    }\n    reviewListPage(page: {offset: $offset, limit: $limit}, filters: $filters, prefs: $prefs, initialPrefs: $initialPrefs, filterCacheKey: $filterCacheKey, prefsCacheKey: $prefsCacheKey) {\n      totalCount\n      preferredReviewIds\n      reviews {\n        ... on Review {\n          id\n          url\n          location {\n            locationId\n            name\n          }\n          createdDate\n          publishedDate\n          provider {\n            isLocalProvider\n          }\n          userProfile {\n            id\n            userId: id\n            isMe\n            isVerified\n            displayName\n            username\n            avatar {\n              id\n              photoSizes {\n                url\n                width\n                height\n              }\n            }\n            hometown {\n              locationId\n              fallbackString\n              location {\n                locationId\n                additionalNames {\n                  long\n                }\n                name\n              }\n            }\n            contributionCounts {\n              sumAllUgc\n              helpfulVote\n            }\n            route {\n              url\n            }\n          }\n        }\n        ... on Review {\n          title\n          language\n          url\n        }\n        ... on Review {\n          language\n          translationType\n        }\n        ... on Review {\n          roomTip\n        }\n        ... on Review {\n          tripInfo {\n            stayDate\n          }\n          location {\n            placeType\n          }\n        }\n        ... on Review {\n          additionalRatings {\n            rating\n            ratingLabel\n          }\n        }\n        ... on Review {\n          tripInfo {\n            tripType\n          }\n        }\n        ... on Review {\n          language\n          translationType\n          mgmtResponse {\n            id\n            language\n            translationType\n          }\n        }\n        ... on Review {\n          text\n          publishedDate\n          username\n          connectionToSubject\n          language\n          mgmtResponse {\n            id\n            text\n            language\n            publishedDate\n            username\n            connectionToSubject\n          }\n        }\n        ... on Review {\n          id\n          locationId\n          title\n          text\n          rating\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          photos {\n            id\n            statuses\n            photoSizes {\n              url\n              width\n              height\n            }\n          }\n          userProfile {\n            id\n            displayName\n            username\n          }\n        }\n        ... on Review {\n          mgmtResponse {\n            id\n          }\n          provider {\n            isLocalProvider\n          }\n        }\n        ... on Review {\n          translationType\n          location {\n            locationId\n            parentGeoId\n          }\n          provider {\n            isLocalProvider\n            isToolsProvider\n          }\n          original {\n            id\n            url\n            locationId\n            userId\n            language\n            submissionDomain\n          }\n        }\n        ... on Review {\n          locationId\n          mcid\n          attribution\n        }\n        ... on Review {\n          __typename\n          locationId\n          helpfulVotes\n          photoIds\n          route {\n            url\n          }\n          socialStatistics {\n            followCount\n            isFollowing\n            isLiked\n            isReposted\n            isSaved\n            likeCount\n            repostCount\n            tripCount\n          }\n          status\n          userId\n          userProfile {\n            id\n            displayName\n            isFollowing\n          }\n          location {\n            __typename\n            locationId\n            additionalNames {\n              normal\n              long\n              longOnlyParent\n              longParentAbbreviated\n              longOnlyParentAbbreviated\n              longParentStateAbbreviated\n              longOnlyParentStateAbbreviated\n              geo\n              abbreviated\n              abbreviatedRaw\n              abbreviatedStateTerritory\n              abbreviatedStateTerritoryRaw\n            }\n            parent {\n              locationId\n              additionalNames {\n                normal\n                long\n                longOnlyParent\n                longParentAbbreviated\n                longOnlyParentAbbreviated\n                longParentStateAbbreviated\n                longOnlyParentStateAbbreviated\n                geo\n                abbreviated\n                abbreviatedRaw\n                abbreviatedStateTerritory\n                abbreviatedStateTerritoryRaw\n              }\n            }\n          }\n        }\n        ... on Review {\n          text\n          language\n        }\n        ... on Review {\n          locationId\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          originalLanguage\n          rating\n        }\n        ... on Review {\n          id\n          locationId\n          title\n          labels\n          rating\n          absoluteUrl\n          mcid\n          translationType\n          mtProviderId\n          alertStatus\n        }\n      }\n    }\n    reviewAggregations {\n      ratingCounts\n      languageCounts\n      alertStatusCount\n    }\n  }\n}\n",
          "variables": {
              "locationId": loc,
              "offset": page * 20,
              "filters": [
                  {
                      "axis": "LANGUAGE",
                      "selections": [
                          "es",
                          "en",
                          "de",
                          "fr",
                          "it"
                      ]
                  }
              ],
              "prefs": None,
              "initialPrefs": {},
              "limit": 20,
              "filterCacheKey": None,
              "prefsCacheKey": "locationReviewPrefs",
              "needKeywords": False,
              "keywordVariant": "location_keywords_v2_llr_order_30_en"
          }
      },
      {
          "query": "mutation UpdateReviewSettings($key: String!, $val: String!) {\n  writePersonalCache(key: $key, value: $val)\n}\n",
          "variables": {
              "key": "locationReviewFilters_4107099",
              "val": "[{\"axis\":\"LANGUAGE\",\"selections\":[\"es\"]}]"
          }
      }
  ]
    response = requests.post(GRAPHQL_URL, json=request, headers={
      'origin': 'https://www.tripadvisor.com',
      'pragma': 'no-cache',
      'referer': url,
      'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
      'x-requested-by': 'TNI1625!AMPQUsAUz6m+TvndmqcNWd4EAv60zLWOByxblnsa3g/ghHVC2AycehsYopdE05giJ0ZLpLmlQwWHsXSqINLh7h1SkWTIIpLjdo3/52bxyVmPJmWm6H6/DlJuPvTP1j6YT98AzH2YIsKlPWQ9Cv6nYiw8thPPfeU6Kqs+Vx1YM1zV',
      'Cookie': 'TAUnique=%1%enc%3A3z0L%2FHaaMiL9ipe0HbPnhRb5ADLe5DtFZPnfE3JaluJQcF0be502LA%3D%3D; TASSK=enc%3AAIw5KUmGLzTIHAwu16pOQvvppZvLFIuq8puOvOQwOuM5fePeKZVAs%2BAfnX%2FVNq8UOW%2F5dfJvTngHxbj9K1CurT5PMAMpYW9Vc1g2TO8FzfrLbxn911LOX7qds25jOzk2Ew%3D%3D; TATrkConsent=eyJvdXQiOiIiLCJpbiI6IkFMTCJ9; __gads=ID=6a3d104800541ae3:T=1633043518:S=ALNI_MYrbRFDGi-dKjTEiUSsbw7GoHl8QQ; TADCID=2Z-_b0-pyhv1K4LbABQCFdpBzzOuRA-9xvCxaMyI12mgckBfmLLrccsetS6NntGWuj7wGB3kztI6-aLv6_3atgH8sb9Til_Oq9o; _pbjs_userid_consent_data=3524755945110770; _lc2_fpi=b140173de591--01fmx0qghfra80yawrf1t5tfe6; pbjs_pubcommonID=b43d4ef8-c691-4949-874a-68170e2633c0; TART=%1%enc%3AbiYu%2F2hIUs7zl2ycOVmPbg7d4blaI47mMbINEKPB2b5p%2BMFisVyjmG%2FqF9wjjt11yo%2BS64UqALs%3D; _ga=GA1.2.1198645610.1637358403; _gid=GA1.2.2122847930.1637358403; ServerPool=C; _li_dcdm_c=.tripadvisor.com; VRMCID=%1%V1*id.13091*llp.%2FInfoCenterV6%3Fctr%3Dcontentsolutions*e.1637971496990; TASID=1FC0FCEFC9A441E6BC8679486D235FA7; ak_bmsc=092A0D19397F28DAF0DB644B7CE419D0~000000000000000000000000000000~YAAQ5L7CF/p5yy59AQAAsMFpPQ3XOPh25e7iDPWpwmfYdqQTZzoLqo6u6Ltmn3iHIU/Yk88Vdwpj3okPAHOMmdaFdgx9L64cTCdEnDnhSa3/9F/EpNQsmi0pzpiBJdr1ndkHY1yTHkOMQCmC+bpswWKlAu+F1KlNj9LhIMPM/yqKcfFyv5RXRaIYwr/JCZYwXv6U9a3RZyY8iKneRFx2I+9NI53C77gTYt2wIJQhnff8G4Pgsz1oNOTFmgeqHei+tRwGzub6fxR53S+Sh55ZHVdaZ8yifGUpZOLPDnrOQWGHKhGwj6jB5u3+NjhxHlzR8FLycgtHs1/NMjXSuQZgFGZTpWNlPzxd737UHUtnzTW57SSlvfB8lvGmnWvFJ+NOxC45mKx/se72up+t0J+5; PAC=ACIr8NocHhhD6eGza_aMbjFw2Jh0R0V2cXp0cyu9udOOucotWuVNx5ySr4EisMv0NnDN02pDqeC5KHGeOsBdW7lGGiQQBjsOH_pGiiF1urENruLiJdy5_zR0CEd2CpRUIuJwRQgKHZrLbVvkdiBYOhCiq2Xm7WxfJXwsbdtllC0KEKcD5txbLYG5f9bU5eIJP40mr3utGuuwyPCSlJc34dSt64gYO2n0JZg2BwniHoAU; PMC=V2*MS.57*MD.20210930*LD.20211120; TATravelInfo=V2*AY.2022*AM.5*AD.7*DY.2022*DM.5*DD.8*A.2*MG.-1*HP.2*FL.3*DSM.1637413163932*RS.1; TAReturnTo=%1%%2FHotel_Review-g60982-d87119-Reviews-Hotel_La_Croix_Waikiki-Honolulu_Oahu_Hawaii.html; bm_sv=61DD3ED48BD29EE1024E4C12C6C64288~W/by1fqqMz4pm7xisiFrLyVseiUmr1MYw5wU34x0cmreY6ZP6paNgvuW5E+KKo0QTe3Y6H6QBFj+dlPtO3gsR3/PKccFObVw+gMBgcKMrC/3pLyeUQqelRBOmdLyRmrtyBAAmU56WCDfjedAtz0ayGWrPZo0tixhbIIc5X/y6wo=; __vt=8r_yQ6Fo0QSRZfdFABQCIf6-ytF7QiW7ovfhqc-AvRmB6YgjrBro_1E0ydo-C93Mww011ybfjmt--8sAgIOzaX9vrKb7QC9w3sBSZOzOZZy7HEM_1o8X40Ek6hn6A0Uco56OvjFyifgUNNK8Kip8lQJrqQ; CM=%1%PremiumMobSess%2C%2C-1%7Ct4b-pc%2C%2C-1%7CRestAds%2FRPers%2C%2C-1%7CRCPers%2C%2C-1%7CWShadeSeen%2C%2C-1%7CTheForkMCCPers%2C%2C-1%7CHomeASess%2C%2C-1%7CPremiumMCSess%2C%2C-1%7CSLMCSess%2C%2C-1%7CCrisisSess%2C%2C-1%7CUVOwnersSess%2C%2C-1%7CRestPremRSess%2C%2C-1%7CRepTarMCSess%2C%2C-1%7CCCSess%2C%2C-1%7CCYLSess%2C%2C-1%7CPremRetPers%2C%2C-1%7CViatorMCPers%2C%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7CPremiumORSess%2C%2C-1%7Ct4b-sc%2C%2C-1%7CRestAdsPers%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS2%2C%2C-1%7CTSMCPers%2C%2C-1%7Cb2bmcpers%2C%2C-1%7CPremMCBtmSess%2C%2C-1%7CMC_IB_UPSELL_IB_LOGOS%2C%2C-1%7CLaFourchette+Banners%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7CPremiumRRSess%2C%2C-1%7CTADORSess%2C%2C-1%7CAdsRetPers%2C%2C-1%7CCOVIDMCSess%2C%2C-1%7CListMCSess%2C%2C-1%7CTARSWBPers%2C%2C-1%7CSPMCSess%2C%2C-1%7CTheForkORSess%2C%2C-1%7CTheForkRRSess%2C%2C-1%7Cpers_rev%2C%2C-1%7CSPACMCSess%2C%2C-1%7CRBAPers%2C%2C-1%7CRestAds%2FRSess%2C%2C-1%7CHomeAPers%2C%2C-1%7CPremiumMobPers%2C%2C-1%7CRCSess%2C%2C-1%7CLaFourchette+MC+Banners%2C%2C-1%7CRestAdsCCSess%2C%2C-1%7CRestPremRPers%2C%2C-1%7CSLMCPers%2C%2C-1%7CRevHubRMPers%2C%2C-1%7CUVOwnersPers%2C%2C-1%7Cpssamex%2C%2C-1%7CTheForkMCCSess%2C%2C-1%7CCrisisPers%2C%2C-1%7CCYLPers%2C%2C-1%7CCCPers%2C%2C-1%7CRepTarMCPers%2C%2C-1%7Cb2bmcsess%2C%2C-1%7CTSMCSess%2C%2C-1%7CSPMCPers%2C%2C-1%7CRevHubRMSess%2C%2C-1%7CPremRetSess%2C%2C-1%7CViatorMCSess%2C%2C-1%7CPremiumMCPers%2C%2C-1%7CAdsRetSess%2C%2C-1%7CPremiumRRPers%2C%2C-1%7CCOVIDMCPers%2C%2C-1%7CRestAdsCCPers%2C%2C-1%7CTADORPers%2C%2C-1%7CSPACMCPers%2C%2C-1%7CTheForkORPers%2C%2C-1%7CPremMCBtmPers%2C%2C-1%7CTheForkRRPers%2C%2C-1%7CTARSWBSess%2C%2C-1%7CPremiumORPers%2C%2C-1%7CRestAdsSess%2C%2C-1%7CRBASess%2C%2C-1%7CSPORPers%2C%2C-1%7Cperssticker%2C%2C-1%7CListMCPers%2C%2C-1%7C; TASession=V2ID.1FC0FCEFC9A441E6BC8679486D235FA7*SQ.102*LS.DemandLoadAjax*GR.39*TCPAR.80*TBR.64*EXEX.2*ABTR.32*PHTB.50*FS.82*CPU.15*HS.recommended*ES.popularity*DS.5*SAS.popularity*FPS.oldFirst*LF.en*FA.1*DF.0*FLO.87119*TRA.false*LD.87119*VG.6999277*EAU._; TAUD=LA-1637355218885-1*RDD-1-2021_11_19*ARC-2805261*LD-58961606-2022.5.7.2022.5.8*LG-58961611-2.1.F.*HDD-58961612-2022_05_07.2022_05_08.1; roybatty=TNI1625!ADBxsQz7lmx0VO7DyC7RPZgp6yYAuAko1%2B6mDid31Qy6h%2FBn3PXyO7NNvQFZyjehyS9qfSIiY%2BPXiRcZKrRLWXWhrbLWsp443IdfbCptvkxzcF07ZBlXdVeuU40GUC3AQmGXtmmgjgroTaNh4Qiottbgu6wnRNJHsMEcyD5qBGUE%2C1; SRT=%1%enc%3AbiYu%2F2hIUs7zl2ycOVmPbg7d4blaI47mMbINEKPB2b5p%2BMFisVyjmG%2FqF9wjjt11yo%2BS64UqALs%3D'
  })
    return response.json()




# Third, iterate through each hotel URL and fetch all the reviews to generate our database
# 

# In[72]:


data = []
for hotel_url in links:
    response = request_graphql(hotel_url)[1]['data']['locations'][0]
    hotel_name = response['name']
    print(f'Scraping {hotel_name}')

    # Get total review count
    total_reviews = response['reviewListPage']['totalCount']
    # Get number of pages to get all the reviews
    pages = math.ceil(total_reviews // 20 +1)


    # Iterate through every possible page to get all the reviews
    for i in range(pages):
        # Sleep random seconds to avoid blocking
        time.sleep(random.randint(1, 3))
        # Get the GraphQL response for each page
        response = request_graphql(hotel_url, page=i)[1]['data']['locations'][0]
        # Get the reviews from each response
        reviews = response['reviewListPage']['reviews'] if response['reviewListPage'] is not None else []

        # Add each review to the array
        for review in reviews:
            review_title = review['title']
            review_description = review['text']
            location = review['location']['parent']['additionalNames']['normal']
            review_data = {
            'Hotel Name': hotel_name,
            'Review Date': review['createdDate'],
            'Stay Date': review['tripInfo']['stayDate'] if review['tripInfo'] is not None else None,
            'Location': location,
            'Lang': review['language'],
            'Room Tip': review['roomTip'] if 'roomTip' in review else None,
            'Review Title': review_title,
            'Review Stars': review['rating'],
            'Review': review_description,
            'User Name': review['userProfile']['displayName'] if review['userProfile'] else None,
            'Hometown': review['userProfile']['hometown']['location']['additionalNames']['long'] if review['userProfile'] is not None and review['userProfile']['hometown']['location'] is not None else None
              }

          # Iterate through additionalRatings (Cleanliness, Room Service...)
            for rating in review['additionalRatings']:
                review_data[f'{rating["ratingLabel"]} Stars'] = rating['rating']
            
            data.append(review_data)

    print(f'Reviews: {len(data)}')


# In[73]:


data


# In[74]:


import pandas as pd

df = pd.DataFrame(data)

df.head()


# In[75]:


df.to_csv('./waikiki_hotels_reviews.csv', index=False, encoding='utf-8-sig', sep=';')


# In[76]:


len(df)


# In[88]:


#The parsing was blocked at links[21]
links[21:][:5]


# In[80]:


#Restart parsing from links[21]
data = []
for hotel_url in links[21:]:
    response = request_graphql(hotel_url)[1]['data']['locations'][0]
    hotel_name = response['name']
    print(f'Scraping {hotel_name}')

    # Get total review count
    total_reviews = response['reviewListPage']['totalCount']
    # Get number of pages to get all the reviews
    pages = math.ceil(total_reviews // 20 +1)


    # Iterate through every possible page to get all the reviews
    for i in range(pages):
        # Sleep random seconds to avoid blocking
        time.sleep(random.randint(1, 3))
        # Get the GraphQL response for each page
        response = request_graphql(hotel_url, page=i)[1]['data']['locations'][0]
        # Get the reviews from each response
        reviews = response['reviewListPage']['reviews'] if response['reviewListPage'] is not None else []

        # Add each review to the array
        for review in reviews:
            review_title = review['title']
            review_description = review['text']
            location = review['location']['parent']['additionalNames']['normal']
            review_data = {
            'Hotel Name': hotel_name,
            'Review Date': review['createdDate'],
            'Stay Date': review['tripInfo']['stayDate'] if review['tripInfo'] is not None else None,
            'Location': location,
            'Lang': review['language'],
            'Room Tip': review['roomTip'] if 'roomTip' in review else None,
            'Review Title': review_title,
            'Review Stars': review['rating'],
            'Review': review_description,
            'User Name': review['userProfile']['displayName'] if review['userProfile'] else None,
            'Hometown': review['userProfile']['hometown']['location']['additionalNames']['long'] if review['userProfile'] is not None and review['userProfile']['hometown']['location'] is not None else None
              }

          # Iterate through additionalRatings (Cleanliness, Room Service...)
            for rating in review['additionalRatings']:
                review_data[f'{rating["ratingLabel"]} Stars'] = rating['rating']
            
            data.append(review_data)

    print(f'Reviews: {len(data)}')


# In[81]:


df2 = pd.DataFrame(data)

df2.head()


# In[82]:


df2.to_csv('./waikiki_hotels_reviews_part2.csv', index=False, encoding='utf-8-sig', sep=';')


# In[83]:


len(df2)


# # Generate a pandas DataFrame and store the results in CSV format

# In[85]:


df3=pd.concat([df,df2]).drop_duplicates().reset_index(drop=True)


# In[86]:


len(df3)


# In[87]:


df3.to_csv('./waikiki_hotels_reviews_all.csv', index=False, encoding='utf-8-sig', sep=';')


# # Database is ready

# In[9]:


import pandas as pd
data=pd.read_csv('./waikiki_hotels_reviews_all.csv', sep=';',header=None)


# In[8]:


data

