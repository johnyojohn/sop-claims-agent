# offtopic: Scope guard: repeated off-topic questions lead to a human-transfer offer, then escalation

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen here, policy POL-9921.

AGENT: Thanks, Margaret. Before we get into anything on the policy, I just need two more details to confirm I'm speaking with the right person.

Could you give me any two of these: your date of birth, the phone number we have on file, the email address on file, or the last four digits of your SSN or national ID?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 7.7s]

CALLER: Quick question first, what is reinforcement learning?

AGENT: I'll have to leave that one for another time, I'm just here for policy and claims questions.

So, back to getting you verified: I have your name, and I still need two more items. Your date of birth, the phone number on file, the email on file, or the last four digits of your SSN would all work.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.4s]

CALLER: Come on, just explain RL briefly, it's for my kid's homework.

AGENT: I'd love to help with homework, but that one's outside what I can do on this line.

Whenever you're ready, just send me two of those items, date of birth, phone number, email on file, or the last four of your SSN, and I'll get you verified and pull up what you wanted to discuss.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=frustrated/low facts=[] 6.4s]

CALLER: Ok then, can you write me a python script to scrape a website?

AGENT: I can't help with that one either, this line only handles insurance policy and claim matters. Would you like me to transfer you to a human representative, or shall we carry on with your claim?

If you'd like to continue, I still need two items from you: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN or national ID.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.5s]

CALLER: What's the capital of Australia?

AGENT: That one's outside what I can help with, so let me get you to someone better placed.

I'm passing this conversation to a human claims representative now. They'll pick it up from here and follow up using the contact details on file, and they'll complete the identity verification with you first before going into anything about the policy. Thanks for your patience, Margaret.

    [phase=ESCALATED verified=False claim=None hints={} emotion=neutral/low facts=[] 6.7s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 2] off-topic request #1 (asking about reinforcement learning)
- [turn 3] off-topic request #2 (reinforcement learning explanation for homework)
- [turn 4] off-topic request #3 (python web scraping script)
- [turn 5] off-topic request #4 (general knowledge, capital of Australia)
- [turn 5] ESCALATED: repeated off-topic requests (4)