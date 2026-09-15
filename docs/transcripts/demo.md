# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I have claim CL-2048 pulled up, the healthcare claim opened on January 12, and it is showing as denied.

The denial came down because the review file did not include the pathology report and the treating provider office note. If you can get those two documents to us, the claim can go back into review, and the appeal deadline is March 18, 2026.

The easiest way to send them is through the member portal or the claim upload link so they stay attached to this claim, and if online upload isn't an option for you, we can arrange fax or mail instead. Would it help if I walked you through what each of those two documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.3s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Two documents, Margaret.

The pathology report should show the patient name, specimen details, the testing date, and the clinician or lab signature if there is one. A high quality scan works as long as the report is complete and fully readable. If your plan happens to require the original, the portal instructions or our team can confirm the mailing address.

The office note from the treating provider should show the patient name, visit date, the assessment, and the treatment or follow-up recommendation. Please send all pages together in one PDF if you can.

For both, make sure every page is legible and complete, with the treating provider or facility name visible where possible, along with the relevant dates. Upload them through the member portal or your claim upload link so they attach directly to CL-2048. If that doesn't work for you, I can help set up fax or mail.

Once we have them, the claim goes back into review rather than being decided on the spot. Processing is usually less than a week, though intake and another review cycle can add a little time, and if anything is unclear the team may come back to you for more. Aim to get them in within the week so you're comfortably ahead of the March 18 appeal deadline.

Does that cover what you needed, or would you like help with the submission method?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller asks what documents to send and how to submit them for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 10.1s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, ask them for a complete visit summary or your discharge paperwork, or have them re-send a copy of the chart from your record. Any of those can work as a stand-in as long as it ties back to the same visit and shows the patient name, visit date, assessment, and the treatment or follow-up recommendation.

It's often cleanest if the clinic faxes or uploads the note to us directly, so it's worth asking whether they can do that on their end.

If none of that is available, then a claims representative can review your file with you and look at what other clinical records might be acceptable. Would you like me to set that follow-up up now, or would you rather check with the clinic first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the treating provider office note', 'claim_id': 'CL-2048'} emotion=anxious/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.7s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being finalised right away. The average processing time is usually less than a week, though intake and another review cycle can add some time before the status updates.

One thing to expect: there can be a short intake delay before the claim reflects the upload at all. If it still looks unchanged after a few business days, call back and we can confirm the pathology report and office note were attached correctly. And if either document is incomplete or hard to read, the team may come back to you for more before reconsidering the denial.

Given the March 18 appeal deadline, sending them within the week gives you a comfortable buffer. Anything else I can help you with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January; asking turnaround time after sending documents', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.2s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can email you a summary of today's conversation, what we discussed, the current status of the claim, and the next steps, so you have it all in writing.

I can send it to the address on file ending in m*******@email.com, or to a different address if you prefer, or we can skip it entirely. Which would you like?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller finished asking about submitting pathology report and office note for denied claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.3s]

CALLER: Yes please, send it to johanjohnsjo@gmail.com

AGENT: Sorry about this, Margaret, the summary didn't go through to johanjohnsjo@gmail.com. A representative will make sure you get it.

Best of luck with the documents, and take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller sending pathology report and office note for denied claim; March 18 appeal deadline', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 29.7s]

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