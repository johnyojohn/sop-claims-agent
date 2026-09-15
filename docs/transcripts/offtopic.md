# offtopic: Scope guard: repeated off-topic questions lead to a human-transfer offer, then escalation

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen here, policy POL-9921.

AGENT: Thanks, Margaret. I have your name noted, and I'll use that policy number to pull things up once we finish verifying.

To get you verified I need two more items from this list: your date of birth, the phone number we have on file, the email address on file, or the last four digits of your SSN or national ID. Which would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.4s]

CALLER: Quick question first, what is reinforcement learning?

AGENT: I'm not able to get into that one here, but I'm happy to keep going on your claim.

To finish verifying, I still need two items from these: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN or national ID. Which would you like to give me first?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 5.9s]

CALLER: Come on, just explain RL briefly, it's for my kid's homework.

AGENT: I'll have to leave that one to a search engine, sorry. But let's get you sorted here.

Two items and we're done: date of birth, phone number on file, email on file, or the last four of your SSN or national ID.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=frustrated/low facts=[] 6.1s]

CALLER: Ok then, can you write me a python script to scrape a website?

AGENT: I'm not able to help with writing code, as this line only handles insurance policy and claim matters. Would you like me to transfer you to a human representative, or shall we carry on with your claim?

If you'd like to continue, I still need two items from these: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN or national ID.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.8s]

CALLER: What's the capital of Australia?

AGENT: I'm going to hand you over to one of our claims representatives at this point. They'll pick up this conversation from here and follow up using the contact details we have on file.

Since we didn't get through verification, they'll take care of that first before going into anything about your policy. Thanks for your patience, Margaret.

    [phase=ESCALATED verified=False claim=None hints={} emotion=neutral/low facts=[] 6.7s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 2] off-topic request #1 (machine learning concept question)
- [turn 3] off-topic request #2 (reinforcement learning explanation for homework)
- [turn 4] off-topic request #3 (python web scraping script request)
- [turn 5] off-topic request #4 (general knowledge trivia about Australia's capital)
- [turn 5] ESCALATED: repeated off-topic requests (4)