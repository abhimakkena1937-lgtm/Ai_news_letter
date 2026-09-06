from typing import TypedDict,List,Annotated
import operator
from schemas import(
    NewsItem,
    StartUpItem,
    PaperItem,
    TweetItem,
    GitHubItem,
    RankedContext,
    DiscoveredEntity
)


class NewsLetterState(TypedDict,total=False):
    date:str
    time_window:str
    discovered_entities:Annotated[List[DiscoveredEntity],operator.add]
    news:Annotated[List[NewsItem],operator.add]
    startups:Annotated[List[StartUpItem],operator.add]
    tweets:Annotated[List[TweetItem],operator.add]
    github_repos: Annotated[List[GitHubItem], operator.add]
    research_papers:Annotated[List[PaperItem],operator.add]
    progress:Annotated[List[str],operator.add]
    errors:Annotated[List[str],operator.add]
    ranked_context:RankedContext
    newsletter_markdown:str
    newsletter_html:str

