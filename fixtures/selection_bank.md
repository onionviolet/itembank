# Selection fixture bank (synthetic)

Fully invented content for a fictional municipal water-treatment operator
certification, written to exercise the phase 7 selection engine. It exists to
give the selector a bank large enough to make four selection-mode compositions
visibly differ, to make cooldown and pair tests meaningful, and to give the
trace a real runner-up pool. It is not derived from any real course, exam, or
textbook, and no real question bank belongs in this repository. Objectives are
namespaced (`subject:path`) so the selection and trend work can address them
unambiguously.

Q1. An operator reads 0.9 mg/L free chlorine at the plant outlet but 0.1 mg/L at a sampling tap five miles into the distribution network, against a 0.2 mg/L regulatory minimum. What best explains the gap?   (difficulty: application)
[ID: c3d14e8380044438]
[HASH: sha256:33fb0a979d1c3872]
[OBJECTIVE: water:distribution.residual]
[PAIR: distribution-vs-boil]

A) The far-end tap was sampled during a planned flushing program
B) The outlet analyzer was calibrated with stale reagents and is reading high
C) Chlorine demand in the long, aging main is consuming residual before it reaches the far end
D) The regulatory minimum applies only at the point of entry to the system

CORRECT: C

WHY BEST: A normal reading at the point of entry with a depressed reading far downstream is the signature of demand in transit. Biofilm, sediment, and long residence time all consume chlorine between the plant and the network edge.

KEY DISCRIMINATOR: The outlet reading is normal. That single fact separates a dosing problem (which would depress both readings) from a transit problem.

SECOND-BEST: A. A sample drawn during flushing would read artificially low because the flush is pulling from a different layer; it is worth ruling out, but it explains one tap, not a systemic gradient.

DISTRACTOR ANALYSIS:
- A) A flush would temporarily depress the far-end sample; this would be correct if the reading returned to normal once flushing stopped.
- B) Stale reagents would distort both the outlet and downstream readings, so this would be correct only if the two meters disagreed in isolation, not along a gradient.
- C) Correct: demand in transit consumes the residual.
- D) The minimum applies everywhere in the distribution system; this would be correct if the question asked where the limit is measured.

TRAP: Reading a low number as a dosing failure without checking where in the system it was measured.

CONFIDENCE: high

Q2. What is the primary purpose of maintaining a measurable free-chlorine residual throughout the distribution system?   (difficulty: recall)
[ID: 0cfc5fe04a7e471c]
[HASH: sha256:61aa7c3b5904ec5b]
[OBJECTIVE: water:distribution.residual]

A) To satisfy the laboratory's daily testing quota
B) To make the water taste fresher at the customer tap
C) To provide continuing disinfection against recontamination during transit
D) To prevent scale from depositing in service lines

CORRECT: C

WHY BEST: The residual is the disinfectant that stays in the water after treatment, protecting it from organisms that could enter through leaks, breaks, or backflow between the plant and the tap.

KEY DISCRIMINATOR: The residual protects the water after it leaves the plant. That "in transit" framing is what separates disinfection from mere water-quality reporting.

SECOND-BEST: A. Taste is why some utilities adjust chloramine chemistry, but residual maintenance is a health measure first; taste is a secondary consideration.

DISTRACTOR ANALYSIS:
- A) Testing quotas follow the residual; this would be correct if the question asked why samples are collected daily.
- B) Residual can affect taste, but this would be correct if the question asked why utilities manage disinfection by-products or customer complaints.
- C) Correct: continuing disinfection in transit.
- D) Scale control is about water chemistry, not disinfection; this would be correct if the question asked about hardness or corrosion control.

TRAP: Confusing a side effect of residual management with its purpose.

CONFIDENCE: high

Q3. Which conditions would justify boosting the chlorine residual at a booster station?   (difficulty: application)
[ID: 3eddb0f955c84888]
[HASH: sha256:24abf01a8e4ab4d0]
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: water:distribution.residual]

A) A confirmed low residual at the far end of the booster's service area
B) A customer complaint about a metallic taste in a single home
C) An upcoming planned main break with a temporary bypass
D) Growing demand from a newly connected industrial customer at the network edge
E) A routine weekly report showing the plant outlet at 0.9 mg/L

CORRECT: A, D

WHY BEST: Both indicate that delivered water is losing protection as it travels. A low far-end residual is the direct signal; a new high-demand customer extends residence time and demand, so boosting before the fact is preventive.

KEY DISCRIMINATOR: Is there a plausible mechanism for residual loss between the booster and the tap?

SECOND-BEST: Not applicable; the remaining options describe local complaints, scheduled work, or a healthy reading.

DISTRACTOR ANALYSIS:
- A) Correct: low residual at the far end is the direct justification.
- B) Metallic taste is usually plumbing or corrosion in one home; this would be correct if the complaint were systemic across the booster's area.
- C) A bypass changes flow patterns but is temporary; this would be correct if the question asked what triggers temporary extra chlorination during maintenance.
- D) Correct: new demand extends transit time and chlorine demand.
- E) A healthy outlet reading argues against boosting; this would be correct if the question asked what confirms the current dose is adequate.

