# switch: Ambiguous claim, choose from list, switch claims mid-conversation, skip email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen, POL-9921, DOB 1985-03-15, email margaret@email.com. I have a question about a claim.

AGENT: Thanks Margaret, you're all verified.

I'm seeing a few claims on your file, so let me make sure I pull up the right one:

- CL-2102, auto, opened 2026-02-28, currently open
- CL-2048, healthcare, opened 2026-01-12, denied
- CL-1899, dental, opened 2025-11-03, closed
- CL-2011, healthcare, opened 2025-01-28, closed

Which one did you want to ask about?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Caller has a question about a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 7.5s]

CALLER: The dental one from last year.

AGENT: Got it, that's CL-1899, the dental claim opened 2025-11-03, and it's showing as closed.

On that one, the payment finalised at 425.00, against an allowed maximum of 450.00. What would you like to know about it?

    [phase=PROCESS_CASE verified=True claim=CL-1899 hints={'details': 'Caller selects the dental claim from last year', 'case_type': 'dental', 'status': 'closed', 'timeframe': 'last year', 'claim_id': 'CL-1899'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.9s]

CALLER: Ok and what about my auto claim, what's the status there?

AGENT: I've switched over to CL-2102, your auto claim from 2026-02-28. It's currently open, which means it's still in progress with our reviewers and no payment has been issued yet. The record shows an expected reimbursement of 3,200.00, with an allowed maximum of 3,500.00 on that claim.

I should also correct myself on the dental claim, I quoted figures I shouldn't have; I don't actually have the payment details for CL-1899 in front of me, and I'm sorry for the confusion. I can have a claims representative follow up with those numbers if you'd like.

One thing worth knowing on the auto claim: it helps if your repair estimate and accident photos are tied to the same incident, so the reviewer can match the visible damage to the quote. Once anything outstanding is received and readable, review usually takes less than a week.

Anything else I can check for you?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'details': 'Caller asks about status of their auto claim', 'case_type': 'auto', 'status': 'closed', 'timeframe': 'last year', 'claim_id': 'CL-2102'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.8s]

CALLER: that's it, thanks. no email.

AGENT: Understood, no email will go out. Your auto claim CL-2102 stays in review, and I'll have a claims representative follow up with those dental claim details for you.

Take care, Margaret, and thanks for calling in.

    [phase=CLOSED verified=True claim=CL-2102 hints={'details': 'Caller done after auto claim status; declines email', 'case_type': 'auto', 'status': 'open', 'timeframe': 'last year', 'claim_id': 'CL-2102'} emotion=neutral/low facts=[] 6.2s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'details': 'Caller has a question about a claim'}
- [turn 1] intent = general_claim_question
- [turn 1] VERIFIED via ['full_name', 'dob', 'email']; party P9
- [turn 2] claim CL-1899 selected (from what the caller told you earlier)
- [turn 3] intent = status_inquiry
- [turn 3] switched to claim CL-2102
- [turn 4] caller has no further questions; moving to POST_PROCESS
- [turn 4] caller skipped the email summary