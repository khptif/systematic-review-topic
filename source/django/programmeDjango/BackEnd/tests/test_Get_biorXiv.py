from django.test import TestCase
from BackEnd.functions.Get_biorXiv import *

class test_get_search_term(TestCase):

    def test_method(self):
        input = "virus,hiv,(africa;new-york)"
        output_expected = "virus+AND+hiv+AND+(+africa+OR+new-york+)+"
        output_result = get_search_term(input)
        print(output_result + " ?= " + output_expected)
        self.assertEqual(output_expected,output_result)


class test_get_max_article(TestCase):
    
    def test_method(self):
        input="virus"
        output_expected = 31,586
        output_result = get_max_article(input)
        self.assertLessEqual(output_expected,output_result)


class test_extract_id(TestCase):

    def test_method(self):
        """ we check if the method runs well, if there is a problem
            we check if the list of id is not null and the entry too"""
        search_term = '"Vitamine+C"'
        list_id, entry = extract_id(search_term)

        self.assertTrue(len(list_id)>0 and len(entry)>0)
    
class test_extract_article(TestCase):

    def test_method(self):
        """ we check if the method runs well.
            we recuperate input data in the website.
            After, we check if the article is in database and data match"""

        # the input and expected_data
        entry = """ <div class="highwire-article-citation highwire-citation-type-highwire-article node--2" data-pisa="biorxiv;2021.11.04.467278v1" data-pisa-master="biorxiv;2021.11.04.467278" data-seqnum="1" data-apath="/biorxiv/early/2021/11/04/2021.11.04.467278.atom" id="biorxivearly2021110420211104467278atom20304233"><div  class="highwire-cite highwire-cite-highwire-article highwire-citation-biorxiv-article-pap-list clearfix" >

                    <span class="highwire-cite-title" >
                    <a href="/content/10.1101/2021.11.04.467278v1" class="highwire-cite-linked-title" data-icon-position="" data-hide-link-title="0"><span class="highwire-cite-title">Effect of vitamin C and E supplementation on human gastrointestinal tract tissues and cells: Raman spectroscopy and imaging studies</span></a>    </span>
  
                    <div  class="highwire-cite-authors" ><span  class="highwire-citation-authors"><span class="highwire-citation-author first" data-delta="0"><span class="nlm-given-names">Krystian</span> <span class="nlm-surname">Miazek</span></span>, <span class="highwire-citation-author" data-delta="1"><span class="nlm-given-names">Karolina</span> <span class="nlm-surname">Beton</span></span>, <span class="highwire-citation-author" data-delta="2"><span class="nlm-given-names">Beata</span> <span class="nlm-surname">Brozek-Pluska</span></span></span></div>
  
                    <div  class="highwire-cite-metadata" ><span  class="highwire-cite-metadata-journal highwire-cite-metadata">bioRxiv </span><span  class="highwire-cite-metadata-pages highwire-cite-metadata">2021.11.04.467278; </span><span  class="highwire-cite-metadata-doi highwire-cite-metadata"><span class="doi_label">doi:</span> https://doi.org/10.1101/2021.11.04.467278 </span></div>
  
  
                    <div  class="highwire-cite-extras" ><div id = "hw-make-citation-1" class = "hw-make-citation" data-encoded-apath=";biorxiv;early;2021;11;04;2021.11.04.467278.atom" data-seqnum="1"><a href="/highwire-save-citation/saveapath/%3Bbiorxiv%3Bearly%3B2021%3B11%3B04%3B2021.11.04.467278.atom/nojs/1" id="link-save-citation-toggle-1" class="link-save-citation-save use-ajax hw-link-save-unsave-catation link-icon" title="Save"><span class="icon-plus"></span> <span class="title">Add to Selected Citations</span></a></div></div>
                    </div>
                    </div>"""
        id = "biorxiv;2021.11.04.467278v1"
        dict_entry = {id:entry}
        title_expected="Effect of vitamin C and E supplementation on human gastrointestinal tract tissues and cells: Raman spectroscopy and imaging studies"
        doi_expected = "10.1101/2021.11.04.467278"

        # we start the method
        research_mock = Research.objects.create(search="",year_begin=datetime.date(1902,1,1),year_end=datetime.date(1904,1,1))
        extract_article([id],dict_entry,research_mock)

        #we retrieve the articles from database
        article = Article.objects.filter(research_article__research = research_mock)

        #we check if the article exists
        self.assertTrue(article.exists())

        #we check if there is one article
        self.assertEqual(1,article.count())

        #we check if the title match
        self.assertEqual(title_expected,article[0].title)

        #we check if the doi match
        self.assertEqual(doi_expected,article[0].doi)
        