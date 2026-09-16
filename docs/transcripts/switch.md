# switch: Ambiguous claim, choose from list, switch claims mid-conversation, skip email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, Margaret Chen, POL-9921, DOB 1985-03-15, email margaret@email.com. I have a question about a claim.

AGENT: Thanks, Margaret, you're all verified.

I'm seeing a few claims on your file, so just so I pull up the right one:

- CL-2048, healthcare, January 12, 2026, denied
- CL-2011, healthcare, January 28, 2025, closed
- CL-1899, dental, November 3, 2025, closed
- CL-2102, auto, February 28, 2026, open

Which one did you want to ask about?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Caller has a question about a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 8.5s]

CALLER: The dental one from last year.

AGENT: Got it, that's CL-1899, the dental claim opened November 3, 2025, and it's closed.

That one was finalized with a payment of $425, against an allowed maximum of $450 for the covered service. What would you like to know about it?

    [phase=PROCESS_CASE verified=True claim=CL-1899 hints={'details': 'Caller selects the dental claim from last year', 'case_type': 'dental', 'status': 'closed', 'timeframe': 'November 2025', 'claim_id': 'CL-1899'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 7.1s]

CALLER: Ok and what about my auto claim, what's the status there?

AGENT: Sure, I've switched over to CL-2102, your auto claim from February 28, 2026. It's currently open, which means it's in progress with our review team and no payment has been issued yet.

Right now the expected reimbursement on it is $3,200, against an allowed maximum of $3,500. Nothing is showing as outstanding from you at the moment, and once files are received and readable, claims like this usually move through review in less than a week. Anything else I can check for you?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'case_type': 'auto', 'status': 'open', 'claim_id': 'CL-2102', 'details': 'Asks about the status of her auto claim'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file', 'claims_already_discussed_this_call'] 10.5s]

CALLER: that's it, thanks. no email.

AGENT: Understood, no email summary will be sent. Thanks for calling, Margaret, and take care.

    [phase=CLOSED verified=True claim=CL-2102 hints={'case_type': 'auto', 'status': 'open', 'claim_id': 'CL-2102', 'details': 'Caller done after auto claim status; declines email summary'} emotion=neutral/low facts=[] 5.9s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'details': 'Caller has a question about a claim'}
- [turn 1] intent = general_claim_question
- [turn 1] VERIFIED via ['full_name', 'dob', 'email']; party P9
- [turn 2] claim CL-1899 selected (from what the caller told you earlier)
- [turn 3] case hints replaced (topic changed): {'details': 'Caller selects the dental claim from last year', 'case_type': 'dental', 'status': 'closed', 'timeframe': 'November 2025', 'claim_id': 'CL-1899'} -> {'case_type': 'auto', 'status': 'open', 'claim_id': 'CL-2102', 'details': 'Asks about the status of her auto claim'}
- [turn 3] intent = status_inquiry
- [turn 3] switched to claim CL-2102
- [turn 4] caller has no further questions; moving to POST_PROCESS
- [turn 4] email summary offered
- [turn 4] caller declined the email summary up front