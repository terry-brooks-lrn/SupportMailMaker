




SupportMail





![SupportMail header](https://dozens.nyc3.cdn.digitaloceanspaces.com/learnosity/image-removebg-preview.png)
Date published


February 9, 2026





 Welcome to the January edition of SupportMail.
 For those of you new to this aggregation, SupportMail is an internal
 email assembled by the Support team to highlight noteworthy tickets,
 calls, events, etc., that seem likely to be of interest to a larger
 audience. Inclusions are for information purposes and are not limited
 to unsolved issues.
 



 If you think any internal party should be added to this distribution
 list, please send a request and email address to
 [Rich Shupe](mailto:rich.shupe@learnosity.com).
 




![Issues section header](https://dozens.nyc3.cdn.digitaloceanspaces.com/learnosity/header_issues.png)

 Here are some of the notable customer issues that have come across
 our desks recently:
 



### Platform Limitation




| Title Data Table Preview Scrubber Configuration Customer Beable Education Summary The customer inquired about hiding the Data Table preview scrubber at the item level via LRNO configuration. It was clarified that no out\-of\-the\-box setting currently exists to disable the scrubber independently. The scrubber appears whenever dynamic data tables are present in items, even if editing is restricted. The customer’s use case involves instructors cloning items with dynamic data tables but not viewing or editing them; thus, showing the scrubber causes confusion. The recommended workaround is to hide the scrubber via custom CSS. A feature request to add a configuration option to disable the scrubber was offered, pending more detailed use\-case context from the customer. The conversation is awaiting any further background to support the feature request.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29530) |
| --- |




### Product Bug




| Title Question Type Logic / Scoring Issue Customer Pearson Core Platforms Summary The customer reported an issue with the Match List question type where integer values used as options result in incorrect answers being set as correct. The support team replicated the problem and confirmed it as a bug. They requested the customer's LTS version and upgrade plans for further investigation. The case is currently open, with the team working on a resolution and updates to be provided. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/17429) |
| --- |




| Title Items Api / Json Structure Conflict Customer Riverside Insights Summary The customer needed help setting up an activity with multiple sections but encountered JSON errors and issues with empty "items" arrays being appended by the author site, causing validation errors. Support identified this as a known bug where the author site forcibly adds an empty "items" array, conflicting with the use of "sections" in the Items API. The workaround is to remove the empty "items" Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/24650) |
| --- |




### Upgrade Regression




| Title Accordion Behavior In Items Api Customer Achievement Network Summary The customer is upgrading from Items API v2024\.2 to v2025\.2 and experiencing an issue where Accordion elements' content is hidden but still occupies space, unlike the previous version. They provided detailed configs, code snippets, and screenshots showing CSS discrepancies, suspecting a Learnosity CSS rule enforcing height and display properties. The support team could not reproduce the issue in a vanilla environment and suggested CSS workarounds like using display:none, but the customer prefers a proper fix in the API to avoid fragile hacks. The support team explained their sprint\-based release cycle, estimating no fix before late September or October, and recommended a temporary workaround. The customer implemented a workaround that avoids direct Learnosity element manipulation and awaits a formal fix. Additionally, the customer raised concern about a broad CSS rule using :is(\#lds, body) .collapse:not(.show) { display:none } that may unintentionally affect page elements outside Learnosity. Support acknowledged this and plans to escalate it to engineering, with the ticket added to backlog for future triage. The customer suggested narrowing the CSS selector to avoid affecting global page styles. No ETA for a fix is currently available; updates will be provided as progress occurs. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28622) |
| --- |




### Product Bug




| Title Activity Search \& Bulk Update Errors Customer Cengage Learning Summary The customer is experiencing frequent errors when searching for activities and performing bulk item updates in Cengage Course Solutions – Production, requiring multiple refreshes to resolve. The support agent attempted to reproduce the issue without success initially but requested videos and console error details from the customer. After receiving videos and error information, the agent successfully replicated the problem and escalated it to engineering for resolution. The ticket remains pending while awaiting a fix from the engineering team. No further customer actions are currently requested.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29562) |
| --- |




