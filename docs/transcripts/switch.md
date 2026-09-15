# switch: Ambiguous claim, choose from list, switch claims mid-conversation, skip email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen, POL-9921, DOB 1985-03-15, email margaret@email.com. I have a question about a claim.

AGENT: Thanks, Margaret, you're all verified.

I'm seeing four claims on file, so let me make sure I pull up the right one:

- CL-2048, healthcare, filed 2026-01-12, denied
- CL-2011, healthcare, filed 2025-01-28, closed
- CL-1899, dental, filed 2025-11-03, closed
- CL-2102, auto, filed 2026-02-28, open

Which one did you want to ask about?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Caller has a question about a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 7.7s]

CALLER: The dental one from last year.

AGENT: Got it, that's CL-1899, the dental claim filed 2025-11-03, and it's closed.

It shows as completed with a payment of $425.00, against an allowed maximum of $450.00. What would you like to know about it?

    [phase=PROCESS_CASE verified=True claim=CL-1899 hints={'details': 'Caller selected the dental claim from last year', 'case_type': 'dental', 'status': 'closed', 'timeframe': 'last year', 'claim_id': 'CL-1899'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 6.0s]

CALLER: Ok and what about my auto claim, what's the status there?

AGENT: Switched over to CL-2102, your auto claim filed 2026-02-28. It's currently open, which means it's still in progress and hasn't been finalized yet.

On the numbers side, the expected reimbursement is $3,200.00 against an allowed maximum of $3,500.00, and nothing has been paid out yet. I don't see any outstanding documents being requested on this one right now.

One thing worth keeping in mind for auto claims: if you do send in anything further, keep the repair estimate and the accident photos tied to the same incident so the reviewer can match the visible damage to the quote. Once files come in and they're readable, review usually takes less than a week, though it can need another cycle before the status changes.

Anything else I can look into for you?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'details': 'Caller asks about status of their auto claim', 'case_type': 'auto', 'status': 'open', 'timeframe': 'last year', 'claim_id': 'CL-2102'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.6s]

CALLER: that's it, thanks. no email.

AGENT: Sounds good, Margaret, no email then. Thanks for calling, and take care.

    [phase=POST_PROCESS verified=True claim=CL-2102 hints={'details': 'Caller asks about status of their auto claim', 'case_type': 'auto', 'status': 'open', 'timeframe': 'last year', 'claim_id': 'CL-2102'} emotion=neutral/low facts=[] 5.9s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'details': 'Caller has a question about a claim'}
- [turn 1] intent = general_claim_question
- [turn 1] VERIFIED via ['full_name', 'dob', 'email']; party P9
- [turn 2] claim CL-1899 selected (from what the caller told you earlier)
- [turn 3] intent = status_inquiry
- [turn 3] switched to claim CL-2102
- [turn 4] caller has no further questions; moving to POST_PROCESS
- [turn 4] email summary offered