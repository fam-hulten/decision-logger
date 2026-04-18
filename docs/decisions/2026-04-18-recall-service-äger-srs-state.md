# [2026-04-18] Recall Service äger SRS-state

## Context
Vi diskuterade var SRS-logiken (spaced repetition) ska leva. Två alternativ: Recall Service eller Concepta.

## Decision
Recall Service hanterar all SRS-state (ease factor, interval, repetitions), inte Concepta.

## Rationale
Enkelt att reasona om. Skalar bättre för fler appar. Separation of concerns - Concepta för learning content, Recall för training state.

## Status
Accepted

## Tags
architecture, recall, srs