### Feature Request




| Title Media Handling In Classification Questions Customer Cengage Learning Summary The customer reported an issue with audio clips in their custom Classification (Many to Many) question type, which has "duplicate\_responses" enabled. This problem does not occur in the Many to One type without duplicate responses. The support agent reproduced the issue and escalated it to engineering. Engineering identified a fundamental incompatibility: audio/video players require unique IDs, but duplicate responses duplicate the player without unique IDs, causing conflicts. Therefore, audio/video features cannot currently support duplicate responses. A long\-term feature request is raised, but no short\-term fix is available. The customer is advised to disable duplicate responses or use alternative question types. Additionally, a related audio player issue on touch devices is under review.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27357) |
| --- |




### Product Investigation




| Title Drawing Question Response Persistence \& Reporting Mismatch Customer Manabie Summary The customer reported that after submitting an assessment with a Drawing question type, the session\-detail\-by\-item report shows no drawing data, though the API indicates the question was attempted. Learnosity clarified that they do not store historical session states and noted the response data is null despite "attempted: true," which is unusual. The item attempt status is "not attempted," conflicting with the response attempt flag. Learnosity is investigating the cause and asked if the customer uses resetResponses() or question.reset() methods to help narrow down the issue. No resolution yet; further investigation is ongoing. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28187) |
| --- |




### Product Bug




| Title Scoring Api Math Content Errors Customer Uniwise Summary The customer has been experiencing recurring 500 Internal Server Errors on the scoring endpoint, impacting their ability to generate accurate statistics for grading. Initial scaling of containers temporarily reduced errors, but issues persisted, primarily affecting this customer despite relatively low request volumes. Investigation revealed two content\-related bugs in legacy and current math question types causing scoring failures. The engineering team is actively working on fixes, with an expected sprint completion around early November and ongoing testing. The customer reduced batch sizes from 750 to 500 questions per request to mitigate errors but cannot reduce further due to performance concerns. Recent monitoring shows no new 500 errors since early November, though the customer has a backlog of failed builds to retry. The support team continues to monitor and awaits customer feedback on error resolution. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28869) |
| --- |




### Client Enablement




| Title Max Score Calculation \& Api Limitations Customer Mereos Summary The customer wants to quickly obtain the max score of an activity even if no session exists. Initially, it was explained that no direct API provides this; the max score must be calculated by summing individual question scores via multiple Data API calls. The customer expressed frustration with slow loading and indirect APIs. The support agent recommended switching API endpoints to the EU region to reduce latency and suggested splitting large single\-item activities into multiple items to improve performance using lazy loading. The customer reported discrepancies between max scores from session endpoints and manual calculations, which the agent attributed to improperly authored questions lacking valid correct answers, manual scoring, and edits to items after sessions were created. The agent clarified that max\_score is defined at the item level, not question level, and sessions capture snapshots of item data at the time of creation, causing differences if items are edited later. The agent advised using different activity IDs for cohorts to avoid such discrepancies. Finally, the agent confirmed it is possible to get the max\_score of an item containing many questions by querying the Data API with the item reference and including "max\_score" in the request. An example response showed an item with 30 questions and a max\_score value. No direct API exists to get max score of an activity without a session; it requires summing item/question scores. Performance can be improved by using EU endpoints and splitting large items. Discrepancies in max scores arise from question authoring issues, manual scoring, and item edits post\-session. The agent will discuss internally about additional solutions. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29092) |
| --- |




### Platform Limitation




