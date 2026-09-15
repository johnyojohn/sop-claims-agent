# partial: Partial answers, alternate ID fields, clarification questions

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: hi i need to check on a claim

AGENT: Hi, happy to help with that, and I have noted you want to check on a claim so I can pull it up as soon as we finish verifying you.

To start, could you give me your full name, plus your policy number if you have it handy? I'll also need two more details from this list: your date of birth, the phone number or email on file, or the last four digits of your SSN.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 6.4s]

CALLER: Margaret Chen

AGENT: Thanks, Margaret. I have your name. Could you give me your date of birth next?

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 5.3s]

CALLER: why do you need all that?

AGENT: I hear you, it's annoying to go through this when you just want an update.

The reason is that claim details are protected personal information, so we're required to confirm we're speaking with the policyholder before we share anything, which also keeps someone else from getting at your file.

I just need two more items, and you can pick whichever are easiest: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=frustrated/low facts=[] 6.3s]

CALLER: ok my phone is 650-521-2836

AGENT: Thanks, that one matches. Just one more item and we're set: your date of birth, the email on file, or the last four digits of your SSN, whichever is easiest.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 5.1s]

CALLER: margaret@email.com

AGENT: That matches too, so you're all verified. Thanks for bearing with me, Margaret.

I have four claims on your file, so let me know which one you mean:

- CL-2102, auto, opened 2026-02-28, currently open
- CL-2048, healthcare, opened 2026-01-12, denied
- CL-1899, dental, opened 2025-11-03, closed
- CL-2011, healthcare, opened 2025-01-28, closed

Which one would you like to check on?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 7.6s]

CALLER: the auto one

AGENT: I have CL-2102 pulled up, the auto claim opened on 2026-02-28.

It's currently open, which means it's still in progress and no payment has been finalized yet, the net paid amount is showing 0.00. The expected reimbursement on file is 3,200.00, against an allowed maximum of 3,500.00.

One thing worth knowing for auto claims: keep the repair estimate and the accident photos tied to the same incident, so the reviewer can match the visible damage to the quote. Once documents are received and readable, processing is usually less than a week.

Is there anything else I can check for you on this one?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'details': 'Caller selected the auto claim CL-2102', 'case_type': 'auto', 'status': 'open', 'claim_id': 'CL-2102'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 7.7s]

## Checks

PASS

## Harness events

- [turn 1] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 1] intent = status_inquiry
- [turn 2] caller_role = policyholder
- [turn 2] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 3] verification pushback #1
- [turn 5] VERIFIED via ['full_name', 'phone', 'email']; party P9
- [turn 6] claim CL-2102 selected (from what the caller told you earlier)