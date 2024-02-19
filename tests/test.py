from markdown.test_tools import TestCase
from markdown_ddmarkdown import ddmarkdown

class TestDDMarkdown(TestCase):
    default_kwargs = {'extensions': ['ddmarkdown']}

    def test_fix_render(self):
        self.assertMarkdownRenders(
            self.dedent(
                """
                ::fix AE tests/data/AE.txt
                """
            ),
            self.dedent(
                """
                *FIX*: `AE`
                """
            )
        )