| Title Tag Volume \& Query Performance Customer Cengage Learning Summary The customer inquired about fetching items from the ItemBank with specific tags (ssoIsbn, discipline) in Unpublished status and activities with specific tags containing items without tags. The support team investigated and found that the customer's use of single\-use tags (e.g., Legacy ID, audio, Media) has grown excessively, with some tag types exceeding hundreds of thousands or over a million unique tags. This misuse causes slow or failing tag\-based queries, including the requested API calls timing out or returning errors. The recommendation is to move seldom\-used or single\-use metadata out of Learnosity tags into the customer's own lookup tables to improve query performance. The team confirmed the intended API usage but noted current limitations due to tag volume. No immediate fix was provided; the issue is under review with engineering. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29149) |
| --- |




### Platform Incident




| Title Assessment Integrity \& Validation Exposure Customer Powerschool Group Summary A security alert was raised regarding a publicly available cheating script on GitHub targeting Schoology assessments powered by Learnosity. The script automates answer extraction and completion by intercepting Learnosity API calls and exposes an AI21 API key, enabling unauthorized AI\-based solving of assessments. The issue threatens assessment integrity and exposes confidential data. The vendor acknowledged the report, notified stakeholders, and identified the root cause as inclusion of validation data during assessment initialization. They plan to mitigate this by stripping validation data for high\-stakes assessments and adding obfuscation/encryption in the next LTS release, tentatively scheduled for February. Updates will be provided as available. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29192) |
| --- |




### Platform Limitation




| Title Author Api Asset Upload Overrides Customer Everway Summary The customer reported an issue with adding an audio feature in the Author API text editor: when selecting "Audio" and clicking "\+Add," an empty panel appears and becomes unresponsive. They are using version v2025\.2\.LTS in Chrome. The customer shared their assetRequest callback, which only handles image assets, overriding the default handler for all media types. The Learnosity engineer confirmed that providing an assetRequest callback overrides all asset types, requiring custom logic for each; currently, there is no way to mix custom handlers with default uploaders for other media types like audio or video. The engineer has raised feature requests to allow partial overrides and improve documentation clarity. The customer appreciated the update and feature requests. No immediate fix exists; next steps depend on future product updates.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29571) |
| --- |




### 




| Title Item Pool Validation \& Widget Reference Conflicts Customer HMH Houghton Mifflin Harcourt Summary The customer reported repeated "halted" status issues for the "SS 2018 HS AH" item pool due to duplicate widget references when combining content from multiple item banks. Engineering identified the root cause as two widgets sharing the same reference within the pool, causing the process to halt to prevent overwriting. The duplicate references stemmed from the customer's use of the Data API and content export/import workflow, leading to conflicts especially with item 611218410\. Engineering resolved the halted status issue for this item pool, enabling successful publishing. They plan to follow up separately to understand the customer's workflow and prevent future occurrences. The customer confirmed they can now publish without issue. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/26841) |
| --- |




### Product Bug




| Title Items Api Runtime Errors (10001\) Customer Progress Learning Summary The customer reported intermittent 10001 errors with Learnosity Items API on version 2024\.3 in preprod and QA environments, especially on unstarted Study Plan activities. Support investigated but could not consistently reproduce the issue; CPU throttling triggered it sometimes. A theory about "Enable Scrolling For Long Content" item setting was tested and ruled out. Engineering released a fix on the developer version, later backpatched to 2024\.3\.LTS and 2025\.1\.LTS. The customer planned to upgrade QA to 2025\.1\.LTS and test. After upgrade, new bugs appeared including persistent intermittent 10001 errors in Author API preview. Support requested login and repro steps to escalate. Separate tickets were created for other issues. The latest 10001 error report was linked to a related ticket for further investigation. The fix deployment to production was confirmed but some issues remain in newer versions. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/26886) |
| --- |




### 




