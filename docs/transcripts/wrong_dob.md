# wrong_dob: Mismatched field, then correction; a policy number is lookup-only

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Margaret Chen, policy POL-9921, DOB 1985-03-16, last four 4472.

AGENT: Thanks, Margaret, I've got the policy number and the last four you gave me. The date of birth isn't matching what I have here, though, so could you double-check it for me? If you'd rather, we can use the phone number or email address on file instead.

    [phase=VERIFY_ID verified=False claim=None hints={} emotion=neutral/low facts=[] 6.1s]

CALLER: Oh sorry, it's the 15th, 1985-03-15.

AGENT: That's a match, thank you. Verification is all set.

I'm seeing a few claims on your policy, so let me make sure I pull up the right one:

- CL-2102, auto, opened 2026-02-28, currently open
- CL-2048, healthcare, opened 2026-01-12, denied
- CL-1899, dental, opened 2025-11-03, closed
- CL-2011, healthcare, opened 2025-01-28, closed

Which of those would you like to go over?

    [phase=RESOLVE_INTENT verified=True claim=None hints={} emotion=neutral/low facts=['claims_on_file', 'matching_claims'] 6.8s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] mismatch on ['dob'] (attempt 1)
- [turn 2] identity.dob updated by caller
- [turn 2] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9