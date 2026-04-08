In this exercise, there are four Python functions that are aiming to solve the same problem. 

Problem: Given an array of float numbers, build a Binary Search Tree (VST) by inserting that element into the tree. 

As you may know, in each tree in Binary Search Tree (BST), the left (right) child has a value less (greater) than the root node.

The original code is under `bst_human.py` written. 

In the `bst_agent_assisted.py`, we have copied the human code into the prompt and have asked the Composer 2 (code agent) to write the code that is more efficient and readable. 

Prompt: Paste `bst_human.py` in the prompt + add: "Can you improve this code with regards to performance while keeping it as readable as possible?"

In the `bst_human_in_the_loop.py`, we have aimed to describe the problem only with prompt and not using code to guide the agent through iterative feedbacks in two steps (since the problem is easy to solve). 

Initial Prompt : Given an array of float numbers, build a Binary Search Tree (VST) by inserting that element into the tree. Make sure to make the code have readableílity while make it perform well on larger arrays.


Prompt 1 : Can you include a class for the BST itself? 
Prompt 2: This insertion function is a bit complicated as we speak since you are not calling it recursive, can we get away these while True loops can you make it another way? Agent answers that recursive function will sacrifice too much of the performance. The engineer stops and keeps the code as final.`


In the `bst_agentic`, we have tried to use human prompts but let the agent automatically solve the problem without any feedback in the intermediate steps. 

Prompt: I want you to write a simple Binary Search Tree function In Python that accepts an array and can insert the elements into the array and prints a viz of the tree in the prompt line. Don’t look at the other files and any other resources in this repository. Just implement it from your own context here. The BST needs to accept an array and build the tree. Consider readability and performance at the same time and make sure the code runs correctly with an input.