# wrong_dob: Mismatched field, then correction; a policy number is lookup-only

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Margaret Chen, policy POL-9921, DOB 1985-03-16, last four 4472.

AGENT: Thanks, Margaret. The policy number helps me locate the account, but the date of birth you gave doesn't match what we have on file, so I can't count it toward verification.

Could you double-check the date of birth for me? If it's easier, I can instead use the phone number or email address on file as your second matching item.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.7s]

CALLER: Oh sorry, it's the 15th, 1985-03-15.

AGENT: That one matches, thank you. You're verified.

I've got a few claims on your account, so let me make sure I'm looking at the right one:

- CL-2048, healthcare, opened 2026-01-12, denied
- CL-2011, healthcare, opened 2025-01-28, closed
- CL-1899, dental, opened 2025-11-03, closed
- CL-2102, auto, opened 2026-02-28, open

Which of those did you want to go over?

    [phase=RESOLVE_INTENT verified=True claim=None hints={} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 6.0s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] mismatch on ['dob'] (attempt 1)
- [turn 2] identity.dob updated by caller
- [turn 2] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9