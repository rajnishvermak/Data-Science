package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.spark.api.java.function.FlatMapFunction;
import org.apache.spark.util.LongAccumulator;

import uk.ac.gla.dcs.bigdata.providedstructures.ContentItem;
import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedstructures.Query;
import uk.ac.gla.dcs.bigdata.providedutilities.TextPreProcessor;

/**
 * This is an example of a FlatMapFunction, which in this case acts as a filter for
 * Steam games based on what platforms they support. The constructor of the class
 * (initially created on the driver program) stores what the filter options are, then
 * when flatmap is called for each game, the call method will either return an iterator
 * with the game if it matches the specified platforms, or an empty iterator if not.
 * @author Richard
 *
 */
public class ArticleFilterMap implements FlatMapFunction<NewsArticle,NewsArticle>{

	private static final long serialVersionUID = -5421918143346003481L;

	Query query;

	public ArticleFilterMap(Query query) {
		this.query = query;
	}


	@Override
	public Iterator<NewsArticle> call(NewsArticle article) throws Exception {
		int counter = 0;
		List<NewsArticle> finList = new ArrayList<NewsArticle>();
		List<ContentItem> contentItem = article.getContents();
		for(String term: query.getQueryTerms()) {
			if (article.getTitle() != null && article.getTitle().toLowerCase().equals(term.toLowerCase())) {
				counter++;
				finList.add(article);
				//totalTermFrequencyAccumulator.add(1);
			}
			
				for (ContentItem ci : contentItem) {
					TextPreProcessor processor = new TextPreProcessor();
					List<String> tokens = processor.process(ci.getContent());
					for(String s : tokens) {
						if (s != null && s.toLowerCase().equals(term.toLowerCase())) {
							finList.add(article);
							//totalTermFrequencyAccumulator.add(1);
						}
					}
				}
				
		}
		

		return finList.iterator();

	}
	
	

}
