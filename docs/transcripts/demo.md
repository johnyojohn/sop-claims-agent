# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I have claim CL-2048, your healthcare claim opened on January 12, 2026, which is showing as denied.

The denial came down to missing paperwork: the review file did not include the pathology report or the treating provider office note. Once those two are in, the claim can go back into review.

The easiest way to send them is through the member portal or the claim upload link so they stay attached to the file, and if online upload isn't an option, we can arrange fax or mail. Please keep an eye on the appeal deadline of March 18, 2026.

Would it help if I walk you through exactly what each of those two documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.1s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents, Margaret.

First, the pathology report. It needs to show your name as the patient, the specimen details, the testing date, and the clinician or lab signature if there is one. A high-quality scan is fine as long as the report is complete and fully readable. If your plan happens to require the original, the portal instructions or our support team can confirm a mailing address.

Second, the office note from your treating provider. It should show your name, the visit date, the assessment, and the treatment or follow-up recommendation. Please upload all pages together in one PDF if you can. For medical claims it also helps to have the treating provider or facility name visible on each page.

For submission, start with the member portal or your claim upload link so both files stay attached to CL-2048. If you can't upload, we can set up fax or mail instead, and the provider's office can often fax the records directly, which is usually the cleanest route.

After they come in, the claim goes back into review rather than resolving instantly. Processing is usually less than a week, though intake and another review cycle can add a little time, and if anything is unclear the team may come back to you for more. There can also be a short delay before the status updates, so if it still looks unchanged after a few business days, call us and we'll confirm the files attached correctly. I'd aim to get them in within a week, well ahead of the March 18 appeal deadline.

Does that cover what you needed, or would you like help with the submission method?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim; asking what documents to send and how', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 11.6s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, start by asking them for a complete visit summary, any discharge paperwork, or a re-sent copy of your chart, since those often carry the same details. If they can fax or upload the note or records directly to us, that's usually the cleanest route.

If none of that pans out, I can have a claims representative review the file with you to see what other clinical records might be acceptable. Would you like me to set that up now, or check with the clinic first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the office note needed for the denied claim', 'claim_id': 'CL-2048'} emotion=confused/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.0s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being decided on the spot. The average processing time is usually less than a week, though intake and another review cycle can add a bit, and if either document is incomplete or hard to read the team may come back to you for more before reconsidering the denial.

There can also be a short lag before the status updates on your end, so if it still looks unchanged after a few business days, give us a call and we'll confirm the pathology report and office note were attached correctly.

Anything else I can help you with today?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long after sending documents until she hears back', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.6s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can email you a summary of what we covered today, including the claim status and the next steps with those two documents.

I can send it to the address on file, m*******@email.com, or to a different address if you'd rather, or skip it entirely. Which would you prefer?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied medical claim; caller submitting pathology report and office note for reconsideration', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.1s]

CALLER: Yes, the one on file is fine.

AGENT: Done, I've queued that summary to your email on file at margaret@email.com. It covers what we discussed today, the two documents needed, and the next steps for CL-2048.

Take care, Margaret, and good luck getting those records together.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied claim; needs pathology report and office note submitted for reconsideration', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 22.1s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'}
- [turn 1] intent = denial_question
- [turn 1] VERIFIED via ['full_name', 'dob', 'id_last4']; party P9
- [turn 1] claim CL-2048 selected (from what the caller told you earlier)
- [turn 2] intent = document_submission
- [turn 5] caller has no further questions; moving to POST_PROCESS
- [turn 5] email summary offered
- [turn 6] summary email -> margaret@email.com (mock)

## Email

To: margaret@email.com (mock)
Subject: Claim CL-2048 - Documents needed and next steps

Hi Margaret,

Thank you for calling Northwind Insurance today. We reviewed your denied healthcare claim, the two documents needed to reopen it, and how to send them in.

Claim status / outcome
Claim ID: CL-2048
Type: Healthcare (opened January 12, 2026)
Status: Denied
The denial was because the review file did not include the pathology report or the treating provider office note. Once both are received, the claim goes back into review. The appeal deadline is March 18, 2026.

Next steps
1. Send the pathology report showing your name as the patient, specimen details, testing date, and the clinician or lab signature if one exists. A high-quality scan is fine if the report is complete and fully readable; if your plan requires the original, the portal instructions or our support team can confirm a mailing address.
2. Send the treating provider office note showing your name, visit date, assessment, and the treatment or follow-up recommendation. Upload all pages together in one PDF if possible, with the provider or facility name visible on each page.
3. Submit through the member portal or your claim upload link so both files stay attached to CL-2048. If online upload is not available, we can arrange fax or mail, and your provider's office can often fax records directly.
4. Aim to submit within a week, well ahead of the March 18, 2026 appeal deadline.
5. If the clinic cannot locate the office note, ask for a complete visit summary, discharge paperwork, or a re-sent copy of your chart. If none are available, a claims representative can review other options with you.
6. Processing after submission is usually less than a week, though intake and another review cycle can add time. If the status looks unchanged after a few business days, call us and we will confirm the files attached correctly.

If you have any questions, reply to this email or call the claims line.

Ava
Northwind Insurance Claims Support