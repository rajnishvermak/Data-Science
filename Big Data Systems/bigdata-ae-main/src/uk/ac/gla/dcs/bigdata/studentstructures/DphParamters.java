package uk.ac.gla.dcs.bigdata.studentstructures;

import java.io.Serializable;
import java.util.Map;

import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;

public class DphParamters implements Serializable{

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	NewsArticle article;
	Map<String, Integer> termCountInAllDocs;
	Integer lengthOfAllDocs;
	
	public NewsArticle getArticle() {
		return article;
	}
	public void setArticle(NewsArticle article) {
		this.article = article;
	}
	public Map<String, Integer> getTermCountInAllDocs() {
		return termCountInAllDocs;
	}
	public void setTermCountInAllDocs(Map<String, Integer> termCountInAllDocs) {
		this.termCountInAllDocs = termCountInAllDocs;
	}
	public Integer getLengthOfAllDocs() {
		return lengthOfAllDocs;
	}
	public void setLengthOfAllDocs(Integer lengthOfAllDocs) {
		this.lengthOfAllDocs = lengthOfAllDocs;
	}
	
	

}
