package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.spark.api.java.function.FlatMapFunction;

import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedstructures.Query;
import uk.ac.gla.dcs.bigdata.providedutilities.DPHScorer;
import uk.ac.gla.dcs.bigdata.studentstructures.DPHScoreCalculate;
import uk.ac.gla.dcs.bigdata.studentstructures.DphParamters;

/**
 * This is an example of a FlatMapFunction, which in this case acts as a filter for
 * Steam games based on what platforms they support. The constructor of the class
 * (initially created on the driver program) stores what the filter options are, then
 * when flatmap is called for each game, the call method will either return an iterator
 * with the game if it matches the specified platforms, or an empty iterator if not.
 * @author Richard
 *
 */
public class QueryFilterFlatMapper implements FlatMapFunction<Query,DPHScoreCalculate>{

	private static final long serialVersionUID = -5421918143346003481L;

	List<NewsArticle> newsArticlesList;
	List<DphParamters> paramList;
	
	public QueryFilterFlatMapper(List<NewsArticle> newsArticlesList, List<DphParamters> paramList) {
		this.paramList = paramList;
		this.newsArticlesList = newsArticlesList;
	}
	



	@Override
	public Iterator<DPHScoreCalculate> call(Query query) throws Exception {
		
		List<DPHScoreCalculate> scoreList = new ArrayList<DPHScoreCalculate>();
		long totalDocsInCorpus = newsArticlesList.size();
		Map<NewsArticle,Double> articleMap = new HashMap<NewsArticle, Double>();
		List<Map<NewsArticle,Double>> list = new ArrayList<Map<NewsArticle,Double>>();
		DPHScoreCalculate dph = new DPHScoreCalculate();
		for(NewsArticle article: newsArticlesList) {
			double averageQueryDphScore = 0L;
			for(String term: query.getQueryTerms()) {
				dph.setQuery(query);
				
				short termFrequency;
				int totalTermFrequency = 0;
				double  averageLength = (paramList.get(0).getLengthOfAllDocs())/totalDocsInCorpus;
				if(!article.getMap().isEmpty()) {
					for ( Map.Entry<String, Integer> entry : article.getMap().entrySet()) {
						
						String word = entry.getKey();
						Integer freq = entry.getValue();
						
						if(word.toLowerCase().equals(term.toLowerCase())) {
							termFrequency = freq.shortValue();
							for(DphParamters param: paramList) {
								if(param.getTermCountInAllDocs().get(word) != null)
								totalTermFrequency = param.getTermCountInAllDocs().get(word);
							}
							//termFrequency = freq.shortValue();
							double score = DPHScorer.getDPHScore(termFrequency, totalTermFrequency, article.getCurrentDocLength(), averageLength, totalDocsInCorpus);
							dph.setQuery(query);
							if(score == Double.POSITIVE_INFINITY || score == Double.NEGATIVE_INFINITY)
								score = 0L;
						averageQueryDphScore += score;
						}
					}
				}
			}
			
			averageQueryDphScore = averageQueryDphScore/query.getQueryTerms().size();
			articleMap.put(article, averageQueryDphScore);
			dph.setArticlemapList(articleMap);
			list.add(articleMap);
			
		}
		scoreList.add(dph);
		
		return scoreList.iterator();
	}
		

}
