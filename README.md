# NOTE

This is the second and the last part of my _AI learning process_. This contains the workflow patterns required to build an AI assistant. Important workflow patterns like __Prompt Chaining__, __Routing__ and __Parallelization__ are covered here.

> All the workflow patterns are based on a Calendar Assistant Example.<br>
> Almost all the files contain logging library for better understanding and processing.<br>

# FILES

-*learningPromptChaining.py* - 201 lines - 3 API CALLS per run

-*learningRouting.py* - 235 lines - 2 API CALLS per run

-*learningParallelization.py* - 134 lines - 2 API CALLS per run


1. __learningPromptChaining.py__

- Contains a crucial workflow pattern - Prompt Chaining
- Divides the task into steps and executes it one by one
- Gates/Checks can be implemented in each step to enhance the movement of the workflow

![Prompt Chaining](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F7418719e3dab222dccb379b8879e1dc08ad34c78-2401x1000.png&w=3840&q=75)

- In our case the request has been divided into 4 main steps - _Event Details Extraction_, _Event Details_, _Confirmation Message of the Event_, _Final Processing of the Event_.
- A Gate Check has been implemented in the final processing where if one of the step goes wrong then the calendar request is stated as INVALID.   

2. __learningRouting.py__

- Contains an essential workflow pattern required to fulfil complex tasks when there are various types of categories - Routing
- Uses a router to direct requests to different compartments/handlers
- This allows smooth processing as different requests are directed to their own special handlers

![Routing](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F5c0c0e9fe4def0b584c04d37849941da55e5e71c-2401x1000.png&w=3840&q=75)

- In our case, there are 3 types of requests - _New Event Request_, _Modifying an Existing Event Request_, _Other_
- A router is assigned which routes the calendar requests to their respective handlers
    - The _New Event Handler_ generates a new calendar request whereas the _Modify Event Handler_ modifies an existing request as per user's need


3. __learningParallelization.py__

- An important workflow required for running multiple _LLM Calls_ and analyze different aspects of the same request - Parallelization
- Parallelization can work on both the principles of __Sectioning__ and __Voting__

    A. Sectioning
    - Breaks the request into sub-tasks and runs in a parallel

    B.Voting
    - Runs the same task multiple times to get diverse outputs.

- Then the data is sent to a _Aggregator_ which combines everything and gives a definte output

![Parallelization](https://www.anthropic.com/_next/image?url=https%3A%2F%2Fwww-cdn.anthropic.com%2Fimages%2F4zrzovbb%2Fwebsite%2F406bb032ca007fd1624f261af717d70e6ca86286-2401x1000.png&w=3840&q=75)

- In our case, we have minimized the tasks into just security checks and request validations
    - _Request Validator_ - Verifies if the request is valid
    - _Security Verifier_ - Verifies if the request does not contain any security conflicts
- _Aggregation_: 
    - The aggregator combines all the results
    - Applies the validator/verifier rules and decides whether the request is valid or not     

