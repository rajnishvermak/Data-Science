package uk.ac.gla.dcs.bigdata.studentfunctions;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.apache.spark.api.java.function.MapFunction;

import uk.ac.gla.dcs.bigdata.providedstructures.NewsArticle;
import uk.ac.gla.dcs.bigdata.providedutilities.TextPreProcessor;

public class ProcessorMapper implements MapFunction<NewsArticle, NewsArticle> {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	@Override
	public NewsArticle call(NewsArticle value) throws Exception {
		TextPreProcessor processor = new TextPreProcessor();
		List<String> finalList = new ArrayList<String>();
		value.setOrignalTitle(value.getTitle()!=null?value.getTitle():"");
		List<String> titleTokens = processor.process(value.getTitle());
		String titleList = String.join(" ", titleTokens );
		value.setTitle(titleList);
		String contentlist = "";
		List<String> finalContent = new ArrayList<String>();
		for(int j=0;j<value.getContents().size();j++) {
		List<String> contentTokens = processor.process(value.getContents().get(j).getContent());
		 contentlist = String.join(" ", contentTokens );
		 finalContent.add(contentlist);
		value.getContents().get(j).setContent(contentlist);
		}
		
		finalList.addAll(finalContent);
		finalList.add(titleList);
		 Map<String, Integer> result = finalList.parallelStream().
		            flatMap(s -> Arrays.asList(s.split(" ")).stream()).
		            collect(Collectors.toConcurrentMap(
		                w -> w.toLowerCase(), w -> 1, Integer::sum));
		
		 
		int currentDocLength =  titleList.length() + finalContent.size();
		value.setMap(result);
		value.setCurrentDocLength(currentDocLength);
	
		
		//save the list of processed contents(without stopwords).
		return value;
	}

	
}