| Title Automatic Translation \& Dynamic Content Loading Customer Hats \& Ladders Summary The customer reported an issue where Google Chrome's native Translate feature does not automatically translate newly loaded Learnosity assessment content until the user toggles the language manually. This occurs due to a race condition where Chrome Translate activates before the dynamic Learnosity content fully loads into the DOM. The problem is specific to Chrome and Chrome\-based browsers; other browsers like Safari, Edge, and Firefox do not exhibit this issue. Learnosity support escalated the issue to engineering but found they have limited control over Google Translate's DOM parsing and timing. A fix would require potentially breaking DOM changes and could only be released in a future major version, with no firm ETA. The customer understands the limitations and plans a tiered approach: continue using Chrome Translate for low\-stakes formative assessments, implement static translations with Learnosity tools for higher\-stakes content, and possibly raise the issue with Google. The ticket is now marked solved with no immediate fix available. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/26990) |
| --- |




### Product Bug




| Title Learning Outcomes Report Data Ingestion Customer iTrack Education Summary The customer reported a 500 Internal Server Error when loading the Learning Outcomes report, while other reports worked fine. The support agent escalated the issue to engineering, who identified and fixed the root cause involving dataset indexing. The fix required re\-submitting historical sessions to populate data. The customer tested new sessions but initially saw no data, prompting further investigation and urgent escalation. Engineering then performed a "touch" on relevant items to trigger re\-ingestion and released a fix on the developer version of the Reports API. The customer confirmed the report now loads correctly with data, even without explicitly using the developer version. The fix is being patched to production Long Term Support versions. The case is resolved with the report functioning as expected.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27396) |
| --- |




### Data Visualization Issue




| Title Missing Metadata \& Session Reprocessing Customer Carnegie Learning Summary The customer reported an error in their production environment when loading an outcomes report, indicating a missing tag ID in the item bank. The support team confirmed the tag was deleted on August 21, 2024, and identified six affected items and four user sessions impacted by this deletion. They recommended using the Reports API's errorListener callback to suppress user alerts temporarily and suggested reprocessing affected sessions via the Change Sessions Statuses and Trigger Followup Processing Data API to backfill data and resolve the error. The customer has a process to handle rescoring for manually scored items during reprocessing. Support is awaiting engineering feedback on retrieving the deleted tag's name and has logged a product enhancement request to improve error messaging by including the tag name.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27398) |
| --- |




### Product Investigation




| Title Assessment Navigation State \& Session Resume Issues Customer Flat World Knowledge Summary The customer reports recurring issues where students lose the ability to navigate between questions in assignments, especially when resuming previously started attempts. The problem involves navigation buttons becoming disabled ("toc\-disabled" class and disabled attributes), and persists despite using recommended settings like shuffle\_items and auto\-saving. Support investigated and found no reproducible steps in a vanilla environment except in a rare case of manual item order changes between sessions. They advised implementing robust user session management to prevent multiple concurrent sessions. The customer provided session IDs and LogRocket videos showing the issue. Support escalated a working theory to Engineering and shared environment credentials for deeper investigation. The issue remains unresolved but Engineering is actively investigating. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28724) |
| --- |




### Assessment Best Practices




| Title Client\-Side Validation Exposure Customer Larson Texts (Big Ideas Learning) Summary The customer is concerned that the current "Check Answer" feature exposes validation data client\-side, allowing students to "hack" and obtain correct answers, undermining assessment integrity. Learnosity confirmed no out\-of\-the\-box solution exists to perform local validation without exposing validation data, as server\-side scoring per question is impractical due to rate limits and performance. Recommended best practice is to strip validation and disable Check Answer for high\-stakes tests, but the customer wants a more robust solution. Learnosity proposed a custom Check Answer routine that fetches validation data server\-side per assessment, obfuscates it, and serves it to clients, balancing security and performance. They also discussed differentiating assessment modes (practice vs. exam) to control validation exposure. A stakeholder call is being arranged to explore these options further. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27102) |
| --- |




### Client Enablement




| Title Activity—Level Localization (Labelbundle) Customer HMH Houghton Mifflin Harcourt Summary The issue was a missing labelBundle property; however, HMH is still using base templates for this item bank, so we couldn’t resolve it by updating a player template. Because base templates can’t be modified through the UI or Data API, a script was required as a workaround to update all affected content. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29393) |
| --- |




