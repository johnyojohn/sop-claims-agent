# partial: Partial answers, alternate ID fields, clarification questions

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: hi i need to check on a claim

AGENT: Hi, happy to help with that. I've noted you're calling about a claim, and I'll pull it up as soon as we get you verified.

Can I start with your full name, plus your policy number if you have it handy? Along with that, I'll need two of the following: your date of birth, the phone number or email we have on file, or the last four digits of your SSN.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 6.1s]

CALLER: Margaret Chen

AGENT: Thanks, Margaret. I have your name down. To finish up, I just need two more items from this list: your date of birth, the phone number on file, the email address on file, or the last four digits of your SSN or national ID.

Whichever two are easiest for you, go ahead.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 6.0s]

CALLER: why do you need all that?

AGENT: I get it, it feels like a lot when you just want a quick answer.

The reason is that claim details are protected personal information, so we're required to confirm we're speaking with the policyholder before sharing anything, which also keeps someone else from getting at your file. I have your name already, so I just need two more: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN. Whichever two are easiest.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=frustrated/low facts=[] 6.5s]

CALLER: ok my phone is 650-521-2836

AGENT: Thanks, Margaret, that one checks out. One last item and we're done: your date of birth, the email address on file, or the last four digits of your SSN or national ID. Whichever you prefer.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 5.5s]

CALLER: margaret@email.com

AGENT: Perfect, that matches. Thanks for bearing with me, Margaret, you're all verified.

I'm seeing a few claims on your file, so I want to make sure I'm looking at the right one:

- CL-2102, auto, opened February 28, 2026, currently open
- CL-2048, healthcare, opened January 12, 2026, denied
- CL-1899, dental, opened November 3, 2025, closed
- CL-2011, healthcare, opened January 28, 2025, closed

Which of those did you want to check on?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 6.8s]

CALLER: the auto one

AGENT: Got it, that's CL-2102, the auto claim opened February 28, 2026.

It's currently open, which means it's in progress with the review team and no payment has been issued yet. The record shows an expected reimbursement of $3,200 against an allowed maximum of $3,500, though that's an expectation rather than a final decision. Once any outstanding files are in and readable, reviews typically take less than a week, and there may be another review cycle before the status changes.

Anything else I can check for you on this one?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'details': 'Caller selected the auto claim CL-2102', 'case_type': 'auto', 'status': 'open', 'timeframe': 'February 2026', 'claim_id': 'CL-2102'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.0s]

## Checks

PASS

## Harness events

- [turn 1] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 1] intent = status_inquiry
- [turn 2] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 3] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 3] verification pushback #1
- [turn 5] caller_role = policyholder
- [turn 5] VERIFIED via ['full_name', 'phone', 'email']; party P9
- [turn 6] claim CL-2102 selected (from what the caller told you earlier)