﻿"""
examples that illustrate how to query articles using different search options
"""
from eventregistry import *

er = EventRegistry(allowUseOfArchive=False)
# er = EventRegistry()


# search for the phrase "Barack Obama" - both words have to appear together
q = QueryArticles(keywords = "Barack Obama")
res = er.execQuery(q)

# search for articles that mention both of the two words - maybe together, maybe apart
# this form of specifying multiple keywords, concepts, etc is now depricated. When you have a list,
# use it with QueryItems.AND() or QueryItems.OR() to explicitly specify how the query should be processed
q = QueryArticles(keywords = ["Barack", "Obama"])
# set some custom information that should be returned as a result of the query
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
res = er.execQuery(q)


# search for articles that mention both of the two words - maybe together, maybe apart
# the correct way of specifying multiple keywords - using QueryItems.AND or .OR classes
q = QueryArticles(keywords = QueryItems.AND(["Barack", "Obama"]))
# set some custom information that should be returned as a result of the query
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
res = er.execQuery(q)


# search for articles that mention the phrase "Barack Obama" or Trump
q = QueryArticles(keywords = QueryItems.OR(["Barack Obama", "Trump"]))
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo=ArticleInfoFlags(duplicateList=True, concepts=True, categories=True, location=True, image=True),
        conceptInfo=ConceptInfoFlags(trendingScore=True))))
res = er.execQuery(q)


# if you already have some articles that you have received from Event Registry
# for which you would like to obtain some potentially updated metadata (shared counts, event uri)
# you can use the query shown below. When making such a query you can specify up to 100 article uris in a call.
q = QueryArticles.initWithArticleUriList(["934903913", "934902493", "934902499", "934902488", "934899375", "934900984", "934890360", "934888250"])
res = er.execQuery(q)


# search for articles that:
# * mentions the concept Samsung
# * mention the phrase "iphone" in the article title
# * by BBC or by any news source located in Germany
# * in English or German language
# * return results sorted by relevance to the query (instead of "date" which is default)
q = QueryArticles(
    conceptUri = er.getConceptUri("Samsung"),
    keywords = "iphone",
    keywordsLoc="title",
    lang = ["eng", "deu"],
    sourceUri=er.getSourceUri("bbc"),
    sourceLocationUri=er.getLocationUri("Germany"))
q.setRequestedResult(RequestArticlesInfo(sortBy="rel"))
res = er.execQuery(q)

# find articles that:
# * are related to business (categorized into business category)
# * were published between 1st and 20th August 2018
# * don't mention Trump in the article title
# * are not a duplicate (copy) of another article
# * are from a news source that is among top 20 percentile of sources
# * return results sorted from most shared on social media to least
q = QueryArticles(
    categoryUri=er.getCategoryUri("business"),
    dateStart="2018-08-01",
    dateEnd="2018-08-20",
    ignoreKeywords="Trump",
    ignoreKeywordsLoc="title",
    isDuplicateFilter="skipDuplicates",
    startSourceRankPercentile = 0,
    endSourceRankPercentile = 20)
q.setRequestedResult(RequestArticlesInfo(sortBy="socialScore"))
res = er.execQuery(q)

#
# USE OF ITERATOR
# example of using the QueryArticlesIter to easily iterate through all results matching the search
#

# Search for articles mentioning George Clooney that were reported from sources from Spain or sources from Los Angeles
# iterator class simplifies retrieving and listing the list of matching articles
# by specifying maxItems we say that we want to retrieve maximum 500 articles (without specifying the parameter we would iterate through all results)
# the results will be sorted from those that are from highest ranked news sources down
q = QueryArticlesIter(
    conceptUri = er.getConceptUri("George Clooney"),
    sourceLocationUri = QueryItems.OR([er.getLocationUri("Spain"), er.getLocationUri("Los Angeles")]))
for art in q.execQuery(er, sortBy="sourceAlexaGlobalRank",
        returnInfo = ReturnInfo(
            articleInfo=ArticleInfoFlags(concepts=True, categories=True, location=True, image=True)),
        maxItems = 500):
    print(art["uri"])


