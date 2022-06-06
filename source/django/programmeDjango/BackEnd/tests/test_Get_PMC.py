from django.test import TestCase
from BackEnd.functions.Get_PMC import *


class test_get_max_article(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        number_article_result = get_max_article(input)
        number_article_expected = 234
        self.assertGreaterEqual(number_article_result,number_article_expected)

class test_get_ID(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        list_id = get_ID(input)
        number_id_expected = 234
        self.assertGreaterEqual(len(list_id),number_id_expected)

class test_extract_data(TestCase):

    def test_method(self):
        input = 9150376
        output_expected ={'title': 'The potential impact of nutritional intake on symptoms severity in patients with comorbid migraine and irritable bowel syndrome', 'doi': '10.1186/s12883-022-02723-0', 'date': datetime.date(2022, 5, 20), 'author': [('Magdy', 'Rehab'), ('Eid', 'Ragaey A'), ('Hassan', 'Mahmoud'), ('Abdelghaffar', 'Mohamed'), ('El Sayed', 'Asmaa F'), ('Mohammed', 'Zeinab'), ('Hussein', 'Mona')], 'abstract': 'Background Specific dietary recommendations for migraine patients with comorbid irritable bowel syndrome (IBS) are lacking. This work aimed to study the severity scores of such two common pain-related disorders in relation to various macronutrients and micronutrients intake. Methods A cross-sectional study was conducted on patients with concomitant migraine and IBS. The frequency and intensity of migraine attacks and the severity of IBS were evaluated. Data on dietary intake were collected using food frequency questionnaires and 24-hour dietary recall. Results One-hundred patients with a median age of 36 years participated. The severity scores for migraine and IBS were positively correlated with fat and copper and negatively correlated with fiber and zinc intake. Copper intake was an independent predictor of the severity of both migraine and IBS (P 0.033, < 0.001). Patients with episodic migraine (n = 69) had a significantly higher frequency of cooked, fresh vegetables, and wheat bran bread intake (P 0.009, 0.004, 0.021) and lower frequency of hydrogenated oils intake (P 0.046), in comparison to patients with chronic migraine (n = 31). Patients with moderate intensity of migraine (n = 37) had a significantly higher frequency of herbal drinks intake (P 0.014) than patients with a severe intensity of migraine (n = 63). Patients with mild (n = 13) and moderate IBS (n = 41) had a significantly higher frequency of wheat bran bread and sen bread intake (P 0.003, 0.022) than patients with severe IBS (n = 46). Conclusion Patients with comorbid migraine and IBS are advised to adhere to a diet low in fat and copper and rich in fiber and zinc. Supplementary Information The online version contains supplementary material available at 10.1186/s12883-022-02723-0. ', 'url': 'http://bmcneurol.biomedcentral.com/track/pdf/10.1186/s12883-022-02723-0.pdf'}
        output_result = extract_metadata(input)
        
        self.assertEqual(output_expected,output_result)

class test_get_article_parallel(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        research = Research.objects.create()
        max_article_expected = get_max_article(input)
        list_id = get_ID(input)
        get_article_parallel(research,list_id)

        #we check if we have atmost half of article expected

        self.assertGreater(Research_Article.objects.filter(research=research).count(),max_article_expected/2)