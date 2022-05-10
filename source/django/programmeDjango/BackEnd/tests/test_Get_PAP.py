from django.test import TestCase
from BackEnd.functions.Get_PAP import *


class test_extract_meta_data(TestCase):
    # we check if the meta data are corresctly extracted.

    def test_method(self):
        # we choose an article ID and its metadata and compare it with method's result
        id = 284911490
        data_expected = {
            "title":"A Real-World Observational Study of Gla-300 in Adults with Type 2 Diabetes Who Fast During Ramadan in the South Asia Region: A Subgroup Analysis of the ORION Study",
            "date" : "2022-03-14",
            "doi" : "10.1007/s13300-022-01234-y",
            "authors" : [('Hassanein', 'Mohamed'), ('Sahay', 'Rakesh'), ('Hasan', 'Mohammad I.'), ('Hussain', 'Arshad'), ('Mittal', 'Vinod'), ('Mohammed', 'Riyaz'), ('Shaikh', 'Zaman'), ('Farishta', 'Faraz'), ('Mohanasundaram', 'Senthilnathan'), ('Naqvi', 'Mubarak')],
            "abstract" : "In this ORION study subgroup analysis, the safety and effectiveness of insulin glargine 300 U/mL (Gla-300) was evaluated in people from the South Asia region with type 2 diabetes mellitus (T2DM) before, during, and after Ramadan, in a real-world setting. The ORION study was a real-world, prospective, observational, non-comparative study conducted across 11 countries. The current subgroup analysis included participants from the South Asia region (India and Pakistan) who fasted during Ramadan. The primary endpoint was the percentage of participants experiencing \u2265 1 event of severe and/or symptomatic documented hypoglycemia with self-monitored plasma glucose (SMPG)\u2009\u2264\u200970\u00a0mg/dL during Ramadan. Secondary endpoints analyzed were changes in glycated hemoglobin (HbA1c), fasting plasma glucose (FPG), SMPG, insulin dose, and adverse events (AEs). This subgroup analysis included 106 participants from the South Asia region with mean (standard deviation) age of 51.3 (10.9) years and mean number of 29.8 (4.0) fasting days. The number of severe and/or symptomatic documented hypoglycemia events was low in the pre-Ramadan (SMPG\u2009\u2264\u200970\u00a0mg/dL: 1 event [0.9%]; SMPG\u2009<\u200954\u00a0mg/dL: 1 event [0.9%]) and Ramadan periods (SMPG\u2009\u2264\u200970\u00a0mg/dL: 1 event [0.9%]; SMPG\u2009<\u200954\u00a0mg/dL: 0 events), and none in the post-Ramadan period. One participant reported severe hypoglycemia (any time of the day: nocturnal or daytime) throughout the pre-Ramadan period. A reduction in HbA1c and FPG levels was seen during the pre- to post-Ramadan period; however, a slight increase in SMPG levels was reported during this same period. Gla-300 daily dose was reduced from 21.6 (9.6) U to 20.2 (8.9) U during the pre-Ramadan to Ramadan period. The incidence of AEs was 1.9%. The real-world data from the ORION study indicate that Gla-300 is effective, with low risk of hypoglycemia, for the management of T2DM during Ramadan in the South Asian population. CTRI/2019/02/017636.",
            "url": "https://link.springer.com/content/pdf/10.1007/s13300-022-01234-y.pdf"
        }

        data_result = extract_metadata(id)
        
        for key,value in data_expected.items():
            if key == "abstract":
                continue

            self.assertEqual(value,data_result[key],"value from " + key)

class test_get_article_parallel(TestCase):
    # We test the method to parallelise the id extraction

    # We first test the method individualy. After, we test it in sequentially and in parallel and we compare. We check the process time too.
    # input:

    pass