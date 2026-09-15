# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I've pulled up claim CL-2048, the healthcare claim opened January 12, 2026, and it does show as denied.

The reason on file is that the review file didn't include the pathology report or the treating provider office note. To reopen it, we'd need both of those: the pathology report showing patient name, specimen details, testing date and the lab or clinician signature, and the office note showing patient name, visit date, assessment and the treatment or follow-up recommendation, with all pages together in one PDF if possible. The easiest way to send them is through the member portal or the claim upload link so they stay attached to the file; if online upload isn't an option, I can help arrange fax or mail.

One thing I want to be straight with you about: the appeal deadline on this claim is listed as March 18, 2026, which has already passed. I don't have detail on what options remain after that date, so I'd like to have a claims representative follow up with you on it. Would that work?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 11.1s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents, Margaret.

First, the pathology report. It should show the patient name, specimen details, the testing date, and the clinician or lab signature if there is one. A high-quality scan is fine as long as the report is complete and fully readable; if the plan requires the original, the portal instructions or our support team can confirm the mailing address.

Second, the treating provider office note. That one needs the patient name, visit date, the assessment, and the treatment or follow-up recommendation. Please upload all pages together in one PDF if you can. For medical claims it helps to have the treating provider or facility name visible on each page.

For how to send them: start with the member portal or the claim upload link so they attach directly to CL-2048. If uploading isn't possible, let me know and we can arrange fax or mail instead. Once the files are received and readable, the claim goes back into review rather than being decided instantly, and processing is usually less than a week, though intake and another review cycle can add a little time. If anything is unclear or incomplete, the team may come back to you for more.

If the lab or clinic can't reissue either document, tell me and we'll look at alternatives. Anything else I can help you with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking what documents to send and how to submit them for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 11.8s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, start by asking them for a complete visit summary, discharge paperwork, or a re-sent copy of the chart for that visit. Any of those can work as long as it ties back to the same treatment and shows the visit details.

It's also worth asking whether the clinic can fax or upload the note directly to us. That's often the cleanest route, since it avoids the back-and-forth entirely.

If none of that pans out, that's when I'd have a claims representative review the file with you to see what other clinical records might be acceptable. Want me to set that follow-up up now, or would you rather check with the clinic first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the office note', 'claim_id': 'CL-2048'} emotion=confused/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.6s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being decided on the spot. The average processing time after submission is usually less than a week, though intake and another review cycle can add a bit of time, and if either document is incomplete or hard to read the team may come back to you for more before reconsidering the denial.

One thing to expect: there's often a short intake delay before the status updates on your end. If the claim still looks unchanged after a few business days, call back and we can confirm the pathology report and office note were attached correctly.

And I'd still like to get that representative follow-up going about the March 18 appeal deadline, since it's already passed and I don't have detail on the options after that date. Shall I put that in now?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long until a response after sending documents', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.5s]

CALLER: No, that's everything, thanks.

AGENT: Sounds good, Margaret. Would you like me to email you a summary of what we covered today, including the claim status and the next steps on those two documents? I can send it to the address on file, which ends in m*******@email.com, or to a different address if you'd prefer, or we can skip it entirely.

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long until a response after sending documents', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.2s]

CALLER: Yes please, send it to johanjohnsjo@gmail.com

AGENT: I'm sorry, Margaret, that summary didn't go through to johanjohnsjo@gmail.com. A representative will make sure you receive it.

Take care, and good luck getting those documents together.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller sending pathology report and office note for denied claim review', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 36.1s]

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'}
- [turn 1] intent = denial_question
- [turn 1] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9
- [turn 1] claim CL-2048 selected (from what the caller told you earlier)
- [turn 2] intent = document_submission
- [turn 4] intent = next_steps
- [turn 5] caller has no further questions; moving to POST_PROCESS
- [turn 5] email summary offered
- [turn 6] summary email -> johanjohnsjo@gmail.com (failed)