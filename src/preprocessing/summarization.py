import os
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from src.utils.dbconnector import append_to_document, find_documents
from src.utils.logger import setup_logger

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


# Setup logger
logger = setup_logger()


def summarize_texts(
    articles_id: List[str], max_length: int = 200, min_length: int = 20
):
    """
    Summarizes a list of texts using a pre-trained Transformer model.

    Args:
        texts (List[str]): List of texts to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.

    Returns:
        List[str]: List of summarized texts.
    """
    texts = []
    logger.info("Initializing summarization pipeline.")
    articles = find_documents("News_Articles", {"id": {"$in": articles_id}})
    for article in articles:
        texts.append(
            {"id": article["id"], "content": article.get("content", "")})
    article_summaries = []

    logger.info(f"Starting summarization of {len(texts)} texts.")
    for idx, obj in enumerate(texts):
        logger.debug(f"Summarizing text {idx+1}/{len(texts)}.")
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            Summarize the provided news document while preserving the most important keywords and maintaining the original sentiment or tone. Ensure that the summary is concise, accurately reflects the key points, and retains the emotional impact or intent of the original content.

            News Article:
            {obj.get("content")}
            """
            response = model.generate_content(
                prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            logger.debug(f"DEBUG SUmmary{response.text}")
            article_summaries.append(
                {"id": obj.get("id"), "summary": response.text})
            append_to_document(
                "News_Articles", {"id": obj.get("id")}, {
                    "summary": response.text}
            )
            logger.debug(f"Summary {idx+1}: {response.text}")

        except Exception as e:
            logger.error(f"Error summarizing text {idx+1}: {e}")
            article_summaries.append("")
            append_to_document("News_Articles", {
                               "id": obj.get("id")}, {"summary": ""})

    logger.info("Summarization completed.")
    return article_summaries


if __name__ == "__main__":
    # Test summarization
    texts = [
        {
            "id": "1",
            "content": "Early on Friday morning, a 31-year-old female trainee doctor retired to sleep in a  seminar hall after a gruelling day at one of India’s oldest hospitals.\nIt was the last time she was seen alive.\nThe next morning, her colleagues discovered her half-naked body on the podium, bearing extensive injuries. Police later arrested a hospital volunteer worker in connection with what they say is a case of rape and murder at Kolkata’s 138-year-old RG Kar Medical College.\nTens of thousands of women in Kolkata and across West Bengal state are expected to participate in a 'Reclaim the Night' march at midnight on Wednesday, demanding the \"independence to live in freedom and without fear\". The march takes place just before India's Independence Day on Thursday. Outraged doctors have struck work both in the city and across India, demanding a strict federal law to protect them.\nThe tragic incident has again cast a spotlight on the violence against doctors and nurses in the country. Reports of doctors, regardless of gender, being assaulted by patients and their relatives have gained widespread attention. Women - who make up nearly 30% of India’s doctors and 80% of the nursing staff - are more vulnerable than their male colleagues. \nThe crime in the Kolkata hospital last week exposed the alarming security risks faced by the medical staff in many of India's state-run health facilities.\nAt RG Kar Hospital, which sees over 3,500 patients daily, the overworked trainee doctors - some working up to 36 hours straight - had no designated rest rooms, forcing them to seek rest in a third-floor seminar room. \nReports indicate that the arrested suspect, a volunteer worker with a troubled past, had unrestricted access to the ward and was captured on CCTV. Police allege that no background checks were conducted on the volunteer.\n\"The hospital has always been our first home; we only go home to rest. We never imagined it could be this unsafe. Now, after this incident, we're terrified,\" says Madhuparna Nandi, a junior doctor at Kolkata’s 76-year-old National Medical College.\nDr Nandi’s own journey highlights how female doctors in India's government hospitals have become resigned to working in conditions that compromise their security. \nAt her hospital, where she is a resident in gynaecology and obstetrics, there are no designated rest rooms and separate toilets for female doctors.\n“I use the patients’ or the nurses' toilets if they allow me. When I work late, I sometimes sleep in an empty patient bed in the ward or in a cramped waiting room with a bed and basin,” Dr Nandi told me.\nShe says she feels insecure even in the room where she rests after 24-hour shifts that start with outpatient duty and continue through ward rounds and maternity rooms.\nOne night in 2021, during the peak of the Covid pandemic, some men barged into her room and woke her by touching her, demanding, “Get up, get up. See our patient.”\n“I was completely shaken by the incident. But we never imagined it would come to a point where a doctor could be raped and murdered in the hospital,” Dr Nandi says.\nWhat happened on Friday was not an isolated incident. The most shocking case remains that of Aruna Shanbaug, a nurse at a prominent Mumbai hospital, who was left in a persistent vegetative state after being raped and strangled by a ward attendant in 1973. She died in 2015, after 42 years of severe brain damage and paralysis. More recently, in Kerala, Vandana Das, a 23-year-old medical intern, was fatally stabbed with surgical scissors by a drunken patient last year.\nIn overcrowded government hospitals with unrestricted access, doctors often face mob fury from patients' relatives after a death or over demands for immediate treatment. Kamna Kakkar, an anaesthetist, remembers a harrowing incident during a night shift in an intensive care unit (ICU) during the pandemic in 2021 at her hospital in Haryana in northern India.\n“I was the lone doctor in the ICU when three men, flaunting a politician’s name, forced their way in, demanding a much in-demand controlled drug. I gave in to protect myself, knowing the safety of my patients was at stake,\" Dr Kakkar told me.\nNamrata Mitra, a Kolkata-based pathologist who studied at the RG Kar Medical College, says her doctor father would often accompany her to work because she felt unsafe.\n“During my on-call duty, I took my father with me. Everyone laughed, but I had to sleep in a room tucked away in a long, dark corridor with a locked iron gate that only the nurse could open if a patient arrived,” Dr Mitra wrote in a Facebook post over the weekend.\n“I’m not ashamed to admit I was scared. What if someone from the ward - an attendant, or even a patient - tried something? I took advantage of the fact that my father was a doctor, but not everyone has that privilege.”\nWhen she was working in a public health centre in a district in West Bengal, Dr Mitra spent nights in a dilapidated one-storey building that served as the doctor’s hostel.\n“From dusk, a group of boys would gather around the house, making lewd comments as we went in and out for emergencies. They would ask us to check their blood pressure as an excuse to touch us and they would peek through the broken bathroom windows,” she wrote.\nYears later, during an emergency shift at a government hospital, “a group of drunk men passed by me, creating a ruckus, and one of them even groped me”, Dr Mitra said. “When I tried to complain, I found the police officers dozing off with their guns in hand.”\nThings have worsened over the years, says Saraswati Datta Bodhak, a pharmacologist at a government hospital in West Bengal's Bankura district. \"Both my daughters are young doctors and they tell me that hospital campuses in the state are overrun by anti-social elements, drunks and touts,\" she says. Dr Bodhak recalls seeing a man with a gun roaming around a top government hospital in Kolkata during a visit.\nIndia lacks a stringent federal law to protect healthcare workers. Although 25 states have some laws to prevent violence against them, convictions are “almost non-existent”, RV Asokan, president of the Indian Medical Association (IMA), an organisation of doctors, told me. A 2015 survey by IMA found that 75% of doctors in India have faced some form of violence at work. “Security in hospitals is almost absent,” he says. “One reason is that nobody thinks of hospitals as conflict zones.”\nSome states like Haryana have deployed private bouncers to strengthen security at government hospitals. In 2022, the federal government asked the states to deploy trained security forces for sensitive hospitals, install CCTV cameras, set up quick reaction teams, restrict entry to \"undesirable individuals\" and file complaints against offenders. Nothing much has happened, clearly. \nEven the protesting doctors don't seem to be very hopeful. “Nothing will change... The expectation will be that doctors should work round the clock and endure abuse as a norm,” says Dr Mitra. It is a disheartening thought.\nWith his song Big Dawgs, Hanumankind has fast become a name to reckon with in the global hip-hop scene.\nEighty years on, three survivors recall the catastrophe which killed at least three million people.\nThe building is to become an Ibis hotel, but one floor is now being used by the Indian Consulate.\nThe venture will form India's biggest entertainment player, competing with Sony, Netflix, and Amazon.\nSeveral rivers and reservoirs are overflowing as water levels have crossed the danger mark.\nCopyright 2024 BBC. All rights reserved.  The BBC is not responsible for the content of external sites. Read about our approach to external linking.",
        },
        {
            "id": "2",
            "content": 'The rape and murder of a trainee doctor in India’s Kolkata city earlier this month has sparked massive outrage in the country, with tens of thousands of people protesting on the streets, demanding justice. BBC Hindi spoke to the doctor’s parents who remember their daughter as a clever, young woman who wanted to lead a good life and take care of her family.\nAll names and details of the family have been removed as Indian laws prohibit identifying a rape victim or her family.\n"Please make sure dad takes his medicines on time. Don\'t worry about me."\nThis was the last thing the 31-year-old doctor said to her mother, hours before she was brutally assaulted in a hospital where she worked. \n“The next day, we tried reaching her but the phone kept ringing," the mother told the BBC at their family home in a narrow alley, a few kilometres from Kolkata.\nThe same morning, the doctor’s partially-clothed body was discovered in the seminar hall, bearing extensive injuries. A hospital volunteer worker has been arrested in connection with the crime.\nThe incident has sparked massive outrage across the country, with protests in several major cities. At the weekend, doctors across hospitals in India observed a nation-wide strike called by the Indian Medical Association (IMA), with only emergency services available at major hospitals.\nThe family say they feel hollowed out by their loss.\n“At the age of 62, all my dreams have been shattered," her father told the BBC. \nSince their daughter\'s horrific murder, their house, located in a respectable neighbourhood, has become the focus of intense media scrutiny. \nBehind a police barricade stand dozens of journalists and camera crew, hoping to capture the parents in case they step out.\nA group of 10 to 15 police officers perpetually stand guard to ensure the cameras do not take photos of the victim\'s house.\nThe crime took place on the night of 9 August, when the woman, who was a junior doctor at the city\'s RG Kar Medical College, had gone to a seminar room to rest after a gruelling 36-hour shift. \nHer parents remembered how the young doctor, their only child, was a passionate  student who worked extremely hard to become a doctor. \n“We come from a lower middle-class background and built everything on our own. When she was little, we struggled financially," said the father, who is a tailor.\nThe living room where he sat was cluttered with tools from his profession - a sewing machine, spools of thread and a heavy iron. There were scraps of fabrics scattered on the floor. \nThere were times when the family did not have money to even buy pomegranates, their daughter\'s favourite fruit, he continued. \n"But she could never bring herself to ask for anything for herself."\n“People would say, ‘You can’t make your daughter a doctor\'. But my daughter proved everyone wrong and got admission in a government-run medical college," he added, breaking down. A relative tried to console him.\nThe mother recalled how her daughter would write in her diary every night before going to bed.\n“She wrote that she wanted to win a gold medal for her medical degree. She wanted to lead a good life and take care of us too,” she said softly.\nAnd she did. \nThe father, who is a high blood-pressure patient, said their daughter always made sure he took his medicines on time. \n“Once I ran out of medicine and thought I’d just buy it the next day. But she found out, and even though it was around 10 or 11pm at night, she said no-one will eat until the medicine is here,” he said.\n“That’s how she was - she never let me worry about anything."\nHer mother listened intently, her hands repeatedly touching a gold bangle on her wrist - a bangle she had bought with her daughter.\nThe parents said their daughter’s marriage had almost been finalised. "But she would tell us not to worry and say she would continue to take care of all our expenses even after marriage," the father said. \nAs he spoke those words, the mother began to weep, her soft sobs echoing in the background.\nOccasionally, her eyes would wander to the staircase, leading up to their daughter\'s room.\nThe door has remained shut since 10 August and the parents have not set foot there since the news of her death.\nThey say they still can\'t believe that something "so barbaric" could happen to their daughter at her workplace. \n"The hospital should be a safe place," the father said. \nViolence against women is a major issue in India - an average of 90 rapes a day were reported in 2022, according to government data.\nThe parents said their daughter’s death had brought back memories of a 2012 case when a 22-year-old physiotherapy intern was gang-raped on a moving bus in capital Delhi. Her injuries were fatal.\nFollowing the assault - which made global headlines and led to weeks of protests - India tightened laws against sexual violence.\nBut reported cases of sexual assault have gone up and access to justice still remains a challenge for women.\nLast week, thousands participated in a Reclaim the Night march held in Kolkata to demand safety for women across the country.\nThe doctor’s case has also put a spotlight on challenges faced by healthcare workers, who have demanded a thorough and impartial investigation into the murder and a federal law to protect them - especially women - at work.\nFederal Health Minister JP Nadda has assured doctors that he will bring in strict measures to ensure better safety in their professional environments.\nBut for the parents of the doctor, it\'s too little too late.\n“We want the harshest punishment for the culprit," the father said.\n“Our state, our country and the whole world is asking for justice for our daughter."\nWith his song Big Dawgs, Hanumankind has fast become a name to reckon with in the global hip-hop scene.\nEighty years on, three survivors recall the catastrophe which killed at least three million people.\nThe building is to become an Ibis hotel, but one floor is now being used by the Indian Consulate.\nAmi and Stuart Geddes son Clark was delivered at 24 weeks due to complications and lived for just 12 days.\nThe venture will form India\'s biggest entertainment player, competing with Sony, Netflix, and Amazon.\nCopyright 2024 BBC. All rights reserved.  The BBC is not responsible for the content of external sites. Read about our approach to external linking.',
        },
    ]
    print("Here")
    summaries = summarize_texts(texts)
    print("Now here")
    print(summaries)