TRAP: Treating any customer complaint or planned work as a reason to change the dose rather than as a question about delivered-water protection.

CONFIDENCE: high

Q4. Classify each activity as BOOST or MONITOR for managing residual in the distribution system.   (difficulty: recall)
[ID: 3129bb828958416b]
[HASH: sha256:f2780306c61c0ebe]
[TYPE: table]
[CATEGORIES: Boost | Monitor]
[OBJECTIVE: water:distribution.residual]

ROW) Raising the dose at a booster station after a confirmed low residual :: Boost
ROW) Reading residual at the far end of each pressure zone weekly :: Monitor
ROW) Adding a second booster station to serve a growing development :: Boost
ROW) Reviewing monthly residual trends for one zone :: Monitor

WHY BEST: Boosting changes the dose or the infrastructure that delivers it. Monitoring collects information without changing the dose.

KEY DISCRIMINATOR: Does the activity alter the delivered dose, or does it only measure it?

DISTRACTOR ANALYSIS:
- The weekly far-end reading is the row most often misfiled as boosting, because low readings are what trigger a boost. Measuring is not the same as acting.
- The trend review is monitoring even though it may lead to a future boost; the review itself changes nothing.

TRAP: Classifying by what the data may lead to rather than by what the activity itself does.

CONFIDENCE: high

Q5. A zone has shown a stable 0.4 mg/L residual for two years, then drops to 0.15 mg/L over one week with no change in demand. Which investigation should come first?   (difficulty: analysis)
[ID: 3b05edcdc7ba4c46]
[HASH: sha256:c986031dbb82f398]
[OBJECTIVE: water:distribution.residual]

A) Replace the zone's service-line meters
B) Look for an undetected leak, cross-connection, or biofilm sloughing in the zone
C) Increase the plant's coagulant dose to improve settling
D) Reduce the zone's flushing frequency to preserve residual

CORRECT: B

WHY BEST: A sudden residual drop with stable demand points to an event inside the zone — a leak, intrusion, or biofilm release — not to the plant's coagulation chemistry, which would move the outlet reading first.

KEY DISCRIMINATOR: The drop is zone-specific and sudden. A plant-side cause would move the outlet reading too.

SECOND-BEST: A. Meter replacement addresses billing accuracy, not water quality; it would be worth checking only if the drop were confined to one customer.

DISTRACTOR ANALYSIS:
- A) Meters measure consumption, not residual; this would be correct if the question asked why billable flow was wrong.
- B) Correct: a zone-specific sudden drop points to an event inside the zone.
- C) Coagulant dosing affects plant effluent; this would be correct if the outlet residual had also fallen.
- D) Flushing consumes residual but also protects it; this would be correct if the question asked how to raise a chronically low zone, not investigate a sudden change.

TRAP: Reaching for plant-side chemistry when the evidence points inside the zone.

CONFIDENCE: high

Q6. A dead-end main routinely records a residual below the minimum despite an adequate dose upstream. What is the most effective structural fix?   (difficulty: application)
[ID: 00fa5f184b774fb9]
[HASH: sha256:3079528058608af4]
[OBJECTIVE: water:distribution.residual]

A) Lower the regulatory minimum for dead-end sections
B) Install a recirculation or flushing loop so the dead end is no longer stagnant
C) Double the frequency of customer taste surveys
D) Move the sampling point closer to the booster

CORRECT: B

WHY BEST: A dead-end main loses residual because water sits and demand accumulates with nowhere to go; recirculation removes the stagnation, which is the cause.

KEY DISCRIMINATOR: The fix must address stagnation itself, not the measurement or the paperwork around it.

SECOND-BEST: D. Moving the sampling point hides the problem rather than fixing it; it would be defensible only if the goal were a system-wide average instead of a compliant dead end.

DISTRACTOR ANALYSIS:
- A) Lowering the minimum changes the standard, not the water; this would be correct if the question asked how to make a noncompliant reading legal.
- B) Correct: recirculation eliminates the stagnation that causes the loss.
- C) Surveys measure complaints; this would be correct if the question asked how to track customer satisfaction.
- D) Sampling elsewhere hides the dead-end problem; this would be correct if the question asked how to get a representative system-wide average.

TRAP: Confusing moving the measurement with fixing the condition.

CONFIDENCE: high

Q7. Put the steps for responding to a confirmed low residual in a zone in order.   (difficulty: recall)
[ID: 6f5cc859c91341c2]
[HASH: sha256:94a0dd0f0f0bcd95]
[TYPE: build]
[OBJECTIVE: water:distribution.residual]

STEP) Confirm the reading with a second sample from a nearby tap
STEP) Isolate and inspect the affected section for leaks or cross-connections
STEP) Flush the section to clear stagnant water
STEP) Adjust the booster dose or recirculation as indicated
STEP) Re-sample after stabilization to verify the fix

WHY BEST: Verification comes before any expensive action, inspection identifies the cause, flushing clears the stale water, dosing follows the cause, and re-sampling proves the fix.

KEY DISCRIMINATOR: Each step depends on the previous one: you cannot choose a fix before you know the cause.

