# rep_timeout: Representative, consent never arrives (timeout scenario)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: This is David Chen, son of Margaret Chen, calling about her claim. Her DOB is 1985-03-15, last four 4472.

AGENT: Thanks, David. You're listed on file as Margaret's son, so the next step is her okay to discuss the claim with you. I've just sent a consent request to the contact details we have on file for her.

Once she approves it, I can go through the claim with you. Just say the word when you'd like me to check on it, she'll usually respond within a minute or two.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.8s]

CALLER: Any update?

AGENT: I just checked and it hasn't come through yet, so nothing on our end to act on quite yet.

Happy to check again in a minute if you'd like to hold on, these usually land pretty quickly once she opens the message.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.3s]

CALLER: Still nothing?

AGENT: I checked again just now and it still hasn't come through, sorry to keep you waiting.

Nothing's gone wrong, we just can't move forward until she approves it. I'm happy to keep checking, or if it's easier, I can stay on while you give her a nudge.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent"} emotion=anxious/low facts=[] 6.7s]

CALLER: Check again please.

AGENT: Just checked again, and I'm afraid it still hasn't arrived.

I'll keep an eye on it and check again whenever you'd like. If she's not near her phone or email right now, we can also leave the request open, it stays active, so you can call back once she's approved it and we'll pick up right where we left off.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent approval"} emotion=neutral/low facts=[] 7.0s]

CALLER: Ugh. And again?

AGENT: I hear you, this is a frustrating way to spend your morning. I checked once more and it's still not showing as approved.

I'm not going to pretend it'll change in the next thirty seconds, so your call: I can check again shortly, or leave the request open so you can ring back the moment she's approved it and we'll go straight to the claim.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent approval"} emotion=frustrated/medium facts=[] 6.8s]

CALLER: Once more.

AGENT: Checked again just now, and it's still pending on her end.

That's five or six checks with no change, so I suspect she hasn't seen the message yet. The request stays open, so there's no rush and nothing expires. Would you rather I check once more in a few minutes, or let you go and call us back once she's given the okay?

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent approval"} emotion=frustrated/medium facts=[] 6.6s]

CALLER: And now?

AGENT: I've got an update, though not the one either of us wanted. The consent request has now timed out without being approved, so it's no longer active and I still can't go into her claim details.

Nothing's lost, though. There are a few ways forward: Margaret can call us directly herself, or I can send a fresh consent request later when she's near her phone, or I can pass this to one of our claims representatives to follow up with her directly.

Which of those would work best for you?

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent approval"} emotion=frustrated/medium facts=[] 6.2s]

CALLER: Fine, transfer me to a person.

AGENT: Of course, David. I'm passing you over to one of our claims representatives now, and they'll take over this conversation from here.

They'll need to complete verification first, since we weren't able to confirm authorisation on this call, and they'll follow up using the contact details we have on file. Thanks for your patience with all the back and forth.

    [phase=ESCALATED verified=False claim=None hints={'details': "Calling about his mother's claim; awaiting her consent approval"} emotion=frustrated/medium facts=[] 6.6s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'details': "Calling about his mother's claim"}
- [turn 1] intent = general_claim_question
- [turn 1] representative matched (son); consent request CONSENT-E3C862 sent
- [turn 3] stored case hints for later: {'details': "Calling about his mother's claim; awaiting her consent"}
- [turn 4] stored case hints for later: {'details': "Calling about his mother's claim; awaiting her consent approval"}
- [turn 7] consent request timed out
- [turn 8] ESCALATED: caller asked for a human representative