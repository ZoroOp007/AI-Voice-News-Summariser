<h1>A fullstack AI based News Summarizer.</h1>

<img src="https://github.com/ZoroOp007/AI-Voice-News-Summariser/blob/main/frontend/data/F_427257591_ZVlbJrYL0wZdSahm9kCX1zxYGtjwMSsl.jpg" placeholder="frontend Image"/>

<h3>How it works ??</h3>

<ol>

  <li> User enters topics he is interested in and source where he want news from ( Reddit ,Google News or Both )</li>
  <li> Agent scrape data using bright data from Google News and Reddit.</li>
  <li> First html response is parsed in simple text using beautifulsoup.</li>
  <li> Then this response is again sent a LLM to summarizer in such a way that essence of the news remains same.</li>
  <li> Then the textual response is convered into audio format using gtts and Elevenlabs.</li>
</ol>


<h3> Technology Used </h3>

<ul>

  <li>Backend :: FastAPI</li>
  <li>Frontend :: Streamlit</li>
  <li>AI Framework :: Langchain , Langgraph</li>
  <li>LLM platform :: Groq API </li>
</ul>



