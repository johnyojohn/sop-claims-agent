# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I've got claim CL-2048, your healthcare claim opened January 12, 2026, and it does show as denied.

The denial came down to missing paperwork rather than coverage: the review file didn't include the pathology report or the treating provider's office note. If you can get those two documents to us, the claim can go back into review, and the appeal deadline is March 18, 2026. The easiest way to send them is through the member portal or your claim upload link so they stay attached to the file, and if online upload isn't an option we can arrange fax or mail.

Would you like me to walk through exactly what each of those documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.7s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents, Margaret. The pathology report needs to show your name, the specimen details, the testing date, and the clinician or lab signature if there is one. A high-quality scan works as long as the report is complete and fully readable; if your plan requires the original, the portal instructions or our support team can confirm the mailing address. The office note needs your name, the visit date, the assessment, and the treatment or follow-up recommendation, and it's best to upload all pages together as one PDF.

For both, keep every page legible and complete, with the treating provider or facility name showing where possible. Upload them through the member portal or your claim upload link so they attach straight to CL-2048, or tell me if you'd rather fax or mail and I'll help set that up. Once they're received the claim goes back into review, usually less than a week, though intake and another review cycle can add a little time, and try to send them within the week to stay well ahead of the March 18 deadline.

Anything else I can help with while we're here?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January; asking what documents to send and how', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.7s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, ask them for a complete visit summary, discharge paperwork, or a re-sent copy of the chart, any of those can work as the closest supporting record. It also helps to ask whether they can fax or upload it to us directly, which is often the cleanest route.

If none of that turns up, let me know and a claims representative can review your file and go over what other clinical records might be acceptable. Would you like me to note that on the claim now?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the office note needed for the denied claim', 'claim_id': 'CL-2048'} emotion=anxious/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 6.9s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have the files, the review generally restarts rather than finishing instantly. The average processing time is usually less than a week, though intake plus another review cycle can add a bit, and if either document is incomplete or unclear the team may come back to you for more before reconsidering the denial.

One thing to expect: there can be a short intake delay before the status updates on your end. If the claim still looks unchanged after a few business days, call us and we can check whether the pathology report and office note attached correctly.

Is there anything else I can help you with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long until a response after sending required documents', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 7.3s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can email you a summary of what we covered today, the claim status, and the next steps for sending in those two documents.

I can send it to the address on file, m*******@email.com, or to a different address if you'd rather, or skip it entirely. Which would you prefer?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller wrapping up after discussing documents for denied claim CL-2048', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 7.2s]

CALLER: Yes, the one on file is fine.

AGENT: All set, Margaret, the summary is on its way to margaret@email.com. It covers what we went over today and the next steps for getting those two documents to us.

Best of luck with the clinic, and take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller sending pathology report and office note to support reconsideration of denied claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 16.4s]

## Checks

PASS

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
- [turn 6] summary email -> margaret@email.com (smtp)

## Email

To: margaret@email.com (smtp)
Subject: Claim CL-2048 - Next steps for your denied healthcare claim

Hi Margaret,

Thanks for calling Northwind Insurance today. We reviewed your denied healthcare claim, what the denial was based on, the two documents needed to reopen the review, and how to send them.

Claim status / outcome
Claim ID: CL-2048
Type: Healthcare (opened January 12, 2026)
Status: Denied
The denial was due to missing paperwork rather than coverage: the review file did not include the pathology report or the treating provider office note. The appeal deadline is March 18, 2026. Once the documents are received, the claim goes back into review, usually less than a week, though intake and another review cycle can add time.

Next steps
1. Send the pathology report showing your name, specimen details, testing date, and the clinician or lab signature if one exists. A high-quality scan is acceptable if complete and fully readable; if your plan requires the original, the portal instructions or our support team can confirm the mailing address.
2. Send the office note showing your name, visit date, assessment, and treatment or follow-up recommendation, with all pages uploaded together as one PDF.
3. Upload both through the member portal or your claim upload link so they attach to CL-2048. If online upload is not an option, we can arrange fax or mail.
4. Aim to submit within a week to stay ahead of the March 18, 2026 deadline.
5. If the clinic cannot locate the office note, ask for a complete visit summary, discharge paperwork, or a re-sent copy of the chart, or have them fax or upload it directly. If none is available, let us know and a claims representative can review other acceptable clinical records.
6. If the claim status still looks unchanged after a few business days, contact us and we can confirm the documents attached correctly.

If you have any questions, reply to this email or call the claims line.

Ava
Northwind Insurance Claims Support