### Platform Limitation




| Title Hosted Video Player Format Support Customer MZ Development Summary The customer inquired about playing WebM video files instead of MP4s using the hosted video player, as their project videos are in WebM format. Support confirmed the hosted player officially supports only MP4 files up to 100 MB, though WebM files can be uploaded via the Data API and may play in browsers due to browser behavior, but this is not guaranteed or supported. The customer noted their lockdown browser client does not support MP4, necessitating WebM support. Support escalated a feature request for WebM support to product and engineering teams, clarifying any solution would be long\-term. Currently, using WebM via manual upload is a possible but unsupported workaround. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29444) |
| --- |




### Platform Incident




| Title Regional Routing \& Firewall Access Customer iCEV Summary The customer reported that two correctional facilities suddenly could not access Learnosity assessments due to requests hitting regional URLs (questions\-va.learnosity.com) instead of the expected base URL (questions.learnosity.com), which their firewall whitelist did not allow. Learnosity support confirmed no intentional changes but noted default routing to the US East (VA) region if no regional endpoint is specified. Multiple customers were affected, prompting escalation to engineering. Learnosity identified and fixed the issue by updating hosts and load balancers, completing 50% of updates initially and finishing shortly after. The customer confirmed the platform is now working for their users.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29520) |
| --- |




### 




| Title Server/Client Evaluation \& Api Metadata Customer Manabie Summary The customer reported an issue where their custom math question's max score was showing as zero in the response session and reports, despite being set correctly by the author. Investigation revealed a server\-side scoring error caused by use of the browser\-only \`window\` object in their scorer.js, which was fixed by removing such references. Then, a critical error occurred because \`mathcore.validate()\` was undefined server\-side; Learnosity engineering confirmed this as a platform issue and provided a workaround to use \`mathcore.evaluateVerbose()\` on the server and \`mathcore.validate()\` on the client, resolving scoring inconsistencies. The customer confirmed the fix worked. Later, the customer reported the Data API endpoint for item max score still returned zero despite correct authoring. After further review, Learnosity confirmed recent changes fixed this, and the endpoint now returns the correct max score. The ticket was closed with the issue resolved. No further action or API upgrades are needed from the customer.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27076) |
| --- |




| Title Math Validation Errors In Review State Customer Larson Texts (Big Ideas Learning) Summary The customer reported a validation error (10019\) occurring during Learnosity's review state for a math question using the older clozeformula question type, specifically when a student submits a response involving square roots and fractions. The error triggers the error handler despite the response rendering correctly and scoring properly, causing concern about the review flow. The support agent confirmed the issue stems from limitations in the original clozeformula engine, which is less capable of handling complex math expressions, and recommended migrating to the newer clozeformulav2 question type that handles such cases without errors. The agent escalated the issue to Engineering for investigation and submitted a feature enhancement request to warn authors when question setups exceed clozeformula’s capabilities. The customer inquired about the impact of switching question types on existing assignments; the agent explained that changing question types mid\-assessment can cause inconsistencies for prior and in\-progress submissions and may affect reporting. The current advice is to ignore the console error temporarily while Engineering investigates, as alternative solutions may emerge without requiring immediate question type changes. The agent will provide updates as available.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27797) |
| --- |




### Platform Limitation




| Title Offline Package Generation Size Limits Customer Progress Learning Summary The customer is experiencing failures when generating offline packages of 1000 items, receiving a halted status after 30 seconds. A workaround of splitting into two 500\-item packages is not ideal. The agent confirmed the issue is due to a package size limit of 500MB and will consult product management for potential solutions.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28849) |
| --- |