DISTRACTOR ANALYSIS:
- Flushing before inspecting is the common error: it clears the symptom but can mask an ongoing leak or intrusion.
- Adjusting the dose before inspection risks treating a mechanical problem with chemistry.

TRAP: Treating the response as a fixed script rather than a sequence where cause-finding precedes action.

CONFIDENCE: high

Q8. An operator finds two zones with low residuals: one with a confirmed leak and one with normal flow but long residence time. What single action addresses both causes?
[ID: 87eaac6557b24b38]
[HASH: sha256:f20b789f73412d01]
[OBJECTIVE: water:distribution.residual]

A) Rebuild the zone boundaries so each is served by a nearer source
B) Increase booster chlorination in both zones
C) Switch both zones to chloramine to slow decay
D) Require daily flushing in both zones until readings recover

CORRECT: B

WHY BEST: Boosting the dose compensates for both a leak (which draws untreated water into the system and consumes chlorine) and long residence time (which lets demand accumulate). It is the one lever that acts on delivered residual directly.

KEY DISCRIMINATOR: The question asks for a single action that works for both causes; boosting is the common control.

SECOND-BEST: C. Chloramine decays more slowly than free chlorine, but switching chemistry is a treatment-plant decision, not a distribution fix an operator makes zone by zone.

DISTRACTOR ANALYSIS:
- A) Reboundaries change hydraulics over months; this would be correct if the question asked for a long-term capital solution.
- B) Correct: raising the dose raises delivered residual in both zones.
- C) Chloramine conversion is plant-scale and slow; this would be correct if the question asked how to reduce decay system-wide.
- D) Flushing clears stagnant water but cannot offset an active leak; this would be correct if only residence time were the problem.

TRAP: Picking the fix for the more familiar cause and ignoring that the question demands one action covering both.

CONFIDENCE: high

Q9. What condition is the trigger for issuing a boil-water notice?   (difficulty: recall)
[ID: d24926658abb49af]
[HASH: sha256:709dff7baf78d09b]
[OBJECTIVE: water:notification.boil]
[PAIR: distribution-vs-boil]

A) A scheduled valve-exercise program
B) A turbidity reading one unit below the treatment goal
C) A single customer complaint about cloudy water
D) Loss of positive pressure across part of the distribution system

CORRECT: D

WHY BEST: Loss of positive pressure allows untreated water and contaminants to enter the pipes, creating a credible pathway for pathogens to reach customers.

KEY DISCRIMINATOR: Is there a plausible route for pathogens to enter the system?

SECOND-BEST: A. Cloudy water alarms customers, but it is not itself a pathogen pathway; it would trigger investigation, not a notice.

DISTRACTOR ANALYSIS:
- A) Valve exercise is planned maintenance; this would be correct if the question asked what causes temporary discoloration.
- B) Below the treatment goal means the reading is acceptable; this would be correct if the reading were above the limit.
- C) Cloudiness is aesthetic and investigable; this would be correct if the question asked what starts a customer-complaint investigation.
- D) Correct: pressure loss permits intrusion.

TRAP: Treating any abnormal reading or complaint as a notification trigger.

CONFIDENCE: high

Q10. A main break floods a residential street and pressure in the affected section drops to zero for 40 minutes. What should the operator do about a boil notice?   (difficulty: application)
[ID: b93fb1f71b144ecf]
[HASH: sha256:ff186a7706cdb54a]
[OBJECTIVE: water:notification.boil]

A) Issue a notice immediately and sample after repair, because the pressure loss is a credible intrusion event
B) Wait for a confirmed positive bacteriological sample before notifying anyone
C) Issue a notice only if customers complain of illness
D) Notify the state regulator but not customers, since the break was repaired quickly

CORRECT: A

WHY BEST: The zero-pressure window is itself the trigger: intrusion can happen during the event, so customers must be told to boil before the confirmatory sample comes back.

KEY DISCRIMINATOR: The notice protects public health during the window of uncertainty, not after proof of contamination.

SECOND-BEST: B. Confirmatory sampling is important, but waiting for it leaves customers exposed during the highest-risk hours.

DISTRACTOR ANALYSIS:
- A) Correct: pressure loss is the trigger.
- B) Waiting for a positive sample reverses the precautionary order; this would be correct if the question asked how to confirm contamination after a notice.
- C) Illness reports lag exposure by days; this would be correct if the question asked about outbreak detection.
- D) Customers, not just the regulator, need the notice; this would be correct if the question asked whom to report the event to.

TRAP: Confusing confirmation with precaution.

CONFIDENCE: high

Q11. Which of the following are credible reasons to issue a boil-water notice?   (difficulty: application)
[ID: 8e9ac597b0e74091]
[HASH: sha256:43b0ec880dbdda40]
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: water:notification.boil]

A) Confirmed E. coli in a routine distribution sample
B) A planned switch between two surface water sources
C) Sustained negative pressure following a large main break
D) A seasonal increase in algae in the raw-water reservoir
E) A single low disinfectant reading that returned to normal within an hour

CORRECT: A, C

WHY BEST: A confirmed pathogen and a sustained intrusion pathway are both credible routes for contamination. Planned work and transient anomalies are not.

