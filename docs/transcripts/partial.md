# partial: Partial answers, alternate ID fields, clarification questions

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: hi i need to check on a claim

AGENT: Hi, happy to help with that — I've noted you're calling about a claim and I'll pull it up as soon as we've verified who I'm speaking with.

Could you start with your full name, plus your policy number if you have it handy? I'll also need two of the following: your date of birth, the phone number or email on file, or the last four digits of your SSN.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 6.5s]

CALLER: Margaret Chen

AGENT: Thanks, Margaret. I've got your name — I just need two more items to verify you.

Any two of these will work: your date of birth, the phone number on file, the email address on file, or the last four digits of your SSN. Which would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=neutral/low facts=[] 5.9s]

CALLER: why do you need all that?

AGENT: I get it — it feels like a lot when you just want an update on your own claim.

The reason is that claim details are protected personal information, so we're required to confirm we're speaking with the policyholder before sharing anything, and that protects you from someone else getting at your file.

So I just need any two of these: your date of birth, the phone number on file, the email on file, or the last four digits of your SSN. Whichever is easiest.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants to check on a claim'} emotion=frustrated/low facts=[] 7.6s]

CALLER: ok my phone is 650-521-2836

AGENT: Thanks, Margaret — that one checks out. Just one more item and we're set: your date of birth, the email address on file, or the last four digits of your SSN, whichever is easiest.

Once that's confirmed I'll pull up the claim you're asking about right away.

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Wants to check on a claim'} emotion=neutral/low facts=[] 6.4s]

CALLER: margaret@email.com

AGENT: Perfect, that matches — thanks for bearing with me, Margaret. You're all verified.

I'm seeing a few claims on your file, so let me make sure I'm looking at the right one:

- CL-2048, healthcare, opened 2026-01-12, denied
- CL-2011, healthcare, opened 2025-01-28, closed
- CL-1899, dental, opened 2025-11-03, closed
- CL-2102, auto, opened 2026-02-28, open

Which of those did you want to check on?

    [phase=RESOLVE_INTENT verified=True claim=None hints={'details': 'Wants to check on a claim'} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 6.6s]

CALLER: the auto one

AGENT: Got it — that's CL-2102, your auto claim opened on February 28, 2026.

It's currently open, which means it's still in progress with us and hasn't reached a final decision yet. The record shows an expected reimbursement of $3,200.00, with an allowed maximum of $3,500.00, and nothing has been paid out yet.

One tip while it's in review: if you're sending in anything further, keep the repair estimate and the accident photos tied to the same incident so the reviewer can match the damage to the quote. Is there something specific about this claim I can look into for you?

    [phase=PROCESS_CASE verified=True claim=CL-2102 hints={'details': 'Caller selected the auto claim CL-2102', 'case_type': 'auto', 'status': 'open', 'claim_id': 'CL-2102'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.0s]

## Harness events

- [turn 1] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 1] intent = status_inquiry
- [turn 2] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 3] stored case hints for later: {'details': 'Caller wants to check on a claim'}
- [turn 3] verification pushback #1
- [turn 4] caller_role = policyholder
- [turn 4] stored case hints for later: {'details': 'Wants to check on a claim'}
- [turn 5] VERIFIED via ['full_name', 'phone', 'email']; party P9
- [turn 6] claim CL-2102 selected (from what the caller told you earlier)