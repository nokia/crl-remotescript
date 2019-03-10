# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript.FP
Resource        resource.robot

*** Test Case ***
Execute Bg
        [Documentation]                         Echo Hello World in primary target
        Execute Background Command In Node      CLA-0   "echo ""Hello World"""
        Wait Background Execution

Bg Result
        [Documentation]                         Execute uname -a in target
        Execute Background Command In Node      CLA-1   uname -a
        ${result}                               Wait Background Execution
        Log                                     ${result}
        Should Contain  ${result.stdout}        CLA-1

Bg And Fg
        Execute Background Command In Node      CLA-1                           uname -a
        ${result_fg}                            Execute Command In Node CLA-1   uname -a
        ${result_bg}                            Wait Background Execution
        Log                                     ${result_fg}
        Log                                     ${result_fg}
        Should Contain  ${result_fg.stdout}     CLA-1
        Should Contain  ${result_bg.stdout}     CLA-1

Script
        ${result}                               Execute Script In Node  CLA-1   hello.sh
        Log                                     ${result}
        Should Be Equal ${result.status}        0
        Should Contain  ${result.stdout}        CLA-1

Bg Script
        Execute Background Script In Node       CLA-1   hello.sh
        ${result}                               Wait Background Execution
        Log                                     ${result}
        Should Be Equal ${result.status}        0
        Should Contain  ${result.stdout}        CLA-1

Bg And Kill
        Set Target Property                     default     connection break is error           False
        Execute Background Command In Node      CLA-1       sleep 911
        Kill Background Execution
        ${result}                               Wait Background Execution       background      5
        Log                                     ${result}
        Execute Background Command In Node      CLA-1       sleep 911
        Sleep                                   3
        Kill Background Execution
        ${result}                               Wait Background Execution       background      5
        Set Target Property                     default     connection break is error           True
        Log                                     ${result}
        ${result}                               Execute Command In Node         CLA-1   "ps wwaux | grep -v grep | grep -E ""sleep 911$"""
        Log                                     ${result}
        Should Be Equal                         ${result.status}        1
        Should Be Empty                         ${result.stdout}
        Should Be Empty                         ${result.stderr}

