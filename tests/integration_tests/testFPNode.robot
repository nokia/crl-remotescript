# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         OperatingSystem
Library         RemoteScript.FP
Resource        resource.robot

*** Variable ***
${SU_NODE}      CLA-1

*** Test Case ***
Execute
        [Documentation]             Echo Hello World in primary target
        ${result}                   Execute Command In Node     CLA-0       echo "Hello World"
        Should Contain              ${result.stdout}        Hello World


Execute 2
        [Documentation]             Execute uname -a in target
        ${result}                   Execute Command In Node CLA-1   uname -a
        Log                         ${result}
        Should Contain              ${result.stdout}        CLA-1

Execute 3
        [Documentation]             Check no ssh errors from node
        ${result}                   Execute Command In Node     AS-0      uname -a
        Log                         ${result}
        Should Be Empty             ${result.stderr}
        Should Be Equal             ${result.status}        0

Node Script
        [Documentation]             Check no ssh/scp errors from node script
        ${result}                   Execute Script In Node      AS-0      hello.sh
        Log                         ${result}
        Should Be Empty             ${result.stderr}
        Should Be Equal             ${result.status}        0
        Should Contain              ${result.stdout}        Hello

Node Script SCP
        [Documentation]             Check no ssh/scp errors from node script
        ${result}                   Execute Script In Node      AS-0      hello.sh        scptarget
        Log                         ${result}
        Should Be Empty             ${result.stderr}
        Should Be Equal             ${result.status}        0
        Should Contain              ${result.stdout}        Hello

Get Result
        [Documentation]             Test non-zero exit code
        ${result}                   Execute Command In Node    CLA-0   false
        Log                         ${result}
        Should Not Be Equal         ${result.status}        0

Get Result 2
        [Documentation]             Test longer execution
        ${result}                   Execute Command In Node    CLA-1   for I in {1..5}; do sleep 1; echo $I; echo e >&2; done
        Log                         ${result}
        Should Be Equal             ${result.status}        0
        Should Contain              ${result.stdout}        5

Get Result 3
        [Documentation]             Test multi-digit exit code
        ${result}                   Execute Command In Node    CLA-0       exit 100
        Log                         ${result}
        Should Be Equal             ${result.status}        100

Single Quotes
        Run Keyword And Expect Error    *single quotes* Execute Command In Node CLA-0   echo 'Hello World'

Su Node Cmd 1
        [Setup]             Init Su Target 1
        ${result}           Execute Command In Node     ${SU_NODE}      sleep 2
        Should Be Equal     ${result.status}            0
        Should Be Empty     ${result.stdout}
        Should Be Empty     ${result.stderr}
        ${result}           Execute Command In Node     ${SU_NODE}      "echo ""Hello World!""; ping"
        Should Be Equal     ${result.status}            2
        Should Contain      ${result.stdout}            Hello
        Should Contain      ${result.stdout}            ping
        Should Be Empty     ${result.stderr}

Su Node Cmd 2
        [Setup]             Init Su Target 2
        ${result}           Execute Command In Node     ${SU_NODE}      sleep 2
        Should Be Equal     ${result.status}            0
        Should Be Empty     ${result.stdout}
        Should Be Empty     ${result.stderr}
        ${result}           Execute Command In Node     ${SU_NODE}      "echo ""Hello World!""; ping"
        Should Be Equal     ${result.status}            2
        Should Contain      ${result.stdout}            Hello
        Should Contain      ${result.stdout}            ping
        Should Be Empty     ${result.stderr}

Su Node Script 1
        [Setup]             Init Su Target 1
        ${result}           Execute Script In Node      ${SU_NODE}      hello.sh
        Should Be Equal     ${result.status}            0
        Should Contain      ${result.stdout}            Hello
        Should Be Empty     ${result.stderr}

Su Node Script 2            [Setup] Init Su Target 2
        ${result}           Execute Script In Node      ${SU_NODE}      hello.sh
        Should Be Equal     ${result.status}            0
        Should Contain      ${result.stdout}            Hello
        Should Be Empty     ${result.stderr}

