# offtopic: Scope guard: repeated off-topic questions lead to a human-transfer offer, then escalation

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen here, policy POL-9921.

AGENT: Thanks, Margaret — the policy number helps me find the account. To confirm I'm speaking with the right person, I'll need two more details from this list: your date of birth, the phone number on file, the email address on file, or the last four digits of your SSN.

Which would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.2s]

CALLER: Quick question first, what is reinforcement learning?

AGENT: Ha, that one's a bit outside my lane here on the claims line — I'll have to leave that to the experts.

Back to getting you verified: I have your name, so I still need two of the following — your date of birth, the phone number on file, the email on file, or the last four digits of your SSN. Which works best?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.9s]

CALLER: Come on, just explain RL briefly, it's for my kid's homework.

AGENT: I'd love to help, but homework's one thing I've got to pass on — I'm only set up for policy and claims questions here.

So, to get you verified I just need two of these: your date of birth, the phone number on file, the email on file, or the last four of your SSN. Whichever's easiest.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.5s]

CALLER: Ok then, can you write me a python script to scrape a website?

AGENT: I'm not able to help with coding or anything outside insurance — this line only handles policy and claim matters. Would you like me to transfer you to a human representative, or shall we keep going with your claim?

If you'd like to continue, I still need two of these: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 7.0s]

CALLER: What's the capital of Australia?

AGENT: That one's outside what I can help with here, so I'm going to hand you over to a human claims representative now.

They'll pick up this conversation and follow up using the contact details we have on file. Since we didn't get through verification, they'll take care of that first before going over anything on your policy. Thanks for your patience, Margaret — hang tight.

    [phase=ESCALATED verified=False claim=None hints={} emotion=neutral/low facts=[] 17.9s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 2] off-topic request #1 (asking about reinforcement learning)
- [turn 3] off-topic request #2 (reinforcement learning explanation for homework)
- [turn 4] off-topic request #3 (python web scraping script request)
- [turn 5] off-topic request #4 (general knowledge trivia about Australia's capital)
- [turn 5] ESCALATED: repeated off-topic requests (4)