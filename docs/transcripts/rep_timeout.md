# rep_timeout: Representative, consent never arrives (timeout scenario)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: This is David Chen, son of Margaret Chen, calling about her claim.

AGENT: Thanks, David. Since you're calling on Margaret's behalf, we've just sent a consent request to her using the contact details on file, and once she approves it I can go through the claim with you.

She'll usually respond within a minute or two, so just let me know when you'd like me to check on it.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.0s]

CALLER: Any update?

AGENT: I just checked, and her approval hasn't come through yet. Happy to check again in a moment, these sometimes take a few minutes to land, and as soon as it's approved I can pull everything up for you.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 5.9s]

CALLER: Still nothing?

AGENT: I checked again just now and it still hasn't come through. Nothing has gone wrong on our end, it just hasn't been approved yet, so if she can look for that request from us, I'll keep checking and we can pick right up once it lands.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim; waiting on consent approval"} emotion=anxious/low facts=[] 6.3s]

CALLER: Check again please.

AGENT: Checked once more, and it's still showing as pending on my side. I know that's frustrating when you're just trying to get this sorted for her.

If she's near her phone or email, it may be worth a nudge, and I'm happy to check again whenever you'd like.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim; awaiting consent approval"} emotion=frustrated/low facts=[] 6.8s]

CALLER: Ugh. And again?

AGENT: Just checked, and still nothing yet. I'm sorry, I know this is wearing thin when you've been sitting here waiting.

I'm not going anywhere, so say the word and I'll check again, or if it's easier, a claims representative can follow up once her approval comes through so you're not stuck holding.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim; awaiting consent approval"} emotion=frustrated/medium facts=[] 6.5s]

CALLER: Once more.

AGENT: Checked again, and it's still pending on my end. I wish I had better news for you.

If it helps, I can keep checking while you give her a nudge, or we can arrange for someone to follow up as soon as her approval lands so you're not waiting on the line.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim; awaiting consent approval"} emotion=frustrated/medium facts=[] 6.3s]

CALLER: And now?

AGENT: I checked again, and unfortunately that consent request has now timed out, so it won't approve on its own. I'm sorry, I know that's the last thing you wanted to hear after waiting this long.

There are a few ways forward: Margaret can call us directly and we can handle it in one go, or I can send a fresh consent request for her to approve later, or I can hand this to a claims representative to follow up with you both. Which would you prefer?

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim; awaiting consent approval"} emotion=frustrated/medium facts=[] 6.0s]

CALLER: Fine, transfer me to a person.

AGENT: Of course, David. I'm handing this conversation to a claims representative now, and they'll pick it up from here and follow up using the contact details we have on file.

One thing to expect: since we weren't able to verify identity on this call, they'll need to complete that step with you first before going into any details. Thanks for your patience, I know this has been a long one.

    [phase=ESCALATED verified=False claim=None hints={'details': 'Consent request from policyholder Margaret timed out during verification'} emotion=frustrated/medium facts=[] 6.0s]

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'details': "Calling about his mother's claim"}
- [turn 1] representative matched (son); consent request CONSENT-3288DD sent
- [turn 3] stored case hints for later: {'details': "Calling about mother's claim; waiting on consent approval"}
- [turn 4] stored case hints for later: {'details': "Calling about mother's claim; awaiting consent approval"}
- [turn 7] consent request timed out
- [turn 8] stored case hints for later: {'details': 'Consent request from policyholder Margaret timed out during verification'}
- [turn 8] ESCALATED: caller asked for a human representative