# query articles using the QueryArticles class
# old way of iterating through the pages of results - requesting results page by page
q = QueryArticles(conceptUri = er.getConceptUri("George Clooney"))
page = 1
while True:
    q.setRequestedResult(RequestArticlesInfo(page = page))
    res = er.execQuery(q)
    for article in res["articles"]["results"]:
        print(article["uri"])
    if page >= res["articles"]["pages"]:
        break
    page += 1


# articles published between 2016-03-22 and 2016-03-23
# mentioning Brussels
# published by New York Times
q = QueryArticles(
    dateStart = datetime.date(2016, 3, 22), dateEnd = datetime.date(2016, 3, 23),
    conceptUri = er.getConceptUri("Brussels"),
    sourceUri = er.getNewsSourceUri("New York Times"))

# return details about the articles, including the concepts, categories, location and image
q.setRequestedResult(RequestArticlesInfo(count = 30,
    returnInfo = ReturnInfo(
        articleInfo = ArticleInfoFlags(duplicateList = True, concepts = True, categories = True, location = True, image = True))))
# execute the query
res = er.execQuery(q)

#
# OTHER AGGREGATES (INSTEAD OF OBTAINING ARTICLES)
#

# return top concept mentioned in the articles about Apple
q = QueryArticles(conceptUri=er.getConceptUri("apple"))
q.setRequestedResult(RequestArticlesConceptAggr())

# return the top categories in the articles about Tesla
q = QueryArticles(conceptUri=er.getConceptUri("Tesla"))
q.setRequestedResult(RequestArticlesCategoryAggr())

# obtain the top news sources that report about iphones
q = QueryArticles(keywords="iphone")
q.setRequestedResult(RequestArticlesSourceAggr())

# obtain the top keywords that summarize articles about Trump
q = QueryArticles(keywords="Trump")
q.setRequestedResult(RequestArticlesKeywordAggr())


#
# RECENT ACTIVITY
# example of querying most recently added content related to a particular thing
#

# get latest articles about Obama
q = QueryArticles(conceptUri = er.getConceptUri("Obama"))
q.setRequestedResult(RequestArticlesRecentActivity())     # get most recently added articles related to obama
res = er.execQuery(q)

# assume some time has passed
# time.sleep(60)

# updated the requested result type to return only information that was published after the time that was returned in the last API call
q.setRequestedResult(RequestArticlesRecentActivity(updatesAfterTm = res.get("recentActivity", {}).get("newestUpdate", None)))
# get only the matching articles that were added since the last call
res = er.execQuery(q)


#
# COMPLEX QUERIES
# examples of complex queries that combine various OR and AND operators
# as well as nested sub-queries
#

# prepare some variables used in the queries
trumpUri = er.getConceptUri("Trump")
obamaUri = er.getConceptUri("Obama")
politicsUri = er.getCategoryUri("politics")
merkelUri = er.getConceptUri("merkel")
businessUri = er.getCategoryUri("business")


# find articles that (1) were published on 2017-04-22 and (2) are either about Obama or mention keyword Trump and (3) are related to business
cq1 = ComplexArticleQuery(
    CombinedQuery.AND([
        BaseQuery(dateStart = "2017-04-22", dateEnd = "2017-04-22"),
        CombinedQuery.OR([
            BaseQuery(conceptUri = QueryItems.OR([obamaUri])),
            BaseQuery(keyword = "Trump")
        ]),
        BaseQuery(categoryUri = businessUri)
    ])
)
q = QueryArticles.initWithComplexQuery(cq1)
res = er.execQuery(q)


# find articles that are both about Obama and Trump and are not in English or German language
cq2 = ComplexArticleQuery(
    BaseQuery(
        conceptUri = QueryItems.AND([obamaUri, trumpUri]),
        exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"])))
    )
q = QueryArticles.initWithComplexQuery(cq2)
res = er.execQuery(q)


# get articles that were published on 2017-02-05 or are about trump or are about politics or are about Merkel and business
# # and are not published on 2017-02-05 or are about Obama
qStr = """
{
    "$query": {
        "$or": [
            { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
            { "conceptUri": "%s" },
            { "categoryUri": "%s" },
            {
                "$and": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ]
            }
        ],
        "$not": {
            "$or": [
                { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                { "conceptUri": "%s" }
            ]
        }
    }
}
    """ % (trumpUri, politicsUri, merkelUri, businessUri, obamaUri)
q1 = QueryArticles.initWithComplexQuery(qStr)
res = er.execQuery(q1)
