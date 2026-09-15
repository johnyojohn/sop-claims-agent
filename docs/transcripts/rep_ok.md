# rep_ok: Representative: named on file + 3 policyholder items + consent (default scenario approves on the second check)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, I'm David Chen calling for my mother Margaret Chen about her denied healthcare claim.

AGENT: Thanks for reaching out, David. I've noted that you're calling about a healthcare claim denial for your mother, and I'll pull that up as soon as we get through verification.

Since you're calling on her behalf, I'll need a couple more details about your mother before I can send her a consent request. Could you give me her date of birth to start?

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's healthcare claim was denied"} emotion=neutral/low facts=[] 6.0s]

CALLER: Sure, I'm her son. Her date of birth is March 15, 1985 and the last four of her SSN are 4472.

AGENT: Thank you, David. You're listed on file as Margaret's son, so I've gone ahead and sent a consent request to her using the contact details we have on file. Once she approves it, I can go through the claim with you in full.

She usually responds within a minute or two, so just let me know when you'd like me to check on it.

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"} emotion=neutral/low facts=[] 7.7s]

CALLER: Ok, can you check if she approved it?

AGENT: I just checked and the approval hasn't come through yet. I'm happy to check again in a moment, these sometimes take a few minutes to land on her end. Just say the word and I'll refresh it.

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"} emotion=neutral/low facts=[] 6.8s]

CALLER: And now?

AGENT: Good news, her consent just came through, so you're verified as her authorised representative and I can go through everything with you.

The claim I have up is CL-2048, a healthcare claim opened on 12 January 2026, and it's currently denied. The reason is that the review file did not include the pathology report and the treating provider office note.

To appeal, you'd need to send in those two documents, the pathology report and the office note, by 18 March 2026. The easiest route is the member portal or the claim upload link so they stay attached to the file, and if online upload isn't an option, we can help arrange fax or mail.

Would you like me to walk you through what each of those documents needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.4s]

CALLER: Great. So what documents does she need to send?

AGENT: Two things, David.

First, the pathology report. It should show the patient name, specimen details, the testing date, and the clinician or lab signature if there is one. A high-quality scan is fine as long as the report is complete and fully readable. If the plan happens to require the original, the portal instructions or our support team can confirm the mailing address.

Second, the treating provider's office note. That needs to show the patient name, visit date, the assessment, and the treatment or follow-up recommendation. Please upload all pages together in one PDF if you can. For medical claims it also helps to have the treating provider or facility name visible on each page.

For submission, start with the member portal or the claim upload link so both files stay attached to CL-2048. Each file should be legible and complete with the claim-identifying details and dates visible. If you can't upload online, we can set up fax or mail.

Once they're received, the claim goes back into review rather than finishing instantly. Processing is usually less than a week, though intake and another review cycle can add time, and if anything is unclear the team may come back for more information. Aim to send them within a week, and remember the appeal deadline is 18 March 2026.

Anything else I can help with on this?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Asking which documents need to be submitted for the denied claim', 'timeframe': 'January', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 9.7s]

CALLER: No that's all. And no email needed, thanks.

AGENT: Understood, no email summary will be sent. Thanks for taking care of this for your mother, David, and good luck with the appeal. Take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Caller done with questions about denied healthcare claim CL-2048 document submission', 'timeframe': 'January', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 5.8s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's healthcare claim was denied"}
- [turn 1] intent = denial_question
- [turn 2] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"}
- [turn 2] representative matched (son); consent request CONSENT-722EE2 sent
- [turn 3] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"}
- [turn 4] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"}
- [turn 4] consent approved; representative verified
- [turn 4] claim CL-2048 selected (from what the caller told you earlier)
- [turn 5] intent = document_submission
- [turn 6] caller has no further questions; moving to POST_PROCESS
- [turn 6] email summary offered
- [turn 6] caller declined the email summary up front