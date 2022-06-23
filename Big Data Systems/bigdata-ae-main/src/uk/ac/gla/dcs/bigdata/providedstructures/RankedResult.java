package uk.ac.gla.dcs.bigdata.providedstructures;

import java.io.Serializable;
import java.util.Objects;

public class RankedResult implements Serializable, Comparable<RankedResult> {

	private static final long serialVersionUID = -2905684103776472843L;
	
	String docid;
	NewsArticle article;
	double score;
	
	public RankedResult() {}
	
	public RankedResult(String docid, NewsArticle article, double score) {
		super();
		this.docid = docid;
		this.article = article;
		this.score = score;
	}

	public String getDocid() {
		return docid;
	}

	public void setDocid(String docid) {
		this.docid = docid;
	}

	public NewsArticle getArticle() {
		return article;
	}

	public void setArticle(NewsArticle article) {
		this.article = article;
	}

	public double getScore() {
		return score;
	}

	public void setScore(double score) {
		this.score = score;
	}

	@Override
	public int compareTo(RankedResult o) {
		return new Double(score).compareTo(o.score);
	}

	@Override
	public int hashCode() {
		return Objects.hash(docid);
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		RankedResult other = (RankedResult) obj;
		return Objects.equals(docid, other.docid);
	}
	
	
	
}