![Oops section header](https://dozens.nyc3.cdn.digitaloceanspaces.com/learnosity/header_oops.png)

 Here are some recent oops moments worth noting:
 



### Platform Incident




| Title Scoring Delay During Db Migration Customer Manabie Summary The customer, Manabie, reported an issue on December 15th where some Learnosity sessions were returned as incomplete due to delayed scoring responses between 4:30 PM and 5:00 PM VNT. Investigation revealed the root cause was a scheduled database migration from MySQL to PostgreSQL, part of a platform\-wide upgrade to improve performance and scalability. The migration involved temporary processing queues and a brief cutover period causing scoring delays but no data loss or submission interruptions. The vendor apologized for the impact and acknowledged the lack of prior notification, committing to better communication for future maintenance. The customer accepted the explanation and plans to inform partners accordingly. No unresolved issues remain.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29381) |
| --- |





![Wins section header](https://dozens.nyc3.cdn.digitaloceanspaces.com/learnosity/header_wins.png)

 Here are some recent wins worth celebrating:
 



### Authoring Workflow




| Title Multilingual Content Management Customer ACTFL Summary The customer, Reuben, inquired about using the Author Aide translation tool, specifically about viewing original English content alongside translations in metadata fields and preventing certain fields (like Introduction text) from being translated. Anthony responded that side\-by\-side metadata viewing is currently unavailable and that all text fields are translated by default, recommending manual overwriting for untranslated sections. Anthony also informed Reuben about upcoming bulk translation features, clarifying no need to duplicate items before translation and that usage limits depend on contract terms. Reuben requested security information about content translation; Anthony provided a relevant FAQ document link. Additionally, Anthony introduced a pending LT Library plugin for multilingual content inclusion, explaining it requires manual integration and does not offer built\-in grammar/spelling checks. Reuben expressed interest and will await further updates. No explicit next steps were stated beyond monitoring feature developments and potential client testing.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/26580) |
| --- |




### Performance Issue




| Title Author Api Activity Listing Customer Cengage Learning Summary The customer reported slow performance and occasional timeouts when loading the Author API Activity List view, especially with a large number of activities in their dev item bank. They use a workflow where they initially load the activity list, then call navigate() with complex tag filters, causing multiple server calls and slow load times. The support agent recommended avoiding the extra navigate() call by applying filters directly in the initial Author API request or calling navigate() once in the readyListener event, which improved performance. The customer cannot use the initial filter config due to a known issue and has many throw\-away activities from automated tests, which may impact performance. The agent advised preventing saving test activities by intercepting saves and using just\-in\-time previews via the Items API, and archiving old test activities to reduce load. The customer confirmed their automated tests do not run on production and are limited in concurrency. The agent also addressed a similar issue with the item list view, requesting the customer's initialization JSON to investigate why filters do not apply when using navigate() in readyListener. The conversation is ongoing with the agent awaiting further details to reproduce the item list issue. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27281) |
| --- |





![News section header](https://dozens.nyc3.cdn.digitaloceanspaces.com/learnosity/news_header.png)

 Here is some recent news worth sharing:
 



### Operational Task




| Title Bulk Activity \& Session Deletion Customer Accelerate Learning Summary The customer requested deletion of activities tagged as "Assignment" or "Resource" created before July 4, 2025, initially in the dev environment for review, then in production. They do not require backup but want to review data counts before deletion. The support team clarified data counts, deletion scope, and backup policies, confirming data is stored in the customer's warehouse. Engineering validated deletion scripts in QA and staging, planning to delete over 9 million sessions in batches over 13\-18 days, starting with dev. The customer requested confirmation of deletion scope and expected activity counts in dev. The process is pending engineering confirmation and scheduled to begin soon. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28884) |
| --- |




### Platform Incident




| Title Adaptive Scoring Stuck In Pending\_Scoring Customer Manabie Summary The customer reported multiple assessment sessions stuck in the PENDING\_SCORING status for over a day, preventing users from seeing their scores and impacting exams. Initial investigation revealed the status is transient but sessions stalled due to missing question/response data in the adaptive session database, causing the scoring engine to hang. The engineering team is still investigating the root cause, including potential content issues. The customer declined manual grading tools and seeks a thorough incident analysis with root cause identification and preventive measures, emphasizing the critical impact on user trust and exam integrity. Retakes are a short\-term workaround but not a viable long\-term solution. No resolution yet; further investigation and updates are pending. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/29358) |
| --- |




