# product-ordering
Master's thesis project for OTH / Internship project for M2 ICS at ISIMA

## PDDL to ASP translator
This Python script translates a planning problem into a logic program. The planning problem has to be given in PDDL representation. PDDL stands for Planning Domain Definition Language and is the de-facto standard for expressing classical planning problems. The script takes two files, the PDDL domain file and the PDDL problem instance file, as an input. Its result is an LP-file, which describes the problem using the declarative programming paradigm ASP (Answer Set Programming). 
The computation of a planning problem results in a sequence of actions (plan). Note that for the translation the length of the sequence, the number of timesteps, has to be given, too.

```
python src/translator/translator.py <domain_file> <problem_file> <timesteps>
```
