package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.List;

import org.apache.spark.api.java.function.MapFunction;

import uk.ac.gla.dcs.bigdata.providedstructures.ContentItem;
import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedutilities.TextPreProcessor;

public class FetchMapper implements MapFunction<NewsArticle, NewsArticle> {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	@Override
	public NewsArticle call(NewsArticle value) throws Exception {
		List<ContentItem> updatedContents = new ArrayList<ContentItem>();
		NewsArticle newsArticle = new NewsArticle();
		newsArticle = value;
		//if(value.getTitle() != null && (!value.getTitle().equals(null) || !value.getTitle().equals(""))) {
			List<ContentItem> contents = value.getContents();
					updatedContents = fetchContent(contents);
					newsArticle.setContents(updatedContents);
		//}
		return newsArticle;


	}

	 private List<ContentItem> fetchContent(List<ContentItem> contents) {
			List<ContentItem> updatedContents = new ArrayList<ContentItem>();
			List<ContentItem> tempContents = new ArrayList<ContentItem>();

			for(ContentItem con: contents) {
				if(con.getSubtype()!= null && con.getSubtype().equalsIgnoreCase("PARAGRAPH")){
					tempContents.add(con);
				}
			}
					if (tempContents.size() < 5)
						return tempContents;
					for (int i = 0; i < 5; i++) { // loop over the first 5 paragraph
						updatedContents.add(tempContents.get(i));
					}
				
			
			return updatedContents;
		}
		
}
