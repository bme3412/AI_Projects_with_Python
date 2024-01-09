from crewai import Task
from textwrap import dedent

class StockAnalysisTasks():
    def research(self, agent, company):
        return Task(description=dedent(f"""
        Collect and summarize recent news articles, press
        releases, and market analyses related to the stock and
        its industry.
        Pay special attnetion to any significant events, market
        sentiments, and analyst opinions. Also include upcoming
        events like earnings and others.
        
        Your final answer MUST be a report that includes a
        comprehensive summary of the latest news, any notble
        shifts in market sentiment, and potential impacts on
        the stock.
        Also make sure to return the stock ticker.
        
        {self.__tip_selection()}
        
        Make sure to use the most recent data as possible.

        Selected company: {company}
        """),agent=agent)
    
    def financial_analysis(self, agent):
        return Task(description=dedent(f"""
            Conduct a thorough analysis of the stock's financialhealth and market performance. 
            This includes examining key financial metrics such as
            P/E ratio, EPS growth, revenue trends, and 
            debt-to-equity ratio. 
            Also, analyze the stock's performance in comparison 
            to its industry peers and overall market trends.

            Your final report MUST expand on the summary provided
            but now including a clear assessment of the stock's
            financial standing, its strengths and weaknesses, 
            and how it fares against its competitors in the current
            market scenario.{self.__tip_section()}

            Make sure to use the most recent data possible. """), agent=agent)
    
    def filings_analysis(self, agent):
        return Task(description=dedent(f"""
            Analyze the latest 10-Q and 10-K filings from EDGAR for
            the stock in question. 
            Focus on key sections like Management's Discussion and
            Analysis, financial statements, insider trading activity, 
            and any disclosed risks.
            Extract relevant data and insights that could influence
            the stock's future performance.

            Your final answer must be an expanded report that now
            also highlights significant findings from these filings,
            including any red flags or positive indicators for
            your customer.
        {self.__tip_section()}        
          """),agent=agent)
    
    def __tip_section(self):
        return "If you do your BEST WORK, I'll give you a $10,000 commission!"