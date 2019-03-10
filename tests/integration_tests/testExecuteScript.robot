# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript
Resource        resource.robot

*** Test Case ***
Script
        ${result}         Execute Script In Target        hello.sh
        Should Be Equal   ${result.status}                0
        Should Be Empty   ${result.stderr}
        Should Contain    ${result.stdout}                Hello

Script SCP
        ${result}         Execute Script In Target        hello.sh        scptarget
        Should Be Equal   ${result.status}                0
        Should Be Empty   ${result.stderr}
        Should Contain    ${result.stdout}                Hello

Bg Script
        Execute Background Script In Target     hello.sh        default     bg4
        Execute Background Script In Target     hello.sh        default     bg3
        Execute Background Script In Target     hello.sh        default     bg2
        Execute Background Script In Target     hello.sh        default     bg1
        ${result_fg}        Execute Script In Target        hello.sh
        ${result_bg1}       Wait Background Execution       bg1
        ${result_bg2}       Wait Background Execution       bg2
        ${result_bg3}       Wait Background Execution       bg3
        ${result_bg4}       Wait Background Execution       bg4
        Log                 ${result_fg}
        Log                 ${result_bg1}
        Log                 ${result_bg2}
        Log                 ${result_bg3}
        Log                 ${result_bg4}
        Should Contain      ${result_fg.stdout}             Hello
        Should Contain      ${result_bg1.stdout}            Hello
        Should Contain      ${result_bg2.stdout}            Hello
        Should Contain      ${result_bg3.stdout}            Hello
        Should Contain      ${result_bg4.stdout}            Hello
        Should Be Equal     ${result_fg.status}             0
        Should Be Equal     ${result_bg1.status}            0
        Should Be Equal     ${result_bg2.status}            0
        Should Be Equal     ${result_bg3.status}            0
        Should Be Equal     ${result_bg4.status}            0

Su Script 1
        [Setup]             Init Su Target 1
        ${result}           Execute Script In Target        hello.sh
        Should Be Equal     ${result.status}                0
        Should Contain      ${result.stdout}                Hello
        Should Be Empty     ${result.stderr}

Su Script 2
        [Setup]             Init Su Target 2
        ${result}           Execute Script In Target        hello.sh
        Should Be Equal     ${result.status}                0
        Should Contain      ${result.stdout}                Hello
        Should Be Empty     ${result.stderr}
