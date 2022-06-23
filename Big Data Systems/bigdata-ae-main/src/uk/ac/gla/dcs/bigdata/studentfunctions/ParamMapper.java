package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.apache.spark.api.java.function.FlatMapFunction;

import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedstructures.Query;
import uk.ac.gla.dcs.bigdata.studentstructures.DphParamters;

/**
 * This is an example of a FlatMapFunction, which in this case acts as a filter
 * for Steam games based on what platforms they support. The constructor of the
 * class (initially created on the driver program) stores what the filter
 * options are, then when flatmap is called for each game, the call method will
 * either return an iterator with the game if it matches the specified
 * platforms, or an empty iterator if not.
 * 
 * @author Richard
 *
 */
public class ParamMapper implements FlatMapFunction<Query, DphParamters> {

	private static final long serialVersionUID = -5421918143346003481L;

	List<NewsArticle> newsArticlesList;

	public ParamMapper(List<NewsArticle> newsArticlesList) {
		this.newsArticlesList = newsArticlesList;
	}

	@Override
	public Iterator<DphParamters> call(Query query) throws Exception {

		List<DphParamters> list = new ArrayList<DphParamters>();
		DphParamters params = new DphParamters();
		
		int lengthOfAllDocs = 0;
		int sum = 0;
		Map<String, Integer> map = new HashMap<String, Integer>();
		for (NewsArticle article : newsArticlesList) {
			lengthOfAllDocs += article.getCurrentDocLength();
			for (String term : query.getQueryTerms()) {
				if (!article.getMap().isEmpty()) {
					for (Map.Entry<String, Integer> entry : article.getMap().entrySet()) {

						String word = entry.getKey();
						Integer freq = entry.getValue();

						if (word.toLowerCase().equals(term.toLowerCase())) {
							sum += freq;
							map.put(word, sum);
						}
					}
				}
				

			}

			
		}
		params.setTermCountInAllDocs(map);
		list.add(params);
		list.get(0).setLengthOfAllDocs(lengthOfAllDocs);		

		return list.iterator();

	}
}
