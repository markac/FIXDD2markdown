import markdown
from ddmarkdown import DDMarkdownExtension

markdown.markdown('::fix AE', extensions=[DDMarkdownExtension()])
