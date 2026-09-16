# rep_timeout: Representative, consent never arrives (timeout scenario)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: This is David Chen, son of Margaret Chen, calling about her claim. Her DOB is 1985-03-15, last four 4472.

AGENT: Thanks, David, that all matches up on Margaret's side.

I've just sent a consent request to Margaret using the contact details we have on file. Once she approves it, I can go through the claim with you. She'll usually respond within a minute or two, so just let me know when you'd like me to check on it.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.6s]

CALLER: Any update?

AGENT: I checked just now and the consent hasn't come through yet. These sometimes take a few minutes to land on her end, so it's nothing to worry about.

Happy to check again in a moment, just say the word.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.0s]

CALLER: Still nothing?

AGENT: I checked again just now and it still hasn't come through. Nothing has gone wrong, it just hasn't been approved on her end yet.

If it's easier, Margaret can approve it whenever she gets a moment and we can pick this straight up. Otherwise say the word and I'll check once more.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=anxious/low facts=[] 6.2s]

CALLER: Check again please.

AGENT: I've just checked and there's still no approval on it. I know that's not the answer you were hoping for.

I'll keep it open on my side, so if it might help to nudge Margaret to look for the request, I'm happy to check again right after.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Waiting on consent approval from policyholder'} emotion=neutral/low facts=[] 6.1s]

CALLER: Ugh. And again?

AGENT: Checked again, and it's still not through. I'm sorry, I know this is wearing thin when you just want to get on with it.

Nothing's expired on my end, so the moment she approves it I can pull everything up. Want me to try once more in a minute or two?

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Waiting on consent approval from policyholder'} emotion=frustrated/medium facts=[] 6.8s]

CALLER: Once more.

AGENT: I've checked once more and it's still not showing as approved, unfortunately.

Nothing's lost, the request stays live, so whenever Margaret approves it we can go straight into her claim. I can check again shortly, or if you'd prefer, a claims representative can follow up with her directly so you're not sat waiting on me.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Waiting on policyholder Margaret to approve authorization request'} emotion=frustrated/medium facts=[] 6.6s]

CALLER: And now?

AGENT: I'm afraid that request has now timed out without being approved, so I can't go through Margaret's claim with you on this call. I know that's frustrating after all that waiting.

There are a few ways forward: Margaret can call us directly herself, or I can send a fresh consent request whenever she's ready to watch for it, or I can pass this to a claims representative to follow up with her. Which would you prefer?

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Waiting on Margaret's authorization approval before claim can be accessed"} emotion=frustrated/medium facts=[] 7.1s]

CALLER: Fine, transfer me to a person.

AGENT: Of course, David, I'll hand this over now.

A claims representative will take over this conversation and follow up using the contact details we have on file. Because we weren't able to complete verification here, they'll take care of that step first before going into any details. Thanks for bearing with it.

    [phase=ESCALATED verified=False claim=None hints={'details': "Waiting on Margaret's authorization approval before claim can be accessed"} emotion=frustrated/medium facts=[] 5.5s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'details': "Calling about his mother's claim"}
- [turn 1] representative matched (son); consent request CONSENT-6F55C5 sent
- [turn 4] stored case hints for later: {'details': 'Waiting on consent approval from policyholder'}
- [turn 6] stored case hints for later: {'details': 'Waiting on policyholder Margaret to approve authorization request'}
- [turn 7] stored case hints for later: {'details': "Waiting on Margaret's authorization approval before claim can be accessed"}
- [turn 7] consent request timed out
- [turn 8] ESCALATED: caller asked for a human representative