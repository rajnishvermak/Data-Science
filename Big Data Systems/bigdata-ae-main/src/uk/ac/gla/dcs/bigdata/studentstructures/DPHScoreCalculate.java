package uk.ac.gla.dcs.bigdata.studentstructures;

import java.util.Map;

import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedstructures.Query;

public class DPHScoreCalculate{

	Query query;
	Map<NewsArticle,Double> articlemapList;
	public Query getQuery() {
		return query;
	}
	public void setQuery(Query query) {
		this.query = query;
	}
	
	public Map<NewsArticle, Double> getArticlemapList() {
		return articlemapList;
	}
	public void setArticlemapList(Map<NewsArticle, Double> articlemapList) {
		this.articlemapList = articlemapList;
	}
	
}
