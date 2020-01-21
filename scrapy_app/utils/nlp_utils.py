import os
from rake_nltk import Rake
from summa import summarizer, keywords

_text = '''
    My daughter’s dad wanted out of his first marriage, but he didn’t want to be alone when he ended things. During our (mostly online) affair, we talked a lot about moving forward and starting our own life. Together.

He was insistent that he couldn’t leave his wife until I was able to be there for him. At the time, I lived in Minnesota and he lived in Tennessee. I told him that I needed to find a job and an apartment first, but that the sooner he came clean about wanting a divorce, the better it would be for everyone involved.

He still wanted me to promise to be there as soon as he left, and we decided to make plans for everything to happen in July.
The plans we made were very surreal. Anytime you fall for someone online, it’s difficult to feel that it’s actually happening. Personally, I struggled a lot with that weird sense of reality. I felt guilty about having an affair with a married man. I knew I was playing with fire and I wasn’t sure where it all would lead.

The affair began online in early February. We met in real life in mid-May. Just a week after I flew down to Tennessee so we could finally meet, he told his wife he wanted a divorce.

Without warning me.

He didn’t do it for me or for us. The reason he finally told his wife was because he’d confessed the affair to a guy friend who said he couldn’t respect him unless he told his wife the truth.

In reality, he didn’t actually tell his wife the truth. Instead, he simply said he wanted a divorce. When she asked if there was someone else, he insisted there wasn’t.

“She’s going to find out about me,” I said. “It will be even worse for her to discover you lied about cheating. And it will be worse for me if everybody thinks I was the only one.”

Still, he refused to come clean. He couldn’t, he claimed. His wife packed up their three kids and drove out of state to spend time with her parents. He decided to drive up to see me.

We spent a long Memorial Day weekend together. It was stupid and reckless much like any other affair, and we were each fooled by the fantasy of being happy in love.

He kept complaining that I was supposed to be there with him. That he couldn’t get through everything alone. I was painfully naive, so I did what he never would have done for me--I left my job, my home, and entire life to live with him in Tennessee.

We didn’t really have a place to stay in Tennessee, however. The home he rented with his family was vacant, but they would be back after their trip. He was unwilling or unable to spend money on a hotel, and I didn’t get paid until the following week.

Against my better judgment, we spent the first night in Tennessee at his place. I already felt like a jerk falling for him. Spending a night in his family home definitely didn’t help.

I often wonder why I never stopped, never turned around, never ran away. All I can think is that I felt too committed to seeing the foolish thing through.

In my mind, the only way to make the whole affair “right” was if we actually wound up together. I lived with the guilt by fooling myself like that. By telling myself it would be worth it in the end.

After spending that first night in his home, he went into work the next morning, about 30 minutes away. My plan for the day was to go job hunting online. There was nothing else I could do without transportation in this new town.

I sat on the bed--their bed--and filled out job applications on my laptop. I was fully dressed and there was nothing sexy about it, but I knew I was in big trouble as soon as I heard keys in the door a couple of hours after my married boyfriend left for work.

For one brief moment, I contemplated hiding under the bed. Figuring that would be even worse, I didn’t move. There was a slim chance that who ever it was might not even walk into the bedroom.

Slim.

I sat there frozen for what felt like forever, with my heart caught in my throat. Eventually, a woman walked into the bedroom and demanded to know who I was.

This was not his wife. As it turns out, she was a friend of his wife’s, and she’d been charged with the task of checking in on the house and feeding the pets.

My first thought was frustration that he didn’t consider this possibility. That I’d get caught in his house with no way out. My next thought was what on earth I could say.

Nothing I said was going to make the situation any better. I knew that. So, I said about as little as possible. There was no use in lying about it, so, I answered her basic questions. Were we dating? Yes. How long? For a few months.

The woman was angry for her friend and rightfully so. “He’s married with three kids,” she shouted. “I’m calling his wife.”

She called her and immediately told his wife everything. “There’s a woman in your house who’s dating your husband.” By the sound of things, his wife had a ton of questions.

“Do you want to talk to her?” I silently pleaded with the universe that she would not want to speak to me. She didn’t.

I waited for the conversation to end. Waited for the friend to say everything she wanted to say to me about how I was this terrible homewrecker.

The woman finally left and I messaged him that he needed to come and get me out of there. I explained what happened and soon his wife was calling him too. He couldn’t come get me, he claimed.

Instead, he’d have a friend come over to drive me to him. He asked me to pack up some of his stuff.

In those days, my ex was friends with all of his exes. Out of all the red flags I’d ignored, that was the one that creeped me out the most at the time.

A lot of people think that’s no big deal, but this was a guy who got married right out of high school. His exes were nearly all ex-mistresses.

There was one woman in particular who worked with him. Like a lot of his extramarital partners, she lived with her own boyfriend, but was unhappy with the relationship. She wanted to have a baby, but her boyfriend did not.

She seemed to think that the married dad might prove to be her ticket to starting a family. Except that he didn’t want another baby.

This woman and I had begun to become unwitting friends because we were each involved with his blog and Facebook group. But he didn’t want us to become friends.

“She’s kinda crazy,” he told me. “I wish you wouldn’t talk to her.” I asked if they had been involved and after a lot of prodding and intial denials, he admitted they had a brief fling. He said he called it off because she wanted a baby and threatened to come over to his house when his family was home.

In reality, however, he’d been seeing her at the same time he began pursuing me. It was true that he’d ended things with her and eventually told me the truth about the timeline, but she was hurt that he “chose” me over her.
'''

def extract_keywords_rake(text):
    r = Rake()

    r.extract_keywords_from_text(_text)

    return r.get_ranked_phrases()[:5]

def summarize_keywords_summa(text):
    _summary = summarizer.summarize(text)
    _keywords = keywords.keywords(text, words=10)

    return _summary, _keywords

def extract_article_text(link):
    from newspaper import Article

    article = Article(link)
    article.download()
    article.parse()

    return article.text

def detect_language(text):
    from textblob import TextBlob

    blob = TextBlob(text)
    return blob.detect_language()

def extract_details_text(_link):
    details = {}
    _text = extract_article_text(_link)
    details['lang'] = detect_language(_text)
    if details.get('lang') == 'en':
        details['summary'], details['keywords'] = summarize_keywords_summa(_text)
    else:
        details['summary'] = []
        details['keywords'] = []

    return details

#print(extract_keywords(_text))
#summary, keywords = summarize_keywords_summa(_text)
#print(summary)
#print("*"*30)
#print(keywords)

details = extract_details_text("https://medium.com/better-programming/5-simple-git-commands-to-supercharge-productivity-3bbd31da4abb")

for key, value in details.items():
    print (key, ":", value, "\n")
