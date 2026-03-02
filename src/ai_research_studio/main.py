## 
##     代码的核心流程
## poetry run ai-research-studio daily-brief
## cli.py
## run_daily_brief()  
## pipelines/daily_brief.py
## settings.py 读取配置
## collectors 拉行情 / 拉新闻
## utils 做分类
## summarizers 做摘要（LLM 或 fallback）
## outputs/markdown_writer.py 写 markdown
## reports/daily/YYYY-MM-DD_daily_brief.md
    



from ai_research_studio.cli import main


if __name__ == "__main__":
    main()