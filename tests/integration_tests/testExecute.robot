# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript
Resource        resource.robot

*** Test Case ***
Execute
        [Documentation]                 Echo Hello World in primary target
        Execute Command In Target       "echo ""Hello World"""

Execute 2
        [Documentation]                 Execute uname -a in target
        Execute Command In Target       uname -a

Execute 3
        [Documentation]                 Execute echo foo1 in target
        ${result}                       Execute Command In Target       echo -n foo1
        Log                             ${result}
        Should Be Equal                 ${result.status}                0
        Should Be Equal                 ${result.stdout}                foo1

Execute 4
        [Documentation]                 Execute command with no output in target
        Execute Command In Target       true

Get Result
        [Documentation]                 Test non-zero exit code
        ${result}                       Execute Command In Target       false
        Log                             ${result}
        Should Not Be Equal             ${result.status}                0

Get Result 2
        [Documentation]                 Test longer execution
        ${result}                       Execute Command In Target       sh -c 'for I in {1..5}; do sleep 1; echo $I; echo e >&2; done'
        Log                             ${result}
        Should Be Equal                 ${result.status}                0
        Should Contain                  ${result.stdout}                4

Get Result 3
        [Documentation]                 Test multi-digit exit code
        ${result}                       Execute Command In Target       sh -c '$(exit 100)'
        Log                             ${result}
        Should Be Equal                 ${result.status}                100

Exception
        [Documentation]                 exception is thrown when nonzero exit status error is True and exit status is nonzero
        Set Default Target Property     nonzero status is error         True
        Run Keyword And Expect Error    NonZeroExitStatusError:*        Execute Command In Target       $(exit 100)

Exception 1
        [Documentation]                 exception is not thrown when nonzero exit status error is False and exit status is nonzero
        Set Default Target Property     nonzero status is error         False
        Run Keyword                     Execute Command In Target       $(exit 100)

Exception 2
        [Documentation]                 exception is not thrown when nonzero exit status error is True and exit status is zero
        Set Default Target Property     nonzero status is error         True
        Run Keyword                     Execute Command In Target       $(exit 0)

Exception 3
        [Documentation]                 exception is not thrown when nonzero exit status error is False and exit status is zero
        Set Default Target Property     nonzero status is error         False
        Run Keyword                     Execute Command In Target       $(exit 0)

Su Cmd 1
        [Setup]                         Init Su Target 1
        ${result}                       Execute Command In Target       sleep 2
        Should Be Equal                 ${result.status}                0
        Should Be Empty                 ${result.stdout}
        Should Be Empty                 ${result.stderr}
        ${result}                       Execute Command In Target       "echo ""Hello World!""; ping"
        Should Be Equal                 ${result.status}                2
        Should Contain                  ${result.stdout}                Hello
        Should Contain                  ${result.stdout}                ping
        Should Be Empty                 ${result.stderr}

Su Cmd 2
        [Setup]                         Init Su Target 2
        ${result}                       Execute Command In Target       sleep 2
        Should Be Equal                 ${result.status}                0
        Should Be Empty                 ${result.stdout}
        Should Be Empty                 ${result.stderr}
        ${result}                       Execute Command In Target       "echo ""Hello World!""; ping"
        Should Be Equal                 ${result.status}                2
        Should Contain                  ${result.stdout}                Hello
        Should Contain                  ${result.stdout}                ping
        Should Be Empty                 ${result.stderr}

Big Output
        ${result}                       Execute Command In Target       cat /bin/bash
        Should Be Equal                 ${result.status}                0
        ${result}                       Execute Command In Target       cat /bin/bash >&2
        Should Be Equal                 ${result.status}                0
        ${result}                       Execute Command In Target       (cat /bin/bash >&2 &); cat /bin/bash
        Should Be Equal                 ${result.status}                0
        ${result}                       Execute Command In Target       cat /bin/bash >&2; cat /bin/bash
        Should Be Equal As Strings      ${result.stdout}                ${result.stderr}        stderr and stdout differs       ${false}
        Should Be Equal                 ${result.status}                0