KEY DISCRIMINATOR: Does the event create or confirm a pathogen pathway right now?

SECOND-BEST: Not applicable; the remaining options describe planning, raw-water conditions, or a transient anomaly.

DISTRACTOR ANALYSIS:
- A) Correct: a confirmed indicator organism means contamination is present.
- B) A planned source switch is managed work; this would be correct if the question asked what triggers enhanced monitoring during a switch.
- C) Correct: sustained negative pressure permits intrusion.
- D) Algae in the reservoir affects treatment, not the distribution system; this would be correct if the question asked about taste-and-odour events.
- E) A transient low reading that self-corrects is not a pathway; this would be correct if the question asked when to begin an investigation.

TRAP: Listing anything abnormal rather than events that create a pathogen pathway.

CONFIDENCE: high

Q12. Sort each finding into NOTICE or NO NOTICE under the boil-water trigger rules.   (difficulty: recall)
[ID: 69bb6292bb884831]
[HASH: sha256:b763d8ac6167b050]
[TYPE: dnd]
[CATEGORIES: Notice | No notice]
[OBJECTIVE: water:notification.boil]

ITEM) Confirmed E. coli in a routine sample :: Notice
ITEM) Zero pressure for 30 minutes during a main break :: Notice
ITEM) A customer reports water that tastes metallic :: No notice
ITEM) Turbidity at 0.4 NTU against a 0.3 NTU treatment goal :: No notice

WHY BEST: Notices follow pathogen pathways: confirmed organisms or pressure loss. Aesthetic complaints and minor treatment excursions do not reach that bar.

KEY DISCRIMINATOR: Does the finding indicate contamination or intrusion, or does it merely look bad?

DISTRACTOR ANALYSIS:
- The turbidity row is the one that catches people: it is a real excursion, but it is a treatment-side goal, not a distribution pathogen pathway.
- The metallic taste is alarming to a customer but has no health pathway by itself.

TRAP: Treating every abnormal reading or complaint as a notice trigger.

CONFIDENCE: high

Q13. A notice was issued after a main break, repairs are complete, and two consecutive daily samples are clear. What is still required before the notice can be lifted?   (difficulty: analysis)
[ID: 70f90d5d82d64db0]
[HASH: sha256:d113863c59063127]
[OBJECTIVE: water:notification.boil]

A) A customer survey confirming no one drank the water
B) A third independent laboratory confirmation
C) Pressure restored to normal and regulator-approved clearance, including flushing and post-repair sampling per the notice protocol
D) A six-month period with no further complaints

CORRECT: C

WHY BEST: Lifting a notice is a process, not a single test: the repaired section must be flushed, pressure restored, samples collected, and the regulator's clearance criteria met.

KEY DISCRIMINATOR: Clearance is about completing the documented protocol, not about counting clean days or surveying customers.

SECOND-BEST: A. A third sample adds confidence but is not the deciding step; the protocol determines when the notice ends.

DISTRACTOR ANALYSIS:
- A) What customers drank is unknowable and irrelevant to clearance; this would be correct if the question asked about epidemiological follow-up.
- B) More samples help but are not the protocol's end condition; this would be correct if the question asked how to increase confidence in a result.
- C) Correct: the full clearance protocol.
- D) Six months with no complaints proves little about the event; this would be correct if the question asked how long to keep enhanced monitoring.

TRAP: Treating "no one got sick" or "two clean days" as the formal end of a notice.

CONFIDENCE: high

Q14. During a boil-water notice, a school asks whether bottled water is required for hand washing. What is the correct guidance?   (difficulty: application)
[ID: c0def0cbd8364566]
[HASH: sha256:0a58b6f533031689]
[OBJECTIVE: water:notification.boil]

A) Boiled water is required only for dishwashing, not for drinking
B) Bottled water is required for all uses including flushing toilets
C) Tap water is fine for hand washing if soap is used, because the notice targets water that may be ingested
D) Hand washing must use only alcohol-based sanitizer for the notice's duration

CORRECT: C

WHY BEST: Boil notices are about water that may be swallowed. Washing hands with soap and tap water is safe even under a notice, because the residual and mechanical action protect the user.

KEY DISCRIMINATOR: The notice governs ingestion, not contact.

SECOND-BEST: D. Sanitizer is an acceptable alternative where water is unavailable, but it is not required; soap and tap water remain safe.

DISTRACTOR ANALYSIS:
- A) Boiled water is required for drinking and cooking, not just dishwashing; this would be correct if the question asked which appliances are affected.
- B) Toilets and other non-ingestion uses are unaffected; this would be correct if the question asked how to use water during a complete loss of service.
- C) Correct: ingestion is the risk path.
- D) Sanitizer is an option, not a requirement; this would be correct if the question asked what to use where no tap water exists.

TRAP: Broadening the notice to every water use instead of the ingestion pathway.

CONFIDENCE: high

Q15. What is the single most important thing an operator must tell customers during a boil-water notice?   (difficulty: recall)
[ID: fc52fe9ee95f47df]
[HASH: sha256:5e97af787641b1ed]
[OBJECTIVE: water:notification.boil]

