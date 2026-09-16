# rep_ok: Representative: named on file + 3 policyholder items + consent (default scenario approves on the second check)

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Hi, I'm David Chen calling for my mother Margaret Chen about her denied healthcare claim.

AGENT: Thanks, David, and I've noted that you're calling about your mother's healthcare claim. I'll pull that up as soon as we're through verification.

Since you're calling on her behalf, I'll need two more details about your mother before I can send her a consent request. Any two of these work: her date of birth, the phone number on file, the email address on file, or the last four digits of her SSN or national ID. Which would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's healthcare claim was denied"} emotion=neutral/low facts=[] 6.1s]

CALLER: Sure, I'm her son. Her date of birth is March 15, 1985 and the last four of her SSN are 4472.

AGENT: Thank you, David, those details check out on my end.

I've just sent a consent request to your mother using the contact details we have on file. Once she approves it, I can go through the claim with you in full. She'll usually respond within a minute or two, so just let me know when you'd like me to check on it.

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's denied healthcare claim"} emotion=neutral/low facts=[] 5.9s]

CALLER: Ok, can you check if she approved it?

AGENT: I just checked, and her approval hasn't come through yet. That's pretty normal in the first few minutes, so nothing to worry about. I'm happy to check again in a moment if you'd like to stay with me, and as soon as it lands I'll go straight into the claim with you.

    [phase=VERIFY_ID verified=False claim=None hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's denied healthcare claim"} emotion=neutral/low facts=[] 6.9s]

CALLER: And now?

AGENT: Good news, her consent has just come through, so you're verified as her authorised representative and I can go through everything with you.

The claim I have up is CL-2048, the healthcare claim opened on January 12, 2026, and it's currently showing as denied. The reason is that the review file didn't include the pathology report or the treating provider's office note.

To get it reconsidered, you'd need to send in those two documents. The best route is the member portal or the claim upload link so they stay attached to the file, and if online upload isn't an option, we can help arrange fax or mail. The appeal deadline is March 18, 2026, so I'd aim to get them in within the week. Want me to walk you through exactly what each document needs to show?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.0s]

CALLER: Great. So what documents does she need to send?

AGENT: Two documents, David.

The pathology report needs to show your mother's name, the specimen details, the testing date, and the clinician or lab signature if there is one. A high-quality scan is fine as long as the report is complete and fully readable; if the plan requires the original, the portal instructions or our team can confirm the mailing address.

The office note from the treating provider needs to show her name, the visit date, the assessment, and the treatment or follow-up recommendation. Upload all pages together in one PDF if you can, and it helps to have the provider or facility name visible on each page. Send both through the member portal or claim upload link, or we can arrange fax or mail. Once they're received, the claim goes back into review, usually less than a week, though intake and another review cycle can add a little time, and the team may come back to you if anything is unclear. Anything else I can help with?

    [phase=PROCESS_CASE verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Asking which documents need to be submitted for the denied healthcare claim', 'timeframe': 'January', 'claim_id': 'CL-2048'} emotion=neutral/low facts=['claim', 'document_guidance', 'field_meanings', 'other_claims_on_file'] 8.1s]

CALLER: No that's all. And no email needed, thanks.

AGENT: Understood, no email summary will be sent. Best of luck getting those documents in before the 18th, David, and take care.

    [phase=CLOSED verified=True claim=CL-2048 hints={'case_type': 'healthcare', 'status': 'denied', 'details': 'Caller done with questions; declines email summary', 'timeframe': 'January', 'claim_id': 'CL-2048'} emotion=neutral/low facts=[] 5.8s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = representative
- [turn 1] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's healthcare claim was denied"}
- [turn 1] intent = denial_question
- [turn 2] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's denied healthcare claim"}
- [turn 2] representative matched (son); consent request CONSENT-18E082 sent
- [turn 3] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Mother's denied healthcare claim"}
- [turn 4] stored case hints for later: {'case_type': 'healthcare', 'status': 'denied', 'details': "Denied healthcare claim for caller's mother"}
- [turn 4] consent approved; representative verified
- [turn 4] claim CL-2048 selected (from what the caller told you earlier)
- [turn 5] intent = document_submission
- [turn 6] caller has no further questions; moving to POST_PROCESS
- [turn 6] email summary offered
- [turn 6] caller declined the email summary up front