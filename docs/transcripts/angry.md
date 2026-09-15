# angry: Bonus: frustrated caller demanding claim details before verification

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, it's Margaret Chen. I'm calling about my denied healthcare claim.

AGENT: Thanks, Margaret — I've noted that you're calling about a denied healthcare claim, and I'll pull everything up as soon as we finish verifying you.

I have your name. To get you verified I'll need two more items from this list: your date of birth, the phone number on file, the email address on file, or the last four digits of your SSN.

What would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Calling about her denied healthcare claim'} emotion=neutral/low facts=[] 6.0s]

CALLER: I already told you who I am. This is ridiculous. Just tell me why my claim was denied.

AGENT: I get it — you called about one thing and you're being asked to jump through hoops first. That's genuinely frustrating.

The reason I can't skip it is that claim details are protected personal information, so I'm required to confirm I'm speaking with the policyholder before I share anything — that protection works in your favor too.

Two quick items and we're done: your date of birth, the phone number on file, the email on file, or the last four of your SSN. Whichever two are easiest.

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Caller wants to know why her healthcare claim was denied'} emotion=frustrated/high facts=[] 7.3s]

CALLER: Fine. Born March 15 1985, last four of my social is 4472.

AGENT: Thank you, Margaret — that matches, so you're all set.

I have claim CL-2048, your healthcare claim opened on January 12, 2026, and it does show as denied. The reason given is that the review file did not include the pathology report or the treating provider office note — so it wasn't a coverage decision, just missing paperwork.

To get it reconsidered, the two documents needed are the pathology report and the office note. The best way to send them is through the member portal or your claim upload link so they stay attached to the file; if online upload isn't an option, I can help arrange fax or mail. One thing I do want to flag: the appeal deadline on file is March 18, 2026, which has passed, so I'd like a claims representative to review your options before you spend time gathering records.

Would you like me to walk you through exactly what each document needs to show, or set up that representative follow-up first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Denied healthcare claim; wants to know why'} emotion=frustrated/medium facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.0s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': 'Calling about her denied healthcare claim'}
- [turn 1] intent = denial_question
- [turn 2] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': 'Caller wants to know why her healthcare claim was denied'}
- [turn 2] verification pushback #1
- [turn 3] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': 'Denied healthcare claim; wants to know why'}
- [turn 3] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9
- [turn 3] claim CL-2048 selected (from what the caller told you earlier)