# PDF -> evidence -> PDF
This repository contains a Python script, and its utilities, to 
1) Process an anonymized personal statement, in pdf format.
2) Collect evidence across the internet.
3) For each personal statement, your python script should output well formatted pdf documents listing all supporting evidence and arguments for eligibility criterion #1 listed above.

## Detailed Plan

```
project/
├── src/
│   ├── pipeline_steps/
│   │   ├── step1_pdf_processor.py      # PDF reading and writing
│   │   ├── step2_extract_claims.py     # NLP and claim extraction
│   │   ├── step3_evidence_gather.py    # Evidence gathering (Recall-like, get everything relevant)
│   │   ├── step4_evidence_validator.py # Validation and ranking (Precision-like, keep only the strongest evidence)
│   │   └── step5_report_generator.py   # Output PDF creation
│   └── main.py                         # Script orchestration
├── output/                             # Output directory for processed statements
├── tests/
├── requirements.txt
└── README.md
```

### Next Up (TODOs)
* Better Step 2 claim extraction (try with Anthropic/ChatGPT)

### Assumptions and Design Decisions
P0 - It Works
* Modules for each step in the pipeline - expect pipeline to be linear, one-directional.
* Save intermediate state (JSON) between modules, allowing recovery and intermediate validation between steps. (save each personal statement & state to its own folder; gives staleness)
* Text Matching does not work, call LLM APIs instead to ID claims.
* Trustworthy sources for citations.
    * Claims relating to "endeavor has national interest" benefit from web search.
    * Claims related to background/previous experience, leave placeholder for applicant to fill in with evidence. This is real business flow.
* Here are a few tips for where evidence of national importance can be sourced from:
    1.	Media articles and reports from reputable outlets that highlight the broader impact of your work or its alignment with national interests
    2.	Evidence showing your work aligns with U.S. government priorities, such as federal climate action initiatives or energy independence goals - Executive orders or government press releases
    3.	Documentation demonstrating your work's potential to employ U.S. workers or have significant economic impact, particularly in economically depressed areas
    4.	Evidence of your work's potential to produce significant economic impact or other substantial positive economic effects
    5.	Documentation showing your endeavor has national or global implications within a particular field, such as improved manufacturing processes or medical advances
    6.	Evidence of media coverage in national or reputable regional outlets, indicating broader interest in your work
    7.	Comparative analysis demonstrating how your work stands out in your field, emphasizing its unique national importance
    8.	Documentation showing the scalability of your work, indicating its potential for broader impact beyond its current scope


P1 - QoL
* Each module will implement input validation and clear error messaging
* Failed processing attempts will be logged with detailed context
* System will gracefully handle network issues during web scraping
* Each piece of evidence will be tagged with source, timestamp, and relevance score

P2 - Efficiency
* Batch processing 


### Setup
* Use requirements.txt to create an environment; spaCy package requres special install per their website: https://pypi.org/project/spacy/


# IO References

## Criteria #1
The following is from https://www.uscis.gov/working-in-the-united-states/permanent-workers/employment-based-immigration-second-preference-eb-2

B. Eligibility for National Interest Waiver

Prong 1: Evidence That Your Endeavor Has Substantial Merit and National Importance

    Provide a detailed description explaining your proposed endeavor and supporting documentary evidence to establish that the endeavor is of national importance.
        The term "endeavor" is more specific than the general occupation; you should offer details not only as to what the occupation normally involves, but what types of work you propose to undertake specifically within that occupation.
        When explaining the endeavor, you should do so in a straightforward manner, and clearly lay out the potential direct impacts of the endeavor and whether the endeavor will be furthered through the course of your duties at a particular employer or some other way.

Note that benefits to a specific employer alone, even an employer with a national footprint, are not sufficiently relevant to the question of whether your endeavor has national importance. At issue is whether you can demonstrate that your own individual endeavor stands to have broader implications, such as for a field, a region, or the public at large.

