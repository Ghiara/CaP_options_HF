## CaP-Learner

1. [Introduction](#Introduction)

2. [Installation & Setup](#Installation)

3. [Overview](#Overview)

4. [Repository Structure](#RepositoryStructure)

5. [Interaction](#Interaction)

6. [Future Work](#FutureWork)

7. [Acknowledgements](#Acknowledgements)

## Introduction

Approaches that use LLMs to generate robot control code have become increasingly popular in robotics. Such approaches typically build on a fixed API of perception and control primitives, and handcrafted prompts that contain examples of how these API functions can be called in response to natural language instructions. The capabilities of the agent are determined completely by the API and these prompts, as such these are the primary avenues for altering the agents behaviour if it doesn't align with our expectations. We propose a simple alternative mechanism for _learning_ based on _Retrieval-augmented Generation_, i.e. endowing the agent with a memory.

We focus on _learning from human feedback_, inspired by methods in Teleoperation and End-user Programming: adaptation to a specific environment requires environment experts. Also, LLM/VLM self-correction just doesn't work that well yet. A human operator can _teach_ the agent _skills_ by setting up _tasks_, and then providing feedback. We test this idea in a simple pick-and-place environment.

## Installation

Clone the repository:

```bash
git clone https://github.com/maxf98/cap_options
```

Create the conda environment (we recommend using mamba, creating the env with conda failed for us).

```bash
cd cap_options
mamba env create -n cap-options -f environment.yml
```

You will need to add an OpenAI API key as a python environment variable to run experiments.
For example, you can add the following line to .bashrc, .zshrc, or .bash_profile.

```bash
export OPENAI_API_KEY=<your_key_here>
```

## Overview

A **skill** $z$ is a python function. The agent can use skills to solve a task, by generating python code $c$ that calls these skills.

An **example** $(l, s_0, c, s_T)$ is a mapping from a task description $l$ and initial environment state $s_0$ to python code $c$ that _succesfully_ generates the desired final state $s_T$.

A **task** is a pair $(l, s_0)$ of instruction and initial environment state. Tasks can be initialised in three ways:

1. (Default) on-the-fly: an LLM generates environment setup code from a natural language description (see [agents/environment.py](agents/environment.py))
2. From a previously encountered stored state (i.e. **EnvironmentConfiguration** - [agents/model/environment_configuration.py](agents/model/environment_configuration.py))
3. By writing the task setup code yourself (see [utils/sample_tasks.py](utils/sample_tasks.py))

We focused on on-the-fly task generation, with the goal of creating a flexible and interactive user experience.

An **agent** is endowed with a **memory**, which stores the skills and examples available to the agent (e.g. memory/baseline), and determines its capabilities. We also store trajectories of human-agent-environment interactions for analysis purposes (though we didn't get around to using these), and environment configurations which we can use to initialise downstream tasks (also not fully set up yet).

When presented with a novel task $(l, s_0)$ we retrieve similar previously encountered tasks (based on cosine-similarity of the embeddings of task descriptions). We accomplish this by interactively setting up _tasks of intermediate difficulty_, i.e. tasks that the agent can't yet solve, but is capable enough to solve with feedback. Learning can then happen simply by storing successful examples (i.e. adding successful $(l, s_0, c, s_T)$ tuples based on interaction), or by simultaneously learning skills. There are many reasons you might want to learn skills too, but the most important one is that when the agent calls a skill in a generated code $c$, it will **not** vary the behaviour encoded in the skill, enabling deliberate integration of user knowledge.

## Interaction

An agent is initialised from a given memory directory (e.g. "baseline"). If the directory doesn't exist yet, it is initialised with the base set of skills (i.e. the basic control and perception primitives) and examples. You start the interaction by calling

```bash
agent.run()
```

The interaction is then structured as follows:

1. learn skill (y/n)
2. attempt task (provide task description and initial environment state description)
3. iteratively provide feedback on agent performance

If you choose to learn a skill, you will be prompted to provide a natural language description of what the skill is supposed to accomplish, from which a python function header is generated, which you can iteratively refine. You then provide tasks which use this skill, which the agent tries to solve (with your feedback).

If you don't learn a skill (i.e. select no in step 1), you are just attempting to solve a task with the agents current set of skills and examples. This would be useful for testing a trained agent on a given set of tasks, or providing a baseline of learning without skills.

If you want to inspect an agents memory by rolling out previously _learned_ (task, behaviour) pairs, you can use

```bash
agent.run_past_example()
```

which provides a simple CLI for retrieving these (along with their environment setup) and rolling them out. You can initialise an example agent trained with some more skills from the memory/trained directory, i.e.

```bash
agent = CapOptioner(memory_dir="trained")
```

Some examples of behaviours you can view with `agent.run_past_example()` are:

- "build a jenga tower"
- "build a (w*d*h) block structure at (pose)"
- "build a zig-zag tower"
- "build a house"
- "stack the blocks at (pose)"
- "put (blockA) on the (side) side of (blockB)"
- ...

You can also just set up a task and issue these prompts independently from rolling out past examples, though each skill only works within certain constraints (i.e. from some set of initial states).

## Repository Structure

This repository builds on the [Cliport](https://github.com/cliport/cliport) repo, primarily for the accompanying Ravens benchmark, though there is a lot of unused code leftover from it (mostly in [environments](environments) folder and [utils/general_utils]([utils/general_utils])).

[agents] contains the LLM agent modules for [generating robot policy code](agents/action), for [setting up the environment](agents/environment), and for [skill parsing](agents/skill) (i.e. mapping natural language skill descriptions to python function headers). [agents/memory](agents/memory) contains all the memory related modules, which rely on [ChromaDB](https://www.trychroma.com), used for managing the skill and example libraries (as well as storing environment configs). [agents/model](agents/model) contains the relevant data classes (Skill, TaskExample, EnvironmentConfiguration, and InteractionTrace), for pickling and basic convenience functions.

[environments](environments) contains all the environment-related code. This could be simplified substantially, or ideally replaced with something better.

[memory](memory) contains the memories of agents trained based on our approach, storing skill and example libraries, as well as interaction traces. Each subfolder (e.g. [memory/baseline]) corresponds with a single agent.

[prompts](prompts) contains all the prompts we used, modelled as python fstrings.

[scripts](scripts) contains some attempts at interpreting the agent memories, as well as an attempt at automatically testing whether an environment configuration is equal to another one (though this is more difficult than you might think – would also require some "softer" semantic approach, e.g. based on a VLM-verifier).

[utils](utils) contains a number of necessary supporting functions:

- [utils/base_examples.py](utils/base_examples.py) : the base set of examples a new agent is initialised with. A simple text file would probably have been a better choice.
- [utils/cap_utils.py](utils/cap_utils.py) : the code to execute LLM-written code in an environment - involves adding learned skills to the environment
- [utils/core_primitives.py](utils/core_primitives.py) : the base set of skills a new agent is initialised with.
- [utils/core_types.py](utils/core_primitives.py) : types the agent should adhere to when generating code. In retrospect, this may have hampered the agents performance somewhat, as well as increasing initial engineering overhead slightly. For example, we introduce a 'Point3D' class, which could have also simply been represented as a numpy array – in order to use functions the agent is familiar with from pretraining to manipulate Point3Ds it needs to first convert to np array...
- [utils/llm_utils](utils/llm_utils) : functions that call the openAI API, i.e. LLM calls
- [utils/sample_tasks.py](utils/sample_tasks.py) : an example of a handwritten task initialisation.
- [utils/task_and_store.py](utils/task_and_store.py) : wraps the Ravens Task class, both to enable a natural language based environment initialisation, and to enable storing/restoring of environment state from EnvironmentConfigurations.

[main.py](main.py) contains the main agent running code, as well as _most_ of the logic for the user interaction.

## Future Work

The point of this repo was to create a natural language based interface to _teach_ robots, similar to the interfaces that are being created in many other contexts. We motivate this with Moravec's paradox: robots are very bad at things that are trivial for any human, so any human could act as an effective teacher, provided the right interface.

The interface we've created is still pretty bare-bones, and serves more as a proof-of-concept. Effective deployment would require a GUI, as well as a more interesting environment (e.g. [Nvidia Isaac Orbit](https://isaac-orbit.github.io)) and base set of skills (e.g. more sophisticated control algorithms), as well as improvements to the basic interaction, some of which we outline below.

1. GUI - the CLI limits the interactions that can be made available to the user, and is generally unwieldy. For instance, sometimes the policy code generated by the LLM gets worse from one iteration to the next, and right now we don't have a function to step back to the last attempt. A GUI would also provide a good way to inspect the agents memory, for example by playing videos of past examples/interactions, and providing an overview of the skills the agent has learned.

2. Environment - our environment is quite limited, when technically this approach should enable arbitrary, open-ended behaviours in more meaningful scenarios, provided the right set of base control and perception primitives. Thanks to our context-dependent retrieval of skills and examples, we can provide a larger number of base control and perception primitives.

3. Control APIs - the robotic arm is currently controlled with a waypoint-based inverse kinematics controller. This makes certain end-effector motions (e.g. along a straight line along the horizontal plane, or end-effector rotations not along z-axis) difficult to achieve. The gripper included in the Ravens benchmark doesn't seem to work very well either.

4. Interpretability - we _could_ talk to the agent about what it is capable of, by interacting with its memory (e.g. asking it about what tasks it has solved previously, and what the environment looked like), though we have not implemented it. _Hints_ are one instance of this – while providing feedback on generated policy code, we make it possible for the user to tell the robot to use a specific skill (see [agents/action.py](agents/action.py) – revise_code_with_feedback).

## Acknowledgements

- [Cliport](https://github.com/cliport/cliport) – for the basic Ravens benchmark setup
- [Code-as-Policies](https://github.com/google-research/google-research/tree/master/code_as_policies) - code-generation for robotics
- [LoHoRavens](https://github.com/Shengqiang-Zhang/LoHo-Ravens) - for task inspiration
- [CapRavens](https://github.com/Flakeeeet/capravens) - was the basis for my thesis
- [VOYAGER](https://github.com/MineDojo/Voyager), [Expel](https://github.com/LeapLabTHU/ExpeL), [DROC](https://github.com/Stanford-ILIAD/droc) - provided the inspiration for our code base, and the concept of LLM-Agent -_learning_ by reading and writing to memory based on experience
