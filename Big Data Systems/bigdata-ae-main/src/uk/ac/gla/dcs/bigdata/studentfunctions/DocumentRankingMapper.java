package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.spark.api.java.function.MapFunction;

import uk.ac.gla.dcs.bigdata.providedstructures.DocumentRanking;
import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedstructures.RankedResult;
import uk.ac.gla.dcs.bigdata.providedutilities.TextDistanceCalculator;
import uk.ac.gla.dcs.bigdata.studentstructures.DPHScoreCalculate;

public class DocumentRankingMapper implements MapFunction<DPHScoreCalculate, DocumentRanking>{

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	//sort and calcuate texual distance, move them to list, get top 10
	@Override
	public DocumentRanking call(DPHScoreCalculate value) throws Exception {

		Map<NewsArticle,Double> list = value.getArticlemapList();
	
		Map<NewsArticle,Double> sortedMap = list
		        .entrySet()
		        .stream()
		        .sorted(Collections.reverseOrder(Map.Entry.comparingByValue()))
		        .collect(
		           Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue, (e1, e2) -> e2,
		                LinkedHashMap::new));

	
		DocumentRanking ranking = new DocumentRanking();
		
		List<RankedResult> resultList = new ArrayList<RankedResult>();
				main:  for (Map.Entry<NewsArticle,Double> first : sortedMap.entrySet()) {
					  for (Map.Entry<NewsArticle,Double> next : sortedMap.entrySet()) {
						  if(!first.getKey().equals(next.getKey())) {
							  RankedResult result = new RankedResult();
							  String textSnippet1 = first.getKey().getTitle();
							  String textSnippet2 = next.getKey().getTitle();
							  double simialr = 0;
								simialr = TextDistanceCalculator.similarity(textSnippet1, textSnippet2);
							
							  if(simialr<0.5) {
								  NewsArticle article = new NewsArticle();
								  if(Double.compare(first.getValue(), next.getValue())>0) {
									  	 article = first.getKey();
									  	 article.setTitle(first.getKey().getOrignalTitle());
									  	  result.setArticle(article);
										  result.setScore(first.getValue());
										  result.setDocid(first.getKey().getId());
									  }
								  else {
									  article = next.getKey();
								  	  article.setTitle(next.getKey().getOrignalTitle());
								  	  result.setArticle(article);
									  result.setScore(next.getValue());
									  result.setDocid(next.getKey().getId());
								  }
								  if(!resultList.contains(result)) {
									  if(resultList.size()<11)
										  resultList.add(result);
									  else
										  break main;
								  }
										
							  }
						  }
					    }
						  }
				  


		if(!resultList.isEmpty()) {
			ranking.setQuery(value.getQuery());
			ranking.setResults(resultList.subList(0, 10));
		}
		
		return ranking;
	}

}
