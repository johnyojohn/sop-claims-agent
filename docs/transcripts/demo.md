# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I have claim CL-2048, your healthcare claim opened on January 12, 2026, and it is showing as denied.

The denial came down to missing paperwork: the review file did not include the pathology report or the treating provider office note. Once those two are in, the claim can go back into review.

The easiest way to send them is through the member portal or your claim upload link so they stay attached to the file, and if online upload isn't an option, we can arrange fax or mail. Please note the appeal deadline is March 18, 2026, so sooner is better, ideally within the next week.

Would it help if I walked you through exactly what each of those two documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.7s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents, Margaret.

The pathology report should show the patient name, specimen details, the testing date, and the clinician or lab signature if there is one. A high quality scan works as long as the report is complete and fully readable. If your plan requires the original, the portal instructions or our support team can confirm the mailing address.

The office note from your treating provider should show the patient name, visit date, the assessment, and the treatment or follow-up recommendation. Send all pages together in one PDF if you can.

For both, make sure each page is legible and complete, with the claim details, dates, and the treating provider or facility name visible where possible. Upload them through the member portal or your claim upload link first; if that isn't available, I can help arrange fax or mail.

After they come in, the claim goes back into review rather than being decided instantly. Processing is usually less than a week, though intake and another review cycle can add time, and if anything is unclear the team may come back to you for more. There can also be a short delay before the status updates, so if nothing has changed after a few business days, call us and we will confirm the files attached correctly.

Anything else I can help you with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller asks what documents to send and how to submit them for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 10.4s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, start by asking them for a complete visit summary, discharge paperwork, or a re-sent copy of the chart, any of those can work as a substitute. It often goes smoothest if the provider faxes or uploads the note directly to us.

If none of that is available, then a claims representative can review your file with you and look at what other clinical records might be acceptable. I can set that up for you if it comes to that.

Does the clinic think the note is truly lost, or just slow to get to you?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the office note needed for the denied claim', 'claim_id': 'CL-2048'} emotion=anxious/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 7.6s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being finalized right away. The average processing time is usually less than a week, though intake and another review cycle can add some time before the status updates.

If anything in the pathology report or office note is incomplete or hard to read, the team may come back to you for more information before reconsidering the denial. And if the claim still looks unchanged after a few business days, give us a call and we can check that both documents attached to the file correctly.

Just keep the March 18 appeal deadline in mind, that's the date to have things submitted by. Anything else I can help with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long until a response after submitting the missing documents', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.3s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can email you a summary of today's conversation, what we covered, the claim status, and the next steps with those two documents.

I can send it to the address on file ending in m*******@email.com, or to a different address if you'd rather, or skip it entirely. Which would you prefer?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied claim; caller submitting pathology report and office note for appeal', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.6s]

CALLER: Yes please, send it to johanjohnsjo@gmail.com

AGENT: All set, Margaret. The summary is queued and on its way to johanjohnsjo@gmail.com, and it covers what we discussed today along with the next steps for those two documents.

Best of luck getting everything together, and take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied claim; needs pathology report and office note submitted before March 18 appeal deadline', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 29.8s]

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
- [turn 6] summary email -> johanjohnsjo@gmail.com (mock)

## Email

To: johanjohnsjo@gmail.com (mock)
Subject: Your Northwind Claim CL-2048 - Summary and Next Steps

Hi Margaret,

Thanks for calling Northwind Insurance claims support today. We reviewed your denied healthcare claim, the two documents needed to reopen the review, how to send them, and what to expect afterward.

Claim status / outcome
Claim ID: CL-2048
Type: Healthcare (opened January 12, 2026)
Status: Denied
The denial was because the review file did not include the pathology report or the treating provider office note. Once both are received, the claim goes back into review. The appeal deadline is March 18, 2026. Average processing time after submission is usually less than a week, though intake and another review cycle can add time.

Next steps
1. Send the pathology report showing the patient name, specimen details, testing date, and clinician or lab signature if one exists. A high-quality scan is acceptable if complete and fully readable; if your plan requires the original, the portal instructions or our support team can confirm the mailing address.
2. Send the treating provider office note showing patient name, visit date, assessment, and treatment or follow-up recommendation, with all pages together in one PDF if possible.
3. Upload both through the member portal or your claim upload link; if that is not available, we can arrange fax or mail.
4. Submit within the next week, and by the March 18, 2026 appeal deadline.
5. If the clinic cannot find the office note, ask for a complete visit summary, discharge paperwork, or a re-sent copy of the chart. If none are available, a claims representative can review other options with you.
6. If the status looks unchanged after a few business days, call us and we will confirm both documents attached correctly.

You can reply to this email or call the claims line if you have any questions.

Ava
Northwind Insurance Claims Support