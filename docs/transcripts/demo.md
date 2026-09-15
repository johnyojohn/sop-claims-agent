# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks Margaret, you're all verified.

I have claim CL-2048 pulled up, the healthcare claim opened on 2026-01-12, and it does show as denied. The denial came down because the review file did not include the pathology report and the treating provider office note.

To get it reconsidered, we need those two documents. The pathology report should show the patient name, specimen details, testing date, and the clinician or lab signature if there is one. The office note should show the patient name, visit date, assessment, and the treatment or follow-up recommendation, ideally all pages together in one PDF. Your best route is the member portal or the claim upload link so they attach straight to the file, and if online upload is not an option we can help arrange fax or mail.

One important date: your appeal deadline is 2026-03-18, so the sooner those come in the better. Would it help if I walked you through what to do if the provider cannot get you either document?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 10.0s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents for claim CL-2048, Margaret.

First, the pathology report. It needs the patient name, specimen details, the testing date, and the clinician or lab signature if one exists. A high quality scan works as long as the report is complete and fully readable. If your plan requires the original, the portal instructions or our team can confirm the mailing address.

Second, the treating provider office note. It needs the patient name, visit date, the assessment, and the treatment or follow-up recommendation. Send all pages together in one PDF if you can.

For both, make sure each page is legible and complete, with the treating provider or facility name visible where possible. Upload them through the member portal or the claim upload link so they stay attached to the claim. If you can't upload online, we can arrange fax or mail.

After they come in, the claim goes back into review. That usually takes less than a week, though there can be a short intake delay before the status updates, and the team may come back to you if anything is unclear. Try to get them in within about a week, and keep the 2026-03-18 appeal deadline in mind.

Anything else I can help with, or would you like to know what to do if the provider can't produce one of these?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller asks what documents to send and how to submit them for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 10.1s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the office note, ask them for a complete visit summary, discharge paperwork, or a re-sent copy of the chart, any of those can stand in for the same visit. It often goes smoothest if the clinic faxes or uploads the record directly to us rather than routing it through you.

If none of that is available, then a human claims representative should look at your file and go over what other clinical records might be acceptable. I can get that started for you if the clinic comes back empty handed.

Would you like me to do that now, or would you rather check with them first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the provider office note', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.9s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being decided on the spot. The average processing time is usually less than a week, though intake and another review cycle can add a bit of time before the status changes. And if either document comes in incomplete or hard to read, the team may come back to you for more before reconsidering the denial.

One thing to expect: there can be a short intake delay before the portal reflects the upload. If the claim still looks unchanged after a few business days, give us a call and we can confirm the pathology report and office note were attached correctly.

Anything else I can help you with today?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long until response after sending documents for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 7.3s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can send you an email summary of today's chat, what we discussed, the denial status on claim CL-2048, and the next steps with the two documents and your deadline.

I can send it to the address on file, m*******@email.com, or to a different address if you prefer, or we can skip it entirely. Which would you like?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller has nothing further after document submission guidance.', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.6s]

CALLER: Yes please, send it to johanjohnsjo@gmail.com

AGENT: I'm sorry, that summary didn't go through to johanjohnsjo@gmail.com, the delivery failed on our end.

A representative will make sure you receive it, so you don't need to do anything further. Take care, Margaret, and good luck getting those documents together.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied claim; needs pathology report and office note submitted', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 29.8s]

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