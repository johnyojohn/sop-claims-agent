# demo: Assessment demo case: identity + early case hint, memory across phases, grounded answers, email

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: I'm the policyholder. My name is Margaret Chen, policy POL-9921. I'm calling about my denied healthcare claim from January. DOB is 1985-03-15, SSN last four is 4472.

AGENT: Thanks, Margaret, you're all verified. I have claim CL-2048 pulled up, the healthcare claim opened on 2026-01-12, and it does show as denied.

The denial came down to missing paperwork rather than anything about the treatment itself: the review file did not include the pathology report or the treating provider office note. If you can get those two documents to us, the claim goes back into review.

The easiest way to send them is through the member portal or the claim upload link so they stay attached to the file. If uploading isn't an option, we can help set up fax or mail instead. Your appeal deadline is 2026-03-18, so ideally within the next week or so.

Would it help if I walk you through exactly what each of those two documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied healthcare claim from January'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.0s]

CALLER: So what exactly do I need to send you, and how?

AGENT: Sure, here's exactly what we need for CL-2048.

The pathology report should show the patient name, specimen details, testing date, and the clinician or lab signature if there is one. A high-quality scan is fine as long as the report is complete and fully readable. If your plan requires the original, the portal instructions or our support team can confirm the mailing address.

The office note from the treating provider should show the patient name, visit date, assessment, and the treatment or follow-up recommendation. Please send all pages together in one PDF if you can. For medical claims like this, it helps if the treating provider or facility name is visible on each page.

For submission, start with the member portal or the claim upload link so the files stay attached to the claim. If online upload isn't available to you, let me know and we can arrange fax or mail. Either way, each file should be legible and complete with the claim details, dates, and provider visible.

After you send them, the claim goes back into review rather than updating instantly. Processing is usually less than a week, though intake plus another review cycle can add a little time, and if anything is unclear the team may come back to you for more. If the status still looks unchanged after a few business days, call us and we can confirm the files attached correctly.

Anything else I can help you with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what documents to send and how to submit them for denied healthcare claim', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 10.6s]

CALLER: What if the clinic can't find the office note?

AGENT: If the clinic can't locate the full office note, start by asking them for a complete visit summary, discharge paperwork, or a re-sent copy of the chart for that visit, any of those can often carry the same information. It's also worth asking whether they can fax or upload the note to us directly, which is usually the cleanest route since it skips you having to chase a copy.

If none of that pans out, let me know and I'll have a claims representative review your file to see what other clinical records might be acceptable in its place.

Would you like me to note that on the claim now, or would you rather check with the clinic first?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asks what to do if clinic cannot locate the office note needed for resubmission', 'claim_id': 'CL-2048'} emotion=anxious/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.7s]

CALLER: How long after I send it will I hear back?

AGENT: Once we have both files, the claim goes back into review rather than being decided on the spot. The average processing time after submission is usually less than a week, though intake and another review cycle can add a bit of time before the status is actually updated. If the pathology report or office note comes in incomplete or hard to read, the team may come back to you for more information before reconsidering the denial.

One thing to keep in mind: there can be a short intake delay before anything shows on your end, so if the claim still looks unchanged after a few business days, give us a call and we'll confirm the documents attached correctly. And do try to get them in well before the 2026-03-18 appeal deadline.

Anything else I can help with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Asking how long after submitting documents until she hears back', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.3s]

CALLER: No, that's everything, thanks.

AGENT: Happy to help, Margaret. Before you go, I can email you a summary of what we covered today, the claim status, and the next steps so you have it in writing. I can send it to the address on file ending in m*******@email.com, or to a different address if you'd rather, or skip it entirely. Which would you prefer?

    [phase=POST_PROCESS verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Caller has no further questions after document submission guidance', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 6.4s]

CALLER: Yes, the one on file is fine.

AGENT: That's on its way to margaret@email.com now, subject line "Your Northwind Claim CL-2048 - Next Steps." It covers what we discussed today and the next steps, so you'll have it all in writing.

Best of luck getting those documents together, Margaret, and take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'timeframe': 'January', 'details': 'Denied claim needing pathology report and office note submitted before appeal deadline', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['email_summary'] 15.8s]

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
Subject: Your Northwind Claim CL-2048 - Next Steps

Hi Margaret,

Thanks for calling today. We reviewed your denied healthcare claim, the two documents needed to reopen the review, how to send them, and what to expect afterward.

Claim status / outcome
Claim ID: CL-2048
Type: Healthcare (opened 2026-01-12)
Status: Denied
The denial was due to missing paperwork, not the treatment itself. The review file did not include the pathology report or the treating provider office note. Your appeal deadline is 2026-03-18, and we recommend submitting within the next week or so.

Next steps
1. Send the pathology report showing patient name, specimen details, testing date, and the clinician or lab signature if one exists. A high-quality scan is fine if complete and fully readable; if your plan requires the original, the portal instructions or our team can confirm the mailing address.
2. Send the treating provider office note showing patient name, visit date, assessment, and treatment or follow-up recommendation, with all pages in one PDF and the provider or facility name visible on each page.
3. Upload both through the member portal or claim upload link so they stay attached to the claim. If uploading is not available, contact us and we can arrange fax or mail.
4. If the clinic cannot locate the office note, ask for a complete visit summary, discharge paperwork, or a re-sent chart copy, or have them fax or upload it directly. If none of that works, let us know and a claims representative will review other options.
5. After submission, review usually takes less than a week, though intake and another review cycle can add time. If the status looks unchanged after a few business days, call us to confirm the files attached correctly.

If you have any questions, reply to this email or call the claims line.

Ava
Northwind Insurance Claims Support