Examples from the Policy Manual:

    * While engineer is an occupation, the explanation of the proposed endeavor should describe the specific projects and goals, and the area of engineering in which the person will work, rather than simply listing the duties and responsibilities of an engineer.
        * A proposed endeavor to engage in classroom teaching, without broader implications for a field or region, generally does not rise to the level of having national importance for the purpose of establishing eligibility for a national interest waiver. Citing the general importance of the profession of classroom teaching would not alone be sufficient to demonstrate national importance in the context of a national interest waiver request.
        Proposing to work in an occupation with a national shortage or serve in a consulting capacity for others seeking to work in an occupation with a national shortage alone, is also insufficient.
        * A person developing a drug for a pharmaceutical company may establish national importance by demonstrating the prospective public health benefits of the drug, instead of solely projecting the profits that will accrue to the employer.
        * A person developing a particular technology for use or sale by a given company may not be able to establish national importance based on evidence that this technology will have benefits for the company or its clients alone. To establish broader public or commercial implications at a level consistent with national importance for this field or industry, the petitioner could demonstrate, through the submission of relevant evidence, widespread interest in adoption or licensing of the technology, a novel and important manufacturing or operational process, or how the technology stands to impact the development of similar technology by other companies.
        * A software engineer adapting their employer's code for various clients will have difficulty demonstrating the national importance of that endeavor, absent additional broader impacts supported by specific evidence.
        * An entrepreneur cannot demonstrate national importance solely by opening a consulting firm for those working or seeking to work in a nationally important occupation. Similarly, statements and evidence regarding the importance of the relevant industry overall, such as the car dealership industry, will not demonstrate that a person seeking to start a car dealership satisfies the national importance prong.

## Sample desired output

Section.2 Dr. name's proposed endeavor has both substantial merit and national
importance for the United States
Dr. name's proposed endeavor is to develop state-of-the-art Artificial Intelligence algorithms for
automatic and intelligent decision making. Among other applications, Dr. name's work is relevant to
the improvement of various technologies, including but not limited to autonomous driving vehicles,
automatical diseases diagnosis, which is of substantial merit and great importance to the United
States.
2.1 Artificial Intelligence is an area of substantial merit
Dr. name is an expert in the field of Artificial Intelligence, especially in the subfield of Computer
Vision. AI eliminates friction and improves analytics and resource utilization across your organiza-
tion, resulting in significant cost reductions. It can also automate complex processes and minimize
downtime by predicting maintenance needs. Artificial Intelligence and Computer Vision have broad
applications such as automatical disease diagnosis from medical images, Autonomous Vehicles from
cameras et. al.
The Artificial Intelligence market size was valued at USD 454.12 billion in 2022 and is expected to
hit around USD 2,575.16 billion by 2032, progressing with a compound annual growth rate (CAGR)
of 19% from 2023 to 2032. The North America artificial intelligence market was valued at USD
167.30 billion in 2022. (Exhibit 16 : a report from the national qualification register.)
The importance of AI has also been recognized by the US goverment:
"AI advances are also providing great benefits to our social wellbeing in areas such as
precision medicine, environmental sustainability, education, and public welfare." (United
States Department of State https://www.state.gov/artificial-intelligence/)
In summary, Artificial Intelligence is an important technology and has broad impact in many in-
dustries. It is of substantial metri to the United States.
2.2 Dr. name's work will be beneficial to the United States
Dr. name's proposed endeavor also will benefit the United States. For example, the Topic B and
Topic A methods he invented can be used as secure identification methods that add an additional
7 of 36
batchfy.com/eb1a
EB-2 Immigrant Petition for Permanent Residency with National Interest Waiver
layer of security to payment systems. In December 2022, the Nilson Report, which monitors the
payments industry, released a forecast indicating that U.S. losses from card fraud will total $165.1
billion over the next 10 years. Adding additional advanced identification technologies like Topic A
and Topic B would prevent many of the losses.
Furthermore, Dr. name's current research at University of A is essential to improving the health-
care. He is developing AI algorithms to automatically diagnose and localize early-stage prostate
cancers from magnetic resonance images (MRI). Prostate cancer is the most common solid organ
malignant tumor and the second leading cause of cancer-related death in men in the United States.
Diagnosing tumors at the very early stage is the key to increasing the chances of successful treat-
ment and improving patient outcomes. However, early-stage tumors are very hard to identify and
depends heavily on the experience of radiologist. Unfortunately, not every patient has the access
to an experienced radiologist. Artificial Intelligence and Computer Vision technologies can greatly
improve the chance of detecting tumors at the early stage and save patients' lives, and also improve
health care equality. In summary, Dr. name's proposed endeavor is of great importance to the
United States. Fellow experts in the field have provided further detail on the importance of this
endeavor:
• "One of his major accomplishments is an AI-based approach for prostate cancer diagnosis
with dynamic contrast-enhanced magnetic resonance images (DCE-MRI). The newly proposed
approach significantly improves the accuracy and efficiency of processing compared to existing
methods." (Exhibit 1 , support letter from Professor, Firstname Lastname, University of XX,
USA)
• "His research outcome has both practical application and academic reputation. His research
on Topic A resulted in a conference paper published in the European Conference on Computer
Vision, and it was covered by MIT Technology Review." (Exhibit 2 , support letter from
Professor X, X University, United Kingdom
