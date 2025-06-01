Some minor points needs to be addressed:

1. flag: change from `memory-dir` to `memory_dir`, otherwise raise error in feeding hyperparameters
2. I'am a little bit confusing about the options' meaning when interact with the robot, for example:

when I run the code `python main.py --memory_dir "baseline" 
there are three options:

[1] Learn a new skill || [2] Attempt a task || [3] Run past example

learn a new task is easy to understand, but what the meaning and difference between option 2 and 3?

Then when I select [2], there are options listed here:

   [1] Generate new task

   [2] Use stored environment state

   [3] Use predefined task

what meaning of option 2 `use stored environment state`??

Then I select [3] and type task descriptor `stack-blocks` in the terminal, when the task finished, it shows:
   
   [1] Success

   [2] Give up

   [3] Re-run

   [4] Try again

   [5] Apply hint

   [6] Feedback & iterate 

option 1,2,6 is clear, but I'm not sure what 3, 4, 5 actually meaning?

As far as I attempt, `re-run` seems use existing code plan to direct run in the task, right?

and `try again` means we use gpt to regenerate code and deploy in the task, right?

what is difference between `apply hint` and give `feedback`?

`give up` means the skill will not be saved in the memory, right?




Therefore I think a brief explanation in either terminal call or in the readme is necessary
for example, something like: 

re-run: run code plan without re-generating

try-again (or another nickname: re-generate): re-generate code plan then deploy

apply hint: e.g., what and when to apply hint etc...

in the README.md file it would be nice if you can list the options and corresponding explanation

| Options | Explanation |
|-----------------------|--------------------------------------------------|
| level 1 | |
| [1] Learn a new skill | option to interactive learn and add a new skill in the memory library |
| [2] ...   | ... |
| [3] ...   | ... |
| level 2  |  |
| [1][1] ..   | ... |
| [1][n] ..   | ... |
| [2][3] Use predefined task   | use pre-defined tasks by typing task descriptor, e.g., `stack-blocks` |
| level 3  |  |
| [1] success | the skills is fully tested and success perform all tasks, can be saved in memory library |