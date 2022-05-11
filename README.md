# product-ordering
The Product Ordering problem is a widespread planning problem in the Beverage and Liquid Food industry. As my master's thesis project for OTH as well as internship project for M2 ICS at ISIMA I take a closer look at this problem. Therefore, I describe it formally. In cooperation with a stakeholder, we capture all side constraints and optimization goals. Then, I come up with different approaches of solving the problem. A special focus lays on Answer Set Programming, a declarative programming paradigm for solving combinatorial optimization problems. The different approaches are illustrated in the following listing:

Product Ordering Problem  
Planning problem; combinatorial (optimization) problem  
|  
- Modelling in PDDL  
  Planning Domain Definition Language; de-facto standard language for expressing classical planning problems  
  |  
  - Off-the-shelf: Computing with the help of an efficient PDDL solvers  
  |  
  - Answer Set Planning: Translating the planning problem into a logic program and computing it with the help of an answer set solver  
|  
- Modelling as logic program  
  Answer Set Programming; modern knowledge representation language with a high degree of elaboration tolerance; computing with the help of an answer set solver  
|  
- Formulation as an ILP  
  Integer Linear Programming; common approach for solving combinatorial optimization problems; computing with the help of a MIP solvers  
|  
- A* algorithm  
  [TODO]  

This repository contains:
- PDDL to ASP translator
- Implementation of different approaches (will be included in the README soon)
- Computational experiments (will be included in the README soon)
- Evaluation of the previous production planning (will be included in the README soon)


## PDDL to ASP translator
This Python script translates a planning problem into a logic program. The planning problem has to be given in PDDL representation. PDDL stands for Planning Domain Definition Language and is the de-facto standard for expressing classical planning problems. The script takes two files, the PDDL domain file and the PDDL problem instance file, as an input. Its result is an LP-file, which describes the problem using the declarative programming paradigm ASP (Answer Set Programming). 
The computation of a planning problem results in a sequence of actions (plan). Note that for the translation the length of the sequence, the number of timesteps, has to be given, too.

```
python src/translator/translator.py <domain_file> <problem_file> <timesteps>
```
