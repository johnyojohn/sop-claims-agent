# human: Refusal to verify, persuasion, then request for a human

AGENT: Hi, thanks for calling Northwind Insurance claims support, this is Ava. How can I help you today?

CALLER: Margaret Chen. I want to know about my claim.

AGENT: Thanks, Margaret. I've noted that you're calling about a claim, and I'll pull it up as soon as we finish verifying you.

I have your name. To get you verified, I need two more items from this list: your date of birth, the phone number on file, the email address on file, or the last four digits of your SSN. Which would you like to start with?

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants information about her claim'} emotion=neutral/low facts=[] 5.7s]

CALLER: I'm not giving you my social security number over chat.

AGENT: That's completely fair, and you don't need to. The SSN digits are just one option among several.

I know the verification feels like a hurdle when you just want an answer, but claim details are protected personal information, so we have to confirm we're speaking with the policyholder before sharing anything. Any two of these will do it: your date of birth, the phone number on file, or the email address on file. Which two work for you?

    [phase=VERIFY_ID verified=False claim=None hints={'details': 'Caller wants information about her claim'} emotion=frustrated/medium facts=[] 6.1s]

CALLER: No. I don't trust this. Get me a real person.

AGENT: Understood, Margaret, and that's a reasonable thing to ask for. I'm handing this conversation to a claims representative now.

They'll pick it up from here and follow up using the contact details we have on file. They will complete the verification with you first, then go through your claim.

    [phase=ESCALATED verified=False claim=None hints={'details': 'Caller wants information about her claim'} emotion=frustrated/high facts=[] 5.4s]

## Checks

PASS

## Harness events

- [turn 1] caller_role = policyholder
- [turn 1] stored case hints for later: {'details': 'Caller wants information about her claim'}
- [turn 1] intent = general_claim_question
- [turn 2] verification pushback #1
- [turn 3] ESCALATED: caller asked for a human representative