### Assessment Best Practices




| Title File Uploads \& Save Workflow Customer Wiley Summary Students reported uploading files that instructors could not see in assignments. Investigation showed no saved or submitted sessions for the provided session and user IDs, indicating uploads were not finalized. After receiving upload attempt dates, engineering retrieved the files from backend storage but noted this is not a sustainable solution. They recommended implementing a save() method call triggered by a file upload completion event to ensure sessions are saved. The customer acknowledged the advice and plans to address it in a future sprint. The ticket is tentatively closed, pending any further questions.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27189) |
| --- |




### Platform Limitation




| Title Annotation Tool Anchoring In Scrollable Content Customer Progress Learning Summary The customer reported that drawings made with the annotation tool are not anchored to the drawn area when scrolling within passages that have scrolling enabled. The support agent reproduced the issue and escalated it to Engineering. Engineering confirmed the root cause: the drawing tool anchors to the main browser scroll, not the inner passage scroll, due to design limitations. No short\-term fix is available, so the agent recommended either disabling passage scrolling or using highlights instead, which remain anchored. The customer accepted this and requested updates on a related highlighter fix. The highlighter fix is tentatively scheduled for deployment by March 11\. The case was closed with a link to the ongoing highlighter ticket for further updates. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27223) |
| --- |




| Title Annotation Behavior With Scrollable Content Customer Pearson Assessment Group Summary The customer reported that drawings and annotations do not move correctly when the "Enable scrolling for long content" feature is enabled, causing them to remain static instead of sticking to their original positions during scrolling. This issue was confirmed internally and escalated as a bug to Engineering. A temporary workaround suggested was to use the "Highlight" annotation tool, which remains correctly positioned during scrolling. The customer requested the fix by end of March due to peak exam season starting in May. Engineering explained the typical bug fix SLA is 6\-8 weeks to dev release and 9\-11 weeks to production, with fixes backpatched to supported LTS versions upon request. The customer is currently on v2023\.1 but upgrading to v2024\.2, and requested the fix be backpatched to v2024\.2\. Engineering later confirmed the root cause is a design limitation where drawings track the main window scroll, not inner scrollbars, making a fix unfeasible short\-term. They recommended avoiding using drawing annotations with long content scrolling enabled. A formal feature request was submitted for a long\-term solution, which will be prioritized and released in a future LTS version following standard feature request timelines. The customer acknowledged the update and will await further news on the feature request. Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27235) |
| --- |




### Performance Issue




| Title Authoring Scalability \& Test Data Overload Customer Cengage Learning Summary Customer Akshay reports slowness and errors in the create item flow due to over 50,000 passages caused by their automated testing flooding the item bank. Support explained this volume is abnormal, requested halting automated testing in authoring, and noted no current solution exists to fix the slowness or errors.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/27514) |
| --- |




| Title Assessment Api Concurrency \& Rate Limits Customer TVO Summary The customer inquired about rate limits on the Assessment API due to concerns about scaling for 6,000\-12,000 students starting a standardized test simultaneously. The response clarified that there are no rate limits on the Assessment API itself, which supports over 40 billion requests annually and millions of daily users. Rate limits apply only to the Data API, which handles bulk content operations, and even those limits are high and manageable with batching. The assessment concurrency is generally not an issue since most processing occurs client\-side, with staggered user interactions. The team requested a sample day/time for peak activity to inform engineering considerations. No immediate action is required; the engineering team will be informed of the customer's scalability expectations.  Ticket  [View ticket](https://learnositysupport.zendesk.com/agent/tickets/28117) |
| --- |







