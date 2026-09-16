# wrong_dob: Mismatched field, then correction; a policy number is lookup-only

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Margaret Chen, policy POL-9921, DOB 1985-03-16, last four 4472.

AGENT: Thanks, Margaret. The date of birth you gave isn't matching what I have, so I can't count it toward verification. Could you double-check it for me, or if you'd rather, give me the phone number or email address on file instead?

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.3s]

CALLER: Oh sorry, it's the 15th, 1985-03-15.

AGENT: Perfect, that matches. Thanks for bearing with me, Margaret.

I've got four claims on file, so tell me which one you're calling about: CL-2048, a healthcare claim from January 12, 2026, currently denied; CL-2011, a healthcare claim from January 28, 2025, closed; CL-1899, a dental claim from November 3, 2025, closed; and CL-2102, an auto claim from February 28, 2026, still open. Which one would you like to go over?

    [phase=RESOLVE_INTENT verified=True claim=None hints={} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 7.0s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] mismatch on ['dob'] (attempt 1)
- [turn 2] identity.dob updated by caller
- [turn 2] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9