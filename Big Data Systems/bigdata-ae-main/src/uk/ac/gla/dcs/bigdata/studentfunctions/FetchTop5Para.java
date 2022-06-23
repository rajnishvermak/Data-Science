package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.List;

import uk.ac.gla.dcs.bigdata.providedstructures.ContentItem;
import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;

public class FetchTop5Para {

	public static List<NewsArticle> fetchTop5Para(List<NewsArticle> newsArticle) {

		List<ContentItem> updatedContents = new ArrayList<ContentItem>();
		for (int i = 0; i < newsArticle.size(); i++) { 
			List<ContentItem> contents = newsArticle.get(i).getContents();
					updatedContents = fetchContent(contents);
					newsArticle.get(i).setContents(updatedContents);
			
		}
		return newsArticle;

	}

	 static List<ContentItem> fetchContent(List<ContentItem> contents) {
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