A) To bring water to a rolling boil for at least one minute before drinking, cooking, or making ice
B) To run every tap for five minutes before using any water
C) To stop using water entirely until the notice is lifted
D) To boil only the water used for bathing

CORRECT: A

WHY BEST: The notice's purpose is to tell customers how to make water safe for ingestion: a rolling boil for one minute (adjusted for altitude) kills the pathogens of concern.

KEY DISCRIMINATOR: The instruction must address ingestion and give the actionable boil method.

SECOND-BEST: B. Flushing taps is part of lifting a notice, not the instruction customers need during it.

DISTRACTOR ANALYSIS:
- A) Correct: rolling boil for one minute before ingestion.
- B) Flushing clears service lines; this would be correct if the question asked what to do when the notice is lifted.
- C) Stopping all water use is unnecessary and impractical; this would be correct if service were physically lost.
- D) Bathing water does not need boiling; this would be correct if the question asked which water uses are exempt.

TRAP: Giving a plumbing instruction where a health instruction belongs.

CONFIDENCE: high

Q16. A notice was issued at 9:00 a.m. after a pressure event. Which timing requirement is typical for notifying the regulatory authority?   (difficulty: analysis)
[ID: f73e3f29e4cc44d9]
[HASH: sha256:c16a31d791372493]
[OBJECTIVE: water:notification.boil]

A) Notification only after the notice is lifted
B) Notification within 24 hours, with the public notice issued as soon as practicable after the event is confirmed
C) Notification within 30 days, alongside the monthly report
D) Notification is the regulator's job, not the utility's

CORRECT: B

WHY BEST: Regulators require prompt notification (commonly within 24 hours) of a significant event, while the public notice goes out immediately to protect health during the investigation window.

KEY DISCRIMINATOR: Public notice and regulatory notification run on different clocks: public first, regulator on the required reporting timeline.

SECOND-BEST: D. The utility owns the notification; the regulator sets the rules and receives the report.

DISTRACTOR ANALYSIS:
- A) Reporting after lifting hides the event from oversight; this would be correct if the question asked when the final after-action report is due.
- B) Correct: prompt regulatory notification plus an immediate public notice.
- C) Monthly reports cover routine data; this would be correct if the question asked about routine compliance reporting.
- D) The utility is the notifying party; this would be correct if the question asked who sets the notification rules.

TRAP: Merging the public-notice clock with the regulatory-reporting clock.

CONFIDENCE: high

Q17. What is the purpose of adding coagulant in the conventional treatment train?   (difficulty: recall)
[ID: 34111b429b054ef0]
[HASH: sha256:2f8024e8485e7141]
[OBJECTIVE: water:treatment.coagulation]
[PAIR: coagulation-train]
[PREREQ: water:distribution.residual]

A) To raise the pH of the finished water
B) To add fluoride for dental health
C) To kill pathogens in the raw water
D) To destabilise suspended particles so they can aggregate and settle

CORRECT: D

WHY BEST: Coagulant destabilises suspended particles so that flocculation and sedimentation can remove them; it is the chemistry that makes the rest of the train possible.

KEY DISCRIMINATOR: Coagulation is the chemistry that makes particles stick together, which is what downstream flocculation and sedimentation rely on.

SECOND-BEST: A. Disinfection is a separate step that happens later in the train.

DISTRACTOR ANALYSIS:
- A) pH adjustment uses other chemicals; this would be correct if the question asked what lime or soda ash does.
- B) Fluoridation is a separate additive; this would be correct if the question asked about dental-health additives.
- C) Disinfection kills pathogens; this would be correct if the question asked what chlorine or UV does.
- D) Correct: destabilisation of suspended particles.

TRAP: Confusing coagulation (particle destabilisation) with disinfection (pathogen kill).

CONFIDENCE: high

Q18. A raw-water sample is turbid but the particles settle very slowly on their own. What does the operator add first to make settling practical?   (difficulty: application)
[ID: 82abce71147b419a]
[HASH: sha256:71e4e9e57af78c1b]
[OBJECTIVE: water:treatment.coagulation]
[PAIR: coagulation-train]
[PREREQ: water:distribution.residual]

A) Chlorine at the plant outlet
B) Coagulant, followed by gentle mixing so the destabilised particles form floc
C) Powdered activated carbon for taste
D) Sodium hydroxide to raise the pH

CORRECT: B

WHY BEST: Slow-settling particles need destabilisation first: coagulant neutralises the charges that keep them apart, and flocculation grows them into settleable floc.

KEY DISCRIMINATOR: The problem is stability, not taste, pH, or disinfection.

SECOND-BEST: D. pH affects coagulation efficiency, but adding base alone does not make particles settle.

DISTRACTOR ANALYSIS:
- A) Chlorine treats pathogens, not turbidity; this would be correct if the question asked about disinfection timing.
- B) Correct: coagulant plus mixing to form floc.
- C) Carbon removes taste and odour; this would be correct if the question asked about an algal event.
- D) pH adjustment conditions the water for coagulation but does not settle it; this would be correct if the question asked what to optimise before adding coagulant.

TRAP: Picking a downstream or conditioning chemical instead of the destabilising one.

CONFIDENCE: high

Q19. Which conditions favour effective coagulation?   (difficulty: application)
[ID: 623a6fe7d1034378]
[HASH: sha256:f92de629bdd841f1]
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: water:treatment.coagulation]
[PAIR: coagulation-train]
[PREREQ: water:distribution.residual]

A) Adequate mixing energy to disperse the coagulant quickly
B) The highest possible pH regardless of the coagulant type
C) Zero flow through the flocculation basin
D) A dose chosen from jar testing on the current raw water
E) Maximum flow through the filters regardless of floc quality

CORRECT: A, D

WHY BEST: Rapid dispersion and a dose tuned to the actual raw water are the two conditions that make coagulation work; pH matters too, but the listed set requires the two best.

KEY DISCRIMINATOR: Coagulation depends on mixing and dose selection; the distractors describe conditions that would break it.

SECOND-BEST: Not applicable; the remaining options describe conditions that hinder or ignore coagulation.

DISTRACTOR ANALYSIS:
- A) Correct: rapid dispersion is essential.
- B) pH extremes outside the coagulant's range hinder performance; this would be correct if the question asked what to optimise before dosing.
- C) Zero flow means no flocculation; this would be correct if the question asked what ruins coagulation.
- D) Correct: jar testing sets the right dose.
- E) Forcing maximum filter flow bypasses floc quality; this would be correct if the question asked what stresses the filters.

TRAP: Treating flow extremes as acceptable operating conditions.

CONFIDENCE: high

Q20. Classify each action as COAGULATION or POST-COAGULATION in the treatment train.   (difficulty: recall)
[ID: 23b60ebbd4514c5d]
[HASH: sha256:10d4e0c244188439]
[TYPE: table]
[CATEGORIES: Coagulation | Post-coagulation]
[OBJECTIVE: water:treatment.coagulation]
[PREREQ: water:distribution.residual]

ROW) Adding alum to raw water :: Coagulation
ROW) Gentle stirring to grow floc :: Coagulation
ROW) Passing settled water through filters :: Post-coagulation
ROW) Adding chlorine before the clearwell :: Post-coagulation

WHY BEST: Coagulation covers destabilisation and floc growth. Everything downstream — filtration and disinfection — is post-coagulation.

KEY DISCRIMINATOR: Does the step make particles aggregate, or does it act on water that has already been clarified?

DISTRACTOR ANALYSIS:
- Gentle stirring is the row that catches people: it feels like a separate step, but flocculation is part of the coagulation stage.
- Chlorine before the clearwell is disinfection, which is emphatically post-coagulation.

TRAP: Splitting the coagulation stage at the wrong boundary.

CONFIDENCE: high

Q21. Jar tests on today's raw water suggest a coagulant dose of 25 mg/L, but the plant's historical average is 15 mg/L. What is the most defensible action?   (difficulty: analysis)
[ID: c989c8eeab8e43aa]
[HASH: sha256:7709bb535cc0e5ce]
[OBJECTIVE: water:treatment.coagulation]
[PREREQ: water:distribution.residual]

A) Run at 15 mg/L because the historical dose has never failed
B) Run at 25 mg/L, confirm with settled-water turbidity, and review why today's raw water needs more
C) Run at 20 mg/L as a compromise between the two figures
D) Skip coagulation today and rely on filtration alone

CORRECT: B

WHY BEST: The jar test is the direct measurement of what today's water needs; the historical average is a baseline, not a limit. Confirming with settled-water turbidity closes the loop.

KEY DISCRIMINATOR: The current raw water, not the average, determines the dose.

SECOND-BEST: C. A compromise dose satisfies neither measurement and risks both under- and overdosing.

DISTRACTOR ANALYSIS:
- A) The historical average does not describe today's water; this would be correct if the raw water were unchanged.
- B) Correct: follow the jar test and verify.
- C) Averaging two numbers is not a treatment decision; this would be correct if the question asked how to reconcile conflicting jar-test replicates.
- D) Filtration cannot compensate for unsettled floc; this would be correct if the question asked about emergency bypass operation.

TRAP: Letting habit override the direct measurement.

CONFIDENCE: high

Q22. After coagulation and settling, the floc blanket in the clarifier collapses. What is the first thing the operator should check?   (difficulty: application)
[ID: c66fd740115c48fa]
[HASH: sha256:3e10ddfb9ca5d0c8]
[OBJECTIVE: water:treatment.coagulation]
[PREREQ: water:distribution.residual]

A) Whether the billing meters are accurate
B) Whether the finished-water tank is full
C) Whether the coagulant dose still matches the current raw-water quality
D) Whether the filters are due for backwashing

CORRECT: C

CONFIDENCE: high

WHY BEST: A collapsed floc blanket is almost always a dose or raw-water mismatch: changed turbidity, pH, or temperature makes the established dose ineffective, and the blanket loses structure.

KEY DISCRIMINATOR: The blanket's stability depends on the coagulation chemistry upstream.

SECOND-BEST: D. Filter backwash is routine, but it does not explain a blanket collapse.

DISTRACTOR ANALYSIS:
- A) Billing meters are unrelated; this would be correct if the question asked about unaccounted-for water.
- B) Tank level is a storage question; this would be correct if the question asked about supply pressure.
- C) Correct: re-check the dose against current raw water.
- D) Filters sit downstream of the blanket; this would be correct if the question asked why effluent turbidity rose after the blanket collapsed.

TRAP: Looking downstream for a failure that originates in the coagulation stage.

CONFIDENCE: high

Q23. Put the coagulation-stage steps in order.   (difficulty: recall)
[ID: d636b1100de542cb]
[HASH: sha256:bc9fc709327bfa32]
[TYPE: build]
[OBJECTIVE: water:treatment.coagulation]
[PREREQ: water:distribution.residual]

STEP) Rapid mix the coagulant into the raw water
STEP) Gentle mixing to grow microfloc into settleable floc
STEP) Settling in the clarifier to remove the floc blanket
STEP) Filtering the clarified water

WHY BEST: Destabilisation must come first, floc growth second, gravity settling third, and filtration last — each step conditions the water for the next.

KEY DISCRIMINATOR: The order is causal: you cannot grow floc before you have destabilised particles.

DISTRACTOR ANALYSIS:
- Swapping rapid mix and gentle mixing is the common error: they are often spoken of as one step, but dispersion must precede aggregation.
- Placing filtration before settling reverses the train and would blind the filters immediately.

TRAP: Memorising the train as a list instead of a chain where each step depends on the previous one.

CONFIDENCE: high

Q24. What is the reporting deadline for a routine monthly water-quality summary to the regulator?
[ID: 6af6d381f5424720]
[HASH: sha256:42a4af11eaaf45aa]
[OBJECTIVE: water:regulatory.reporting]

A) Whenever the utility finishes compiling the data
B) Within one business day of the last sample
C) By the date the regulator sets for the reporting period, typically early the following month
D) Only when the regulator asks for it

CORRECT: C

WHY BEST: Routine reports follow a fixed regulatory calendar. The deadline is set by the regulator for the reporting period, and missing it is a compliance failure even when the data are good.

KEY DISCRIMINATOR: Routine reporting has a calendar deadline; it is not driven by when the data happen to be ready.

SECOND-BEST: A. One business day applies to acute event reporting, not monthly summaries.

DISTRACTOR ANALYSIS:
- A) "Whenever it is ready" is not a deadline; this would be correct if the question asked about internal drafting.
- B) One day is the acute-event clock; this would be correct if the question asked about a contamination event.
- C) Correct: the regulator's calendar deadline.
- D) Routine reports are standing obligations; this would be correct if the question asked about a one-off data request.

TRAP: Applying the acute-event deadline to routine reporting.

CONFIDENCE: high

Q25. An operator discovers a sampling error that made last month's reported copper result look compliant when it was not. What is the correct reporting action?   (difficulty: application)
[ID: 7117a10e2bb741e0]
[HASH: sha256:b4e58a66418da6c1]
[OBJECTIVE: water:regulatory.reporting]

A) Correct the number in the next monthly report without comment
B) Report the error and the corrected result to the regulator promptly, with the reason for the correction
C) Discard the erroneous sample and report only the corrected sample's result
D) Wait until the next compliance cycle to resample

CORRECT: B

WHY BEST: A reported compliance value that was wrong must be corrected and disclosed: the regulator needs the true result, the cause, and the fix, and silence would hide a potential exceedance.

KEY DISCRIMINATOR: Corrections to reported compliance data are themselves reportable.

SECOND-BEST: C. Resampling is part of the fix, but the erroneous reported value still must be disclosed and corrected.

DISTRACTOR ANALYSIS:
- A) Silent correction hides the error's history; this would be correct if the question asked how to amend an internal draft.
- B) Correct: disclose and correct promptly.
- C) Discarding the sample erases the audit trail; this would be correct if the sample were invalid for a documented, pre-approved reason.
- D) Waiting delays disclosure of a possible exceedance; this would be correct if the question asked when routine resampling occurs.

TRAP: Treating reported data as editable drafts.

CONFIDENCE: high

Q26. Which items must a utility include in its consumer confidence report?   (difficulty: application)
[ID: 54cf384d025f47be]
[HASH: sha256:4f1f6fa0e99b43ae]
[TYPE: multi]
[SELECT: 2]
[OBJECTIVE: water:regulatory.reporting]

A) The source of the drinking water
B) Detected contaminants and their levels against the standards
C) The names and salaries of plant operators
D) The utility's marketing budget
E) The number of boil-water notices issued during the year

CORRECT: A, B

WHY BEST: The consumer confidence report is about what is in the water and where it came from: source, detected contaminants, levels, and compliance against standards.

KEY DISCRIMINATOR: The report informs customers about water quality, not about the utility's finances or staffing.

SECOND-BEST: Not applicable; the remaining options describe internal or financial information.

DISTRACTOR ANALYSIS:
- A) Correct: the source is a required element.
- B) Correct: detected contaminants and their levels.
- C) Staff names are not water-quality information; this would be correct if the question asked about public-records requests.
- D) Marketing budgets are internal; this would be correct if the question asked about utility transparency reports.
- E) Notices are relevant health information but are reported through other channels; this would be correct if the question asked what appears in a public-health notification summary.

TRAP: Including anything the utility knows rather than what the report is legally for.

CONFIDENCE: high

Q27. Sort each item into REPORT or DO NOT REPORT in the consumer confidence report.   (difficulty: recall)
[ID: 37760004cf3e4f35]
[HASH: sha256:75d053f1a5706b06]
[TYPE: dnd]
[CATEGORIES: Report | Do not report]
[OBJECTIVE: water:regulatory.reporting]

ITEM) Detected lead level at the 90th percentile :: Report
ITEM) The source of the drinking water :: Report
ITEM) A vendor's internal pricing schedule :: Do not report
ITEM) The plant manager's home address :: Do not report

WHY BEST: The report carries water-quality facts customers need: detected contaminants, compliance, and source. It carries no personnel, pricing, or internal business data.

KEY DISCRIMINATOR: Is the fact about the water customers drink, or about the utility's internal affairs?

DISTRACTOR ANALYSIS:
- The 90th-percentile lead figure is the one a reader might skip: it is a statistical reporting value, not a single sample, and it is exactly what the rule requires.
- Source is easy to misclassify as background, but it is a required report element.

TRAP: Judging reportability by sensitivity rather than by the report's legal scope.

CONFIDENCE: high

Q28. A utility's annual report shows every contaminant below its standard, yet the state asks for a corrective action plan. What is the most likely reason?   (difficulty: analysis)
[ID: c1c714fb8df4438a]
[HASH: sha256:c45eb43c3662136b]
[OBJECTIVE: water:regulatory.reporting]

A) The state is requiring action on a monitoring or reporting violation even though the values complied
B) The state requires a plan whenever any report is filed
C) The report's formatting did not match the state's template
D) A customer complained about the report's readability

CORRECT: A

WHY BEST: Compliance with the numerical standards does not equal compliance with the monitoring and reporting rules. A missed sample, a late report, or an uncorrected error can trigger a corrective action plan on its own.

KEY DISCRIMINATOR: The plan can be about the process of reporting, not the values reported.

SECOND-BEST: C. Formatting matters, but a corrective action plan is reserved for substantive violations, not cosmetic ones.

DISTRACTOR ANALYSIS:
- A) Correct: process violations trigger plans independently of values.
- B) Filing a report does not automatically require a plan; this would be correct if the question asked about routine follow-up.
- C) A template mismatch is a minor administrative issue; this would be correct if the question asked why a report was returned for revision.
- D) Readability is not a regulatory trigger; this would be correct if the question asked about public engagement.

TRAP: Assuming the numbers are the only thing regulators act on.

CONFIDENCE: high

Q29. A utility missed the monthly report deadline by three days because its data system was down. Explain what the utility must do, and why silence is not an option.   (difficulty: analysis)
[ID: 9126ff111d034002]
[HASH: sha256:a43e71b089280ff7]
[TYPE: short]
[OBJECTIVE: water:regulatory.reporting]
[PREREQ: water:distribution.residual, water:notification.boil]

MODEL: The utility must notify the regulator of the missed deadline as soon as it is known, explain the system failure, and submit the completed report with a corrective step to prevent recurrence, such as a manual backup process. Silence is not an option because a late report is a compliance event regardless of the reason: the regulator cannot distinguish a technical failure from concealment if it is not told, and the delay itself must be on the record.

RUBRIC:
- Names prompt notification of the missed deadline as the required first step
- States that the late submission is a compliance event even with an excuse
- Identifies a corrective action to prevent recurrence

TRAP: Treating an unavoidable technical failure as a reason the deadline does not apply.

CONFIDENCE: high

Q30. An operator finds a 2019 sampling record that was never reported to the regulator. What should be done with it now?   (difficulty: application)
[ID: e011cd2cc2d144bf]
[HASH: sha256:187d412f51dfe27f]
[OBJECTIVE: water:regulatory.reporting]
[PREREQ: water:distribution.residual, water:notification.boil]

A) Report the discovery and the unreported result to the regulator, with the reason it was missed and the corrective step taken
B) File the record silently with the current report so the history is complete
C) Discard the record because it is too old to matter
D) Report only if the 2019 result would have exceeded a standard

CORRECT: A

WHY BEST: An unreported compliance sample is a reporting violation whether or not the value exceeded a standard. Disclosure of the discovery, the result, and the fix is the only defensible path.

KEY DISCRIMINATOR: The violation is the missing report itself, not the value it carried.

SECOND-BEST: D. The value matters for whether an exceedance occurred, but the omission must be disclosed regardless.

DISTRACTOR ANALYSIS:
- A) Correct: disclose the discovery and the result.
- B) Silent filing hides the omission; this would be correct if the question asked how to merge an internal archive.
- C) Age does not erase a compliance obligation; this would be correct if the question asked about records retention limits.
- D) Disclosing only noncompliant values reverses the rule; this would be correct if the question asked what the regulator will scrutinise first.

TRAP: Letting the magnitude of the hidden value decide whether to disclose the omission.

CONFIDENCE: high
