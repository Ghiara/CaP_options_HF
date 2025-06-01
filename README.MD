# Cap-options: TODO

- [Cap-options: TODO](#cap-options-todo)
  - [1. Introduction](#1-introduction)
  - [2. Installation](#2-installation)
  - [3. Overview](#3-overview)
  - [4. Run the code with interaction](#4-run-the-code-with-interaction)
    - [4.1 Interact in the terminal](#41-interact-in-the-terminal)
    - [4.2 Test pre-trained agent](#42-test-pre-trained-agent)
    - [4.3 Teach your robot](#43-teach-your-robot)
  - [Repository Structure](#repository-structure)
  - [Known Weaknesses](#known-weaknesses)
  - [Acknowledgements](#acknowledgements)
  - [clis](#clis)

## 1. Introduction

Approaches that use LLMs to generate robot control code have become increasingly popular in robotics. Such approaches typically build on a fixed API of perception and control primitives, and handcrafted prompts that contain examples of how these API functions can be called in response to natural language instructions. The capabilities of the agent are determined completely by the API and these prompts, as such these are the primary avenues for altering the agents behaviour if it doesn't align with our expectations. We propose to _learn_ from human feedback (or environment feedback, if available) by endowing the agent with a memory, and provide a simple CLI to demonstrate this approach in a block-stacking environment.

You can _teach_ the agent new skills by telling it what you want it to learn, and then providing multiple tasks to test whether it has successfully learned the skill. Most of the time, you will have to provide corrections to get to the right result. With more corrections, the skill becomes increasingly refined to match the expectations we have of it, i.e. the agent does what you want more consistently. Once you've taught the agent a behaviour, it may use it to more easily solve downstream tasks.

## 2. Installation

- 2.1 Clone the repository:

```bash
git clone https://github.com/maxf98/cap_options
```

Create the conda environment (we recommend using mamba, creating the env with conda failed for us).

```bash
cd cap_options
mamba env create -n cap-options -f environment.yml

conda activate cap-options

pip install streamlit # in case you want to use Web UI
```

- 2.2 Add an OpenAI API key as a python environment variable to run experiments.
For example, you can add the following line to .bashrc, .zshrc, or .bash_profile.

```bash
export OPENAI_API_KEY=<your_key_here>
```

<!-- Also add `export PYTHONPATH="/path/to/your/project/root:$PYTHONPATH"` if you want to run the agent modules individually (e.g. to interact with skill library or task setup). -->


## 3. Overview

A [**skill**](agents/model/skill.py) is a python function, which the agent calls when writing code to solve a [**task**](task/task_and_store.py). An [**example**](agents/model/example.py) is a pair of a natural language instruction and the python code (which calls different skills) used to successfully respond to the instruction. When presented with a new instruction, the agent is more likely to be able to respond to it correctly if it has examples of similar instructions. A skill represents the part of the behaviour which the agent should not vary in downstream tasks, whereas the example code demonstrates _how_ and _when_ to call a skill (i.e. how to parameterise it, how to use its returns, what other functions are often called around it, ...).

As the number of skills and examples (i.e. number of behaviours the robot is capable of) grows, it becomes less feasible to put them into a single fixed prompt, necessitating some form of instruction-specific retrieval of skills and examples. Even when they all fit into a prompt, too many skills and examples crowd out the useful information.

Core to our approach is an interactive skill _teaching_ mechanism, by which we first describe to the agent the skill we want it to learn, and then provide tasks which test whether this skill _does what we want it to do_, for each of which we may provide corrective feedback to help it get there: "If the skill can be used to successfully solve all these tasks, then we've successfully learned this skill." In this way, we subsume many of the tasks of the RL engineer: the user interactively determines what the agent is capable of, proposes _reasonably_ difficult tasks, and provides feedback to alter the agents behaviour. The goal was to create a natural language UI for _teaching_ robots new behaviours, ultimately for Teleoperation or End-user programming.

## 4. Run the code with interaction

### 4.1 Interact in the terminal

We provide a simple CLI, which you can run with:

```bash
python main.py --memory_dir "baseline"
# [1] Learn a new skill || [2] Attempt a task || [3] Run past example

# for [2]:
    [1] Generate new task
    [2] Use stored environment state
    [3] Use predefined task
    # for [3] + stack-blocks
        [1] Success
        [2] Give up
        [3] Re-run
        [4] Try again
        [5] Apply hint
        [6] Feedback & iterate 
```

This will interactively take you through _teaching_ the agent. `--memory_dir` determines the directory in [memory](memory) which contains the agents memory, and as such determines what the agent is capable of. 
You can use the [baseline](memory/baseline/) or [trained](memory/trained) (larger library of skills and examples) agents, or you can initialise a new one by providing the name of the directory.



### 4.2 Test pre-trained agent
Alternatively, you can test the pretrained agent capabilities on some [predefined tasks](task/__init__.py) by running:

```bash
python main.py --memory_dir "trained" --task "construct-smiley-face"
```

A task provides the initial environment setup and the description of what you want the agent to do. Determining whether or not the agent was successful is left up to the user. [task/**init**.py](task/__init__.py) lists the valid task identifiers, and you can find the tasks (and add new ones) in [task/tasks.py](task/tasks.py). You can also generate one from a prompt (e.g. "6 big red blocks and 2 small green ones") in the interactive CLI.


### 4.3 Teach your robot

A good example to get an understanding of skill learning is to teach the agent to build a "zigzag tower". First, see what a zigzag tower is by running:

```bash
python main.py --memory_dir "trained" --task "build-zigzag-tower"
```

Then see what the untrained agent does in response to the same instruction.

```bash
python main.py --memory_dir "baseline" --task "build-zigzag-tower"
```

Now enter the interactive CLI with the untrained agent, so you can teach it how to do it right.

```bash
python main.py --memory_dir "baseline"
```

First you need to declare that you want to "learn a skill". Then you provide a description of the skill you want to learn (which generates a python function header, i.e. the skill spec). Then you set up the task using the identifier `"build-zigzag-tower"`, and then you provide feedback on what the agent is doing until it looks the way you want it to look (which can be whatever you want). Once you have done this, you can test the agent on the same task, to observe the updated behaviour.

```bash
python main.py --memory_dir "baseline" --task "build-zigzag-tower" --debug True
```

You could now learn another skill on top of this one, for example building a "zigzag wall", by placing multiple zigzag towers next to one another. The point is that the agent now performs this behaviour the way you expect it to, doesn't lose this ability as you teach it more behaviours (as it might with handcrafted prompts), and that this can be achieved interactively.

[data](data) contains some examples of learned behaviours. We included some [videos of failure modes on the simple task of stacking blocks](data/stack_blocks) with the baseline agent, which you can reproduce by running

```bash
python main.py --memory_dir "baseline" --task "stack-blocks"
python main.py --memory_dir "baseline" --task "stack-blocks-induce-failure"
```

Sometimes it gets it right too, and if we altered the prompt to give it more information from the outset this would solve the problem as well. Run it a few times to get a sense of how noisy LLM code generation can be. Then run the same tasks with the trained agent to see the corrected (consistent) behaviour. The point is that you can get from "baseline" to "trained" purely via natural language interaction, and interactive task solving.

You can run examples in the simulator by selecting "Run past examples" in the interactive CLI. Put in a task, and it will retrieve the most similar experiences the agent has stored, which can then be rolled out in the environment. (DISCLAIMER: some of these may not run properly, for a variety of reasons. If you generate new ones, this will work properly.) This is useful for inspecting the agents memory.


All commandlines for agent with trained memory are listed here:
```bash
python main.py --memory_dir "trained" --task "place-green-next-to-yellow"
python main.py --memory_dir "trained" --task "build-house"
python main.py --memory_dir "trained" --task "place-blocks-diagonally"
python main.py --memory_dir "trained" --task "stack-blocks"
python main.py --memory_dir "trained" --task "stack-blocks-big-to-small"
python main.py --memory_dir "trained" --task "stack-blocks-induce-failure"
python main.py --memory_dir "trained" --task "build-cube"
python main.py --memory_dir "trained" --task "build-block-pyramid"
python main.py --memory_dir "trained" --task "build-jenga-layer"
python main.py --memory_dir "trained" --task "build-jenga-tower"
python main.py --memory_dir "trained" --task "build-jenga-tower-long-description"
python main.py --memory_dir "trained" --task "construct-smiley-face"
python main.py --memory_dir "trained" --task "construct-smiley-face-long-description"
python main.py --memory_dir "trained" --task "build-zigzag-tower"
python main.py --memory_dir "trained" --task "build-zigzag-tower-long-description"
python main.py --memory_dir "trained" --task "place-blue-blocks-around-red-block"
```

## Repository Structure

[agents] contains the LLM agent modules for [generating robot policy code](agents/action), for [setting up the environment](agents/environment), and for [skill parsing](agents/skill) (i.e. mapping natural language skill descriptions to python function headers). [agents/memory](agents/memory) contains all the memory related modules, which rely on [ChromaDB](https://www.trychroma.com), used for managing the skill and example libraries (as well as storing environment configs). [agents/model](agents/model) contains the relevant data classes (Skill, TaskExample, EnvironmentConfiguration, and InteractionTrace), for pickling and basic convenience functions.

[environments](environments) contains all the environment-related code. This could be simplified substantially, or ideally replaced with something better. This repository builds on the [Cliport](https://github.com/cliport/cliport) repo, primarily for the accompanying Ravens benchmark, though there is a lot of unused code leftover from it (mostly in this [environments](environments) folder and [utils/general_utils]([utils/general_utils])).

[memory](memory) contains the memories of agents trained based on our approach, storing skill and example libraries, as well as interaction traces. Each subfolder (e.g. [memory/baseline]) corresponds with a single agent. You can inspect the skill libraries (skills are saved in a readable manner) and manually delete, add or edit skills. This might be useful if you want to simply test the agents abilities with a larger number of core primitives, or to remove mistakenly saved skills. Examples are also readable, though they are a bit harder to inspect since we're not giving them meaningful names right now.

[data](data) contains some examples of learned behaviours.

[prompts](prompts) contains all the prompts we used, modelled as python fstrings.

[scripts](scripts) contains some attempts at interpreting the agent memories, as well as an attempt at automatically testing whether an environment configuration is equal to another one (though this is more difficult than you might think – would also require some "softer" semantic approach, e.g. based on a VLM-verifier).

[utils](utils) contains a number of necessary supporting functions.

The main agent code is in [cap_optioner.py](cap_optioner.py), and [main.py](main.py) is the entrypoint for the app.

## Known Weaknesses

The point of this repo was to create a natural language based interface to _teach_ robots, similar to the interfaces that are being created in many other contexts. We describe some of the main weaknesses we encountered in implementing our current agent.

1. GUI - the CLI limits the interactions that can be made available to the user, and is generally unwieldy. For instance, sometimes the policy code generated by the LLM gets worse from one iteration to the next, and right now we don't have a function to step back to the last attempt. A GUI would also provide a good way to inspect the agents memory, for example by playing videos of past examples/interactions, and providing an overview of the skills the agent has learned.

2. Environment - our environment is quite limited, when technically this approach should enable arbitrary, open-ended behaviours in more meaningful scenarios, provided the right set of base control and perception primitives. Thanks to our context-dependent retrieval of skills and examples, we can provide a larger number of base control and perception primitives.

3. Control APIs - the robotic arm is currently controlled with a waypoint-based inverse kinematics controller. This makes certain end-effector motions (e.g. along a straight line along the horizontal plane, or end-effector rotations not along z-axis) difficult to achieve, and made many interesting behaviours impossible from the outset. The gripper included in the Ravens benchmark doesn't seem to work very well either.

4. Interpretability - we _could_ talk to the agent about what it is capable of, by interacting with its memory (e.g. asking it about what tasks it has solved previously, and what the environment looked like), though we have not implemented it. _Hints_ are one instance of this – while providing feedback on generated policy code, we make it possible for the user to tell the robot to use a specific skill (see [agents/action.py](agents/action.py) – revise_code_with_feedback).

5. Skills that call other skills – in some cases, we would like to retain the flexibility of _generating_ code. The point of a skill is to scope a user's feedback and knowledge gained from successful interaction to a specific behaviour & context, so instead of writing the function body of a skill, we could generate it every time with learned examples and instructions. See [parse_location_description skill](memory/trained/skill_library/skills/parse_location_description/code.py) in the trained agent for a simple example of where feedback would still be useful, but writing hardcoded function code is infeasible. This turns skills into [_Language Model Programs_](https://code-as-policies.github.io).

## Acknowledgements

- [Cliport](https://github.com/cliport/cliport) – for the basic Ravens benchmark setup
- [Code-as-Policies](https://github.com/google-research/google-research/tree/master/code_as_policies) - code-generation for robotics
- [VOYAGER](https://github.com/MineDojo/Voyager), [Expel](https://github.com/LeapLabTHU/ExpeL), [DROC](https://github.com/Stanford-ILIAD/droc) - provided the inspiration for our code base, and the concept of LLM-Agent -_learning_ by reading and writing to memory based on experience



## clis

ignore changes in baseline/trained memory
```bash
git ls-files -z -- memory/baseline memory/trained \
| xargs -0 git update-index --skip-worktree --
```

recover update tracking in baseline trained 
```bash
git ls-files -z -- memory/baseline memory/trained \
| xargs -0 git update-index --no-skip-worktree --

```