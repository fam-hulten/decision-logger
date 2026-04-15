# [2026-04-15] Recall Service äger SRS-state

## Context
Vi diskuterade var SRS-logiken (spaced repetition) ska leva. Två alternativ:
- Concepta äger allt (innehåll + repetitionsdata)
- Recall Service äger repetitionsdata, Concepta äger innehåll

## Decision
Recall Service ansvarar för SRS-state. Concepta är "vad som lärs", Recall är "hur det lärs".

## Rationale
- Single responsibility – varje tjänst har en tydlig uppgift
- Concepta kan återanvändas av fler appar utan SRS-overhead
- Recall är utbytbart (FSRS vs SM-2 vs Leitner) utan att påverka Concepta
- Skalar bättre för appar utöver Studywise (Spark Progress, etc.)

## Status
✅ Accepted

## Tags
architecture, recall, srs, concepta
