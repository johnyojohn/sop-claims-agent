# rep_timeout: Representative, consent never arrives (timeout scenario)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: This is David Chen, son of Margaret Chen, calling about her claim.

AGENT: Thanks, David. I have you noted as Margaret's son, and I've just sent a consent request to her using the contact details we have on file.

Once she approves it, I can go through the claim with you. She'll usually respond within a minute or two, so just say the word when you'd like me to check on it.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 6.0s]

CALLER: Any update?

AGENT: I checked just now, and her approval hasn't come through yet. I'm happy to check again in a moment if you'd like to give it another minute.

Nothing's lost in the meantime, so no need to worry.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 5.9s]

CALLER: Still nothing?

AGENT: I've checked again, and it's still not showing her approval on our end. Give it another minute or two and I'll look once more.

These requests do sometimes take a little while to land, so this isn't unusual. I'll stay right here with you.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about mother's claim"} emotion=anxious/low facts=[] 6.2s]

CALLER: Check again please.

AGENT: Just checked again, David, and her approval still hasn't come through. I'm happy to keep checking, or if it's easier, you could give her a nudge to look for the request we sent.

Nothing's expiring on your end while we wait, so take whatever time you need.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Calling about his mother's claim"} emotion=neutral/low facts=[] 7.1s]

CALLER: Ugh. And again?

AGENT: I know this is aggravating, and I wish I had better news. I checked again just now and her approval still isn't showing on our end.

Say the word and I'll check once more in a minute. If she'd rather not wait around for it, another option is for her to reach us directly and verify herself, and I can help from there.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Waiting on policyholder's authorization approval to come through"} emotion=frustrated/medium facts=[] 6.8s]

CALLER: Once more.

AGENT: Checked again just now, and it's still pending on our side. Nothing has come through from her yet.

I'll keep checking as long as you want me to. If it starts feeling like a dead end, having her contact us directly is usually the quicker path.

    [phase=VERIFY_ID verified=False claim=None hints={'details': "Waiting on policyholder's authorization approval to come through"} emotion=frustrated/medium facts=[] 6.3s]

CALLER: Fine, transfer me to a person.

AGENT: Absolutely, David, I'll hand you over now. A claims representative will take over this conversation and follow up using the contact details we have on file.

Since we weren't able to complete verification here, they'll take care of that step first, and then they can help you properly. Thanks for hanging in there through the wait.

    [phase=ESCALATED verified=False claim=None hints={'details': "Waiting on policyholder's authorization approval to come through"} emotion=frustrated/high facts=[] 6.2s]

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'details': "Calling about his mother's claim"}
- [turn 1] representative matched (son); consent request CONSENT-5EFCDE sent
- [turn 3] stored case hints for later: {'details': "Calling about mother's claim"}
- [turn 4] stored case hints for later: {'details': "Calling about his mother's claim"}
- [turn 5] stored case hints for later: {'details': "Waiting on policyholder's authorization approval to come through"}
- [turn 7] ESCALATED: caller asked for